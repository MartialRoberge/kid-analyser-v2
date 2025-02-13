import re
import torch
from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from PIL import Image
import os
from qwen_vl_utils import process_vision_info

def load_model():
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Utilisation du device: {device}")
    
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        "Qwen/Qwen2-VL-2B-Instruct",
        torch_dtype="auto",
        device_map=device
    ).eval()
    
    processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-2B-Instruct")
    return model, processor, device

def get_image_description(image_path, model, processor, device):
    try:
        # Utiliser le chemin complet fourni
        if not os.path.exists(image_path):
            return f"[Erreur: Image non trouvée: {image_path}]"
            
        image = Image.open(image_path)
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": image,
                    },
                    {"type": "text", "text": """Analyse cette image et suis ces instructions précises :

1. Vérifie d'abord si l'image contient une échelle de risque numérotée de 1 à 7 avec un chiffre mis en évidence.
   Une échelle de risque valide doit avoir :
   - Une série de 7 cases ou niveaux numérotés de 1 à 7
   - Un chiffre clairement mis en évidence (par exemple en couleur différente ou surligné)
   - Des mentions "Risque le plus faible" et "Risque le plus élevé" aux extrémités

2. Si tu identifies une telle échelle de risque :
   - Réponds UNIQUEMENT avec la phrase exacte : "le niveau de risque de ce document est : X" 
   où X est le chiffre mis en évidence dans l'échelle

3. Si l'image ne contient PAS une échelle de risque valide selon les critères ci-dessus :
   - Réponds UNIQUEMENT : "cette image ne semble pas indiquer de risque"

Ne fais AUCUN autre commentaire ou description. Ta réponse doit être UNIQUEMENT l'une des deux phrases mentionnées ci-dessus."""},
                ],
            }
        ]

        text = processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = processor(
            text=[text],
            images=image_inputs,
            padding=True,
            return_tensors="pt",
        )
        
        inputs = inputs.to(device)
        
        generated_ids = model.generate(**inputs, max_new_tokens=128)
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        
        response = processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0]
        
        return f"[Description d'image: {response}]"
    except Exception as e:
        return f"[Erreur lors de l'analyse de l'image: {str(e)}]"

def process_markdown(input_file, output_file):
    print("Chargement du modèle...")
    model, processor, device = load_model()
    
    print("Lecture du fichier markdown...")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    def replace_image(match):
        image_path = match.group(2)
        # Construire le chemin vers le dossier images à la racine
        image_path = os.path.join(os.path.dirname(input_file), "images", os.path.basename(image_path))
        print(f"Analyse de l'image: {image_path}")
        return get_image_description(image_path, model, processor, device)
    
    print("Traitement des images...")
    content_with_descriptions = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, content)
    
    print("Écriture du fichier de sortie...")
    # Écriture du fichier markdown uniquement
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content_with_descriptions)
    
    print("Traitement terminé!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python process_markdown_fixed.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    process_markdown(input_file, output_file)

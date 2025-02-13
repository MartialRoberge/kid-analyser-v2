import logging
import json
import llama_cpp
import os
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config():
    """Charge la configuration depuis config.json."""
    try:
        config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "config.json")
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la configuration : {str(e)}")
        raise

def read_input_file(file_path):
    """Lit le contenu du fichier d'entrée."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier : {str(e)}")
        raise

def main():
    try:
        # Charger la configuration
        config = load_config()
        model_path = config["model"]["path"]
        
        # Initialiser le modèle
        llm = llama_cpp.Llama(
            model_path=model_path,
            n_ctx=8192,
            n_batch=512,
            n_threads=4,
            n_gpu_layers=1
        )

        # Lire le fichier d'entrée
        project_root = str(Path(__file__).parent.parent.parent)
        input_file = os.path.join(project_root, "LLM", "inputs", "input.txt")
        content = read_input_file(input_file)

        # Construire le prompt
        prompt = f"""[INST] Tu es un expert financier. Fais un résumé clair et bien structuré de ce document financier.
Mets en avant les informations essentielles comme :
- Le nom et type du produit
- Le niveau de risque et les avertissements importants
- Les dates clés
- Les scénarios de performance
- Les coûts

Utilise une présentation claire avec des titres et des puces pour faciliter la lecture.

Document :

{content}

[/INST]"""

        # Génération de la réponse
        response = llm(
            prompt,
            max_tokens=2048,
            temperature=0.1,
            stop=None,
            echo=False
        )

        # Traitement de la réponse
        response_text = response["choices"][0]["text"].strip()
        
        # Sauvegarder le résumé
        output_file = os.path.join(project_root, "LLM", "outputs", "resume.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response_text)
        
        logger.info(f"Résumé sauvegardé dans {output_file}")

    except Exception as e:
        logger.error(f"Erreur lors du traitement : {str(e)}")
        raise

if __name__ == "__main__":
    main()

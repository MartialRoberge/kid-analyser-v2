import logging
import json
import llama_cpp
import os
import ast
from typing import Dict, Any, List
from dataclasses import dataclass
from validation_advanced import validate_document
import sys

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set TOKENIZERS_PARALLELISM to false to avoid warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def load_config() -> Dict[str, Any]:
    """Charge la configuration depuis config.json."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'configs', 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la configuration: {str(e)}")
        raise

@dataclass
class LLMConfig:
    """Configuration pour le modèle LLM."""
    max_retries: int = 3
    temperature: float = 0.1
    max_tokens: int = 10000

def read_vlm_output(file_path: str) -> str:
    """Lit le contenu du fichier VLM."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            logger.info(f"Fichier {file_path} lu avec succès")
            return content
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier: {str(e)}")
        return ""

def save_json_output(data: Dict[str, Any], output_file: str) -> None:
    """Sauvegarde les données au format JSON après validation."""
    try:
        # Validation avancée
        validation_result = validate_document(data)
        
        # Affichage des résultats de validation
        logger.info(f"\nScore de qualité du document : {validation_result.score:.2%}")
        
        # Si le score est supérieur à 0, on considère que c'est valide
        if validation_result.score > 0:
            # Sauvegarde du JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info(f"Résultats sauvegardés dans {output_file}")
            
            # Affichage du feedback
            if validation_result.feedback:
                logger.info("\nFeedback de validation:")
                for fb in validation_result.feedback:
                    logger.info(f"- {fb}")
        else:
            logger.warning("Document invalide - score trop bas")
            
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du JSON: {str(e)}")

def load_json_schema(schema_file: str) -> Dict[str, Any]:
    """Charge le schéma JSON depuis un fichier."""
    try:
        with open(schema_file, 'r', encoding='utf-8') as file:
            schema = json.load(file)
            logger.info(f"Schéma JSON chargé depuis {schema_file}")
            return schema
    except Exception as e:
        logger.error(f"Erreur lors du chargement du schéma JSON: {str(e)}")
        return {}

def main():
    try:
        # Chargement de la configuration
        config = load_config()
        model_config = config["model"]
        
        # Initialisation du modèle LLM
        llm = llama_cpp.Llama(
            model_path=model_config["path"],
            #n_ctx=model_config["max_length"],
            n_ctx=8192,
            n_threads=8,  # Utiliser plus de threads CPU
            n_batch=1024,  # Augmenter la taille du batch comme dans votre exemple
            n_gpu_layers=-1,  # Charger tous les layers sur le GPU
            use_mmap=True,  # Utiliser le memory mapping pour un chargement plus rapide
            use_mlock=False,  # Désactiver le verrouillage mémoire
            verbose=True  # Activer les logs pour voir ce qui se passe
        )
        
        # Lecture du fichier d'entrée
        input_path = os.path.join(project_root, "inputs", "input.txt")
        vlm_output = read_vlm_output(input_path)
        if not vlm_output:
            logger.error("Impossible de lire le fichier d'entrée")
            return

        # Chargement du schéma JSON
        schema_path = os.path.join(project_root, "configs", "json_schema.json")
        json_structure = load_json_schema(schema_path)
        if not json_structure:
            logger.error("Impossible de charger le schéma JSON")
            return
        
        # Préparation du prompt
        prompt = f""" Tu es un assistant spécialisé dans l'extraction d'informations structurées à partir de texte. Ta tâche est de remplir le JSON Schema suivant avec les informations contenues dans le document fourni.


Voici le JSON Schema :

        {json.dumps(json_structure, indent=2)}

Voici le document :

{vlm_output}

Instructions importantes :

Lis attentivement les informations destructurés du document et ajoute les au format JSON en respectant le formt du schéma.

Si une information n'est pas présente dans le document, laisse le champ correspondant vide ("") ou avec la valeur par défaut si elle est spécifiée dans le schéma (par exemple, false ou []).

Respecte scrupuleusement le format du JSON Schema (guillemets, virgules, accolades, crochets, etc.).

Pour les dates, utilise le format JJ/MM/AAAA.

Pour les nombres, utilise le format numérique approprié (par exemple, 2 et non "deux").


Pour le champ "performanceScenarios" (fais très attention a cette partie, il ne faut surtout pas confondre les chiffres), il y'a tout d'abord un "montant investit".

Pour chaque scénario, ne répète pas l'enum mais choisi pour chaque scénario le bon nom du scénario.

Chaque Scénario :

- Doit avoir un seul titre (Tensions ou Défavorable ou Intermédiaire ou Favorable).
- Doit avoir une ou plusieurs durées de possession (un nombre (ex : 1an, 2ans, 5ans)).
- Doit avoir un montant final, qui est le résultat du montant investit sur chaque periode. 
- Doit avoir une performance en pourcentage.

Sois précis et concis dans tes réponses.

Ne fait pas de phrase, l'objectif est juste de remplir les champs du json schema.

Ta réponse doit être uniquement le JSON Schema complété, sans texte additionnel.

"""
        
        # Génération de la réponse
        response = llm(
            prompt,
            max_tokens=10000,  # limite max
            temperature=model_config["temperature"],
            stop=None,  # Enlever les stop tokens pour éviter la coupure prématurée
            echo=False
        )
        
        # Log de la réponse brute
        response_text = response["choices"][0]["text"]
        logger.info("=== Réponse brute du LLM ===")
        logger.info(response_text)
        logger.info("=== Fin de la réponse brute ===")

        try:
            # Nettoyer la réponse
            response_text = response["choices"][0]["text"].strip()
            
            # Compter les accolades ouvrantes et fermantes
            open_braces = response_text.count('{')
            close_braces = response_text.count('}')
            
            # Équilibrer les accolades si nécessaire
            if open_braces > close_braces:
                response_text += '}' * (open_braces - close_braces)
            elif not response_text.endswith('}'):
                # Ajouter une accolade fermante seulement si on n'en a pas déjà ajouté
                response_text += '}'
            
            # Trouver le JSON dans la réponse
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                response_text = response_text[start_idx:end_idx]
                
                try:
                    # Essayer d'abord avec json.loads pour un parsing strict
                    parsed_data = json.loads(response_text)
                except json.JSONDecodeError:
                    try:
                        # Si json.loads échoue, utiliser ast.literal_eval
                        parsed_data = ast.literal_eval(response_text)
                    except (SyntaxError, ValueError) as e:
                        logger.error(f"Erreur de parsing JSON : {str(e)}")
                        logger.error(f"Texte invalide : {response_text}")
                        # Sauvegarder la réponse brute pour debug
                        debug_file = os.path.join(project_root, "outputs", "debug_response.txt")
                        with open(debug_file, 'w', encoding='utf-8') as f:
                            f.write(response_text)
                        logger.info(f"Réponse brute sauvegardée dans {debug_file}")
                        return
                
                # Valider le document
                validation_result = validate_document(parsed_data)
                
                if validation_result.score >= 0.0:  # Ajuster le seuil si nécessaire
                    # Sauvegarder le résultat
                    output_file = os.path.join(project_root, "outputs", "kid.json")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(parsed_data, f, indent=2, ensure_ascii=False)
                    logger.info(f"Résultat sauvegardé dans {output_file}")
                else:
                    logger.error(f"Validation échouée. Score: {validation_result.score}")
                    for feedback in validation_result.feedback:
                        logger.error(f"Feedback: {feedback}")
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement : {str(e)}")
            logger.error(f"Réponse reçue : {response_text}")
            
    except Exception as e:
        logger.error(f"Erreur lors du traitement : {str(e)}")
        raise

if __name__ == "__main__":
    main()

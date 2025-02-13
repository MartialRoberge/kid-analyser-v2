# Pipeline d'Analyse de Documents PDF avec LLM

Ce projet implémente une pipeline complète d'analyse de documents PDF qui combine l'extraction de texte, l'analyse de mise en page, et l'utilisation de modèles de langage (LLM) pour une compréhension approfondie des documents.

## 🌟 Caractéristiques

- Extraction intelligente de texte et de mise en page à partir de PDFs
- Support OCR pour les documents numérisés
- Génération de markdown structuré
- Analyse sémantique via LLM
- Génération de résumés automatiques
- Export au format XML des informations clés
- Pipeline automatisée complète

## 🏗️ Architecture de la Pipeline

La pipeline se compose de plusieurs étapes séquentielles :

1. **Analyse PDF (main.py)**
   - Extraction du texte et de la mise en page
   - Génération d'images pour les éléments visuels
   - Création de fichiers intermédiaires (JSON, Markdown)

2. **Traitement Markdown (process_markdown_fixed.py)**
   - Nettoyage et structuration du contenu
   - Formatage du texte pour l'analyse LLM

3. **Analyse LLM (llm_test_options.py)**
   - Traitement du contenu par le modèle de langage
   - Extraction des informations pertinentes
   - Génération d'insights

4. **Génération de Résumé (resume.py)**
   - Création de résumés automatiques
   - Synthèse des points clés

5. **Export XML (key_info_xml.py)**
   - Structuration des informations en XML
   - Export des données analysées

## 🚀 Installation

1. Cloner le repository :
```bash
git clone https://github.com/votre-username/nom-du-repo.git
cd nom-du-repo
```

2. Créer et activer l'environnement virtuel :
```bash
python -m venv .venv
source .venv/bin/activate  # Sur Unix/macOS
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configuration de l'environnement Conda pour MinerU (requis pour certaines étapes) :
```bash
conda env create -f environment.yml
```

## 💻 Utilisation

1. Placer le PDF à analyser dans le répertoire du projet

2. Exécuter la pipeline complète :
```bash
./run_pipeline.sh
```

Ou exécuter les étapes individuellement :

```bash
python main.py
python process_markdown_fixed.py
python LLM/src/llm_test_options.py
python LLM/src/resume.py
python LLM/src/key_info_xml.py
```

## 📂 Structure du Projet

```
.
├── main.py                 # Script principal d'analyse PDF
├── process_markdown_fixed.py # Traitement du markdown
├── run_pipeline.sh         # Script d'automatisation
├── requirements.txt        # Dépendances Python
├── LLM/
│   ├── src/               # Scripts d'analyse LLM
│   ├── configs/           # Fichiers de configuration
│   └── outputs/           # Résultats d'analyse
├── images/                # Images extraites
└── logs/                  # Fichiers de logs
```

## ⚙️ Configuration

Le projet utilise plusieurs fichiers de configuration dans le dossier `LLM/configs/` :
- `config.json` : Configuration générale
- `json_schema.json` : Schéma de validation des données

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Notes

- Le modèle LLM utilisé fait environ 7GB et nécessite Git LFS
- Certaines étapes nécessitent l'environnement Conda MinerU
- Les fichiers PDF traités sont sauvegardés avec leurs analyses respectives

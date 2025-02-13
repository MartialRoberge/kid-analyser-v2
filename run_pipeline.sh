#!/bin/bash

echo "🚀 Démarrage de la pipeline..."

# Obtenir le chemin absolu du répertoire du projet
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Chemins des scripts et fichiers (relatifs au projet)
MAIN_SCRIPT="$PROJECT_ROOT/main.py"
PROCESS_SCRIPT="$PROJECT_ROOT/process_markdown_fixed.py"
LLM_SCRIPT="$PROJECT_ROOT/LLM/src/llm_test_options.py"
LLM_INPUT_DIR="$PROJECT_ROOT/LLM/inputs"
UPLOADS_DIR="$PROJECT_ROOT/uploads"
MINERU_PYTHON="$PROJECT_ROOT/MinerU/bin/python3.10"
VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"

# Get the directory and base name of the input PDF file
PDF_DIR=$(dirname "$1")
PDF_BASENAME=$(basename "$1" .pdf)
MD_FILE="${PDF_DIR}/${PDF_BASENAME}.md"

echo "💾 Étape 1: Exécution de main.py avec l'environnement MinerU..."
"$MINERU_PYTHON" "$MAIN_SCRIPT" "$1"

if [ $? -eq 0 ]; then
    echo "✅ main.py exécuté avec succès"
    
    echo "🔄 Étape 2: Exécution de process_markdown_fixed.py avec l'environnement .venv..."
    "$VENV_PYTHON" "$PROCESS_SCRIPT" "$MD_FILE" "$MD_FILE"
    
    if [ $? -eq 0 ]; then
        echo "✅ process_markdown_fixed.py exécuté avec succès"
        
        echo "📝 Copie du contenu markdown vers input.txt..."
        cp "$MD_FILE" "$LLM_INPUT_DIR/input.txt"
        
        echo "🤖 Étape 3: Exécution de llm_test_options.py avec l'environnement .venv..."
        "$VENV_PYTHON" "$LLM_SCRIPT"
        
        if [ $? -eq 0 ]; then
            echo "✅ llm_test_options.py exécuté avec succès"
            
            echo "🗑️ Nettoyage des fichiers temporaires..."
            rm -rf "$UPLOADS_DIR"/*
            rm -f "$LLM_INPUT_DIR/input.txt"
            
            echo "🎉 Pipeline terminée avec succès!"
            exit 0
        else
            echo "❌ Erreur lors de l'exécution de llm_test_options.py"
            exit 1
        fi
    else
        echo "❌ Erreur lors de l'exécution de process_markdown_fixed.py"
        exit 1
    fi
else
    echo "❌ Erreur lors de l'exécution de main.py"
    exit 1
fi

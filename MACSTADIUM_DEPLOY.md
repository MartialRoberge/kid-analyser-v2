# Guide Ultra-Simple MacStadium

## 1. Créer un Compte
1. Allez sur [MacStadium.com](https://www.macstadium.com)
2. Choisissez "Mac mini Subscriptions"
3. Sélectionnez un Mac mini M2/M3
4. Créez votre compte et commandez

## 2. Accéder à Votre Mac
1. MacStadium vous enverra par email :
   - L'adresse IP de votre Mac
   - Les identifiants de connexion
   - La clé VPN pour l'accès sécurisé

2. Connectez-vous en SSH :
```bash
ssh admin@votre-ip-macstadium
```

## 3. Copier Votre Projet
```bash
# Sur votre Mac local
cd /Users/martialroberge/Desktop/Ing4/Python/
tar -czf kid-analyser.tar.gz test_de_tournabilite/

# Copier vers MacStadium
scp kid-analyser.tar.gz admin@votre-ip-macstadium:~

# Sur le Mac MacStadium
tar -xzf kid-analyser.tar.gz
```

## 4. Lancer l'Application
```bash
# Installer Homebrew si pas déjà fait
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Installer PM2
brew install node
npm install -g pm2

# Lancer l'application
cd test_de_tournabilite
pm2 start app.py --name "kid-analyser" --interpreter .venv/bin/python
pm2 save
```

## 5. Configurer le Port
```bash
# Installer nginx
brew install nginx

# Configurer nginx
cat > /usr/local/etc/nginx/servers/kid-analyser.conf << EOL
server {
    listen 80;
    server_name votre-ip-macstadium;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host \$host;
        
        # CORS
        add_header 'Access-Control-Allow-Origin' '*';
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
        add_header 'Access-Control-Allow-Headers' '*';
    }
}
EOL

# Démarrer nginx
brew services start nginx
```

## 6. C'est Prêt !
Vos endpoints sont disponibles :
- http://votre-ip-macstadium/analyze
- http://votre-ip-macstadium/kid-json

## Commandes Utiles
```bash
# Voir les logs
pm2 logs kid-analyser

# Redémarrer l'app
pm2 restart kid-analyser

# Arrêter l'app
pm2 stop kid-analyser
```

## Avantages de Cette Solution
1. ✅ Pas besoin de recréer les environnements
2. ✅ Même architecture que votre Mac (Apple Silicon)
3. ✅ Configuration minimale
4. ✅ Support technique disponible
5. ✅ Uptime garanti

## Notes
- Prix : ~$99/mois
- Support 24/7 inclus
- Backups automatiques disponibles
- Possibilité d'ajouter un nom de domaine personnalisé

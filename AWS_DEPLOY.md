# Guide Simple de Déploiement sur AWS EC2 Mac

## 1. Créer une Instance EC2 Mac

1. Connectez-vous à la [Console AWS](https://console.aws.amazon.com)
2. Allez dans EC2 > Instances > Launch Instance
3. Configurez l'instance :
   - Name: `kid-analyser`
   - AMI: `mac1.metal` (choisir macOS Monterey ou plus récent)
   - Instance type: `mac1.metal`
   - Key pair: Créez une nouvelle paire de clés
   - Network: Laissez les paramètres par défaut
   - Security Group: 
     - Autorisez SSH (22)
     - Autorisez HTTP (80)
     - Autorisez HTTPS (443)
     - Autorisez le port 5001

## 2. Se Connecter à l'Instance

```bash
# Téléchargez votre clé .pem depuis AWS
chmod 400 votre-cle.pem

# Connectez-vous à l'instance
ssh -i votre-cle.pem ec2-user@votre-ip-aws
```

## 3. Copier le Projet

```bash
# Sur votre machine locale, créez une archive du projet
cd /Users/martialroberge/Desktop/Ing4/Python/
tar -czf kid-analyser.tar.gz test_de_tournabilite/

# Copiez l'archive vers AWS
scp -i votre-cle.pem kid-analyser.tar.gz ec2-user@votre-ip-aws:~

# Sur l'instance AWS, extrayez l'archive
tar -xzf kid-analyser.tar.gz
```

## 4. Installer PM2 pour Gérer le Processus

```bash
# Installer Node.js et PM2
brew install node
npm install -g pm2

# Créer le fichier de configuration PM2
cat > ecosystem.config.js << EOL
module.exports = {
  apps : [{
    name: 'kid-analyser',
    script: 'app.py',
    interpreter: '.venv/bin/python',
    cwd: '/Users/ec2-user/test_de_tournabilite',
    env: {
      PORT: 5001
    }
  }]
}
EOL

# Démarrer l'application
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## 5. Configurer Nginx

```bash
# Installer nginx
brew install nginx

# Configurer nginx
cat > /usr/local/etc/nginx/servers/kid-analyser.conf << EOL
server {
    listen 80;
    server_name votre-ip-aws;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        
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

## 6. Tester l'API

```bash
# Test local sur l'instance
curl -X POST -F "file=@test.pdf" http://localhost:5001/analyze

# Test depuis n'importe où
curl -X POST -F "file=@test.pdf" http://votre-ip-aws/analyze
```

## 7. Commandes Utiles

```bash
# Voir les logs de l'application
pm2 logs kid-analyser

# Redémarrer l'application
pm2 restart kid-analyser

# Voir le status
pm2 status

# Arrêter l'application
pm2 stop kid-analyser
```

## Notes Importantes

1. **Coûts** : Les instances mac1.metal sont facturées à l'heure (~$0.65/heure), avec une durée minimale de 24 heures.

2. **Sécurité** :
   - Limitez les IPs qui peuvent accéder à votre instance dans le Security Group
   - Utilisez HTTPS en production
   - Gardez votre clé .pem en sécurité

3. **Backups** :
   - AWS peut faire des snapshots automatiques de votre instance
   - Configurez des sauvegardes régulières via la console AWS

4. **Monitoring** :
   - Utilisez AWS CloudWatch pour surveiller votre instance
   - PM2 fournit des métriques basiques de surveillance

## Endpoints

Vos endpoints seront accessibles à :
- http://votre-ip-aws/analyze
- http://votre-ip-aws/kid-json

Pour une utilisation en production, vous devriez :
1. Configurer un nom de domaine
2. Ajouter un certificat SSL
3. Mettre en place un CDN (comme CloudFront)

Besoin d'aide pour l'une de ces étapes supplémentaires ?

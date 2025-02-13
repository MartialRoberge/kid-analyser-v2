# Guide de Déploiement sur OVH M3

Ce guide détaille les étapes pour déployer l'analyseur de KIDs sur un serveur OVH M3.

## 1. Préparer le Projet

### 1.1 Structure du Projet
```
kid-analyser-backend/
├── MinerU/               # Environnement pour l'extraction PDF
├── .venv/               # Environnement pour le LLM
├── LLM/
│   ├── configs/
│   ├── inputs/
│   ├── outputs/
│   └── src/
├── uploads/             # Dossier pour les fichiers temporaires
├── app.py              # Serveur Flask
└── run_pipeline.sh     # Script d'exécution
```

### 1.2 Archiver le Projet
```bash
# Sur votre machine locale
tar -czf kid-analyser.tar.gz kid-analyser-backend/
```

## 2. Configuration du Serveur OVH

### 2.1 Connexion SSH
```bash
ssh debian@votre-ip
```

### 2.2 Installation des Dépendances Système
```bash
# Mettre à jour le système
sudo apt update
sudo apt upgrade -y

# Installer les dépendances nécessaires
sudo apt install -y python3.10 python3.10-venv python3-pip nginx supervisor
```

### 2.3 Configuration du Pare-feu
```bash
# Autoriser les ports nécessaires
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 5001
sudo ufw enable
```

## 3. Déploiement du Projet

### 3.1 Copier et Extraire le Projet
```bash
# Créer le dossier d'application
sudo mkdir -p /opt/kid-analyser
sudo chown -R debian:debian /opt/kid-analyser

# Copier l'archive (depuis votre machine locale)
scp kid-analyser.tar.gz debian@votre-ip:/opt/kid-analyser/

# Sur le serveur
cd /opt/kid-analyser
tar -xzf kid-analyser.tar.gz
```

### 3.2 Configuration des Permissions
```bash
# Configurer les permissions des dossiers
chmod 755 /opt/kid-analyser
chmod -R 755 /opt/kid-analyser/MinerU
chmod -R 755 /opt/kid-analyser/.venv
chmod -R 777 /opt/kid-analyser/uploads
chmod -R 777 /opt/kid-analyser/LLM/outputs
```

## 4. Configuration de Supervisor

### 4.1 Créer la Configuration
```bash
sudo nano /etc/supervisor/conf.d/kid-analyser.conf
```

Contenu :
```ini
[program:kid-analyser]
directory=/opt/kid-analyser
command=/opt/kid-analyser/.venv/bin/python app.py
user=debian
autostart=true
autorestart=true
stderr_logfile=/var/log/kid-analyser/err.log
stdout_logfile=/var/log/kid-analyser/out.log
environment=PATH="/opt/kid-analyser/MinerU/bin:/opt/kid-analyser/.venv/bin:%(ENV_PATH)s"
```

### 4.2 Créer les Dossiers de Logs
```bash
sudo mkdir -p /var/log/kid-analyser
sudo chown -R debian:debian /var/log/kid-analyser
```

### 4.3 Démarrer le Service
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start kid-analyser
```

## 5. Configuration de Nginx

### 5.1 Créer la Configuration
```bash
sudo nano /etc/nginx/sites-available/kid-analyser
```

Contenu :
```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Configuration CORS
        add_header 'Access-Control-Allow-Origin' '*';
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range';
    }

    # Augmenter la taille maximale des uploads si nécessaire
    client_max_body_size 10M;
}
```

### 5.2 Activer le Site
```bash
sudo ln -s /etc/nginx/sites-available/kid-analyser /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 6. Vérification et Tests

### 6.1 Vérifier les Services
```bash
# Vérifier le status de supervisor
sudo supervisorctl status kid-analyser

# Vérifier les logs
tail -f /var/log/kid-analyser/out.log
tail -f /var/log/kid-analyser/err.log

# Vérifier nginx
sudo systemctl status nginx
```

### 6.2 Tester l'API
```bash
# Test simple
curl -X POST -F "file=@test.pdf" http://votre-domaine.com/analyze
```

## 7. Maintenance

### 7.1 Rotation des Logs
```bash
sudo nano /etc/logrotate.d/kid-analyser
```

Contenu :
```
/var/log/kid-analyser/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 debian debian
}
```

### 7.2 Surveillance des Ressources
```bash
# Installation de htop pour la surveillance
sudo apt install htop

# Surveillance de l'utilisation des ressources
htop
```

### 7.3 Sauvegarde
```bash
# Créer un script de backup
sudo nano /opt/kid-analyser/backup.sh
```

Contenu :
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/kid-analyser"
DATE=$(date +%Y%m%d)
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/kid-analyser-$DATE.tar.gz /opt/kid-analyser
find $BACKUP_DIR -type f -mtime +7 -delete
```

## 8. Dépannage

### 8.1 Problèmes Courants
- Si l'application ne démarre pas : `sudo supervisorctl restart kid-analyser`
- Si nginx ne répond pas : `sudo systemctl restart nginx`
- Si les uploads échouent : vérifier les permissions du dossier `uploads/`

### 8.2 Logs
- Logs application : `/var/log/kid-analyser/`
- Logs nginx : `/var/log/nginx/`
- Logs système : `journalctl -u supervisor`

## 9. Mise à Jour

### 9.1 Mettre à Jour le Code
```bash
# Arrêter l'application
sudo supervisorctl stop kid-analyser

# Sauvegarder l'ancienne version
cd /opt
tar -czf kid-analyser-backup.tar.gz kid-analyser/

# Déployer la nouvelle version
# ... (copier les nouveaux fichiers)

# Redémarrer l'application
sudo supervisorctl start kid-analyser
```

## Notes Importantes
1. Remplacer `votre-ip` et `votre-domaine.com` par vos valeurs réelles
2. Les environnements Python (`MinerU` et `.venv`) doivent être copiés tels quels
3. Vérifier régulièrement l'espace disque et la mémoire disponible
4. Configurer des sauvegardes régulières
5. Mettre en place une surveillance des processus critiques

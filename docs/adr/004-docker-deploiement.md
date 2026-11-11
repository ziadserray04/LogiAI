# ADR 004 — Déploiement de LogiAI avec Docker Compose

- **Statut :** Accepté
- **Contexte :** Atelier 5

## 1. Contexte

LogiAI comprend une API FastAPI qui charge un modèle de Machine Learning et une interface Web servie par Nginx.

L'objectif est de déployer les deux services dans des conteneurs indépendants et de pouvoir les démarrer avec une seule commande :

`docker compose up -d --build`

## 2. Décision : gestion du modèle

Le Dockerfile copie les fichiers du modèle dans l'image :

- `models/model.joblib`
- `models/model_info.json`

Docker Compose monte également le dossier local `models/` dans le conteneur API.

Cette approche permet :
- de disposer du modèle directement dans l'image ;
- de remplacer les fichiers du modèle sur la machine hôte sans reconstruire l'image ;
- de conserver une séparation entre le code de l'API et les artefacts du modèle.

Les fichiers du modèle doivent être versionnés dans Git pour permettre un déploiement reproductible.

Le dataset d'entraînement `data/livraisons.csv` n'est pas copié dans l'image, car l'API utilise le modèle déjà entraîné pour effectuer ses prédictions.

## 3. Décision : exposition des ports

Les ports retenus sont :

| Service | Port conteneur | Port hôte |
|---|---:|---:|
| API FastAPI | 8000 | 8001 |
| Interface Nginx | 80 | 8081 |

Le port 8080 étant déjà utilisé sur la machine par un autre service, le port 8081 a été choisi pour l'interface Web.

Le port 8001 permet également de tester directement l'API sans passer par Nginx.

## 4. Décision : architecture Nginx

Nginx sert les fichiers statiques de l'interface Web et transmet les requêtes commençant par `/api/` au service API.

Cela permet au navigateur d'utiliser une seule origine pour l'interface et les appels API.

## 5. Décision : supervision et démarrage

Le service API possède un healthcheck basé sur `/health`.

Le service Web dépend de l'état de santé de l'API avant son démarrage.

Les deux services utilisent la politique de redémarrage `unless-stopped`.

## 6. Alternatives et compromis

| Choix | Avantages | Inconvénients |
|---|---|---|
| Modèle copié dans l'image | Image autonome et reproductible | Reconstruction nécessaire pour mettre à jour le modèle |
| Modèle monté en volume | Mise à jour sans reconstruction | Dépend des fichiers présents sur l'hôte |
| Port Web 8081 | Évite le conflit avec le port 8080 | URL différente du port habituel |
| API exposée sur 8001 | Tests directs et accès local | Port supplémentaire exposé sur l'hôte |

## 7. Validation

Les tests réalisés confirment :

- démarrage des deux conteneurs avec Docker Compose ;
- état `healthy` de l'API ;
- réponse HTTP 200 de l'interface Web ;
- fonctionnement du proxy Nginx vers `/api/health` ;
- prédiction réussie depuis l'interface Web ;
- réponse HTTP 502 du proxy lorsque l'API est arrêtée ;
- maintien de l'interface Web en HTTP 200 pendant cette panne ;
- retour à l'état `healthy` après redémarrage de l'API.

Les mesures de ressources observées :

- API : environ 119,4 MiB de mémoire ;
- Web : environ 11,91 MiB de mémoire.

## 8. Conséquences

Le déploiement est simplifié : une seule commande permet de construire et démarrer les services.

Les clés API restent stockées dans `.env`, qui ne doit jamais être versionné. Le fichier `.env.example` fournit uniquement des valeurs fictives.

# Compte rendu — Atelier 5 : Déploiement Docker de LogiAI

**Nom :** Ziad Serray
**Groupe :** G3

## 1. Objectif

L'objectif est de conteneuriser l'application LogiAI avec Docker et Docker Compose.

L'application comprend :
- Une API FastAPI qui réalise les prédictions à partir d'un modèle ML.
- Une interface Web HTML/CSS/JavaScript.
- Un serveur Nginx qui sert l'interface et transmet les requêtes à l'API.

## 2. Architecture

Deux conteneurs sont utilisés :

| Service | Technologie | Port interne | Port local |
|---|---|---:|---:|
| API | FastAPI / Uvicorn | 8000 | 8001 |
| Web | Nginx | 80 | 8081 |

Nginx transmet les requêtes `/api/` au service API.

Le port 8081 est utilisé pour éviter un conflit avec un autre service occupant déjà le port 8080 sur la machine.

## 3. Fichiers Docker

Les principaux fichiers créés sont :

- `Dockerfile` : construction de l'image de l'API.
- `web/Dockerfile` : construction de l'image Nginx.
- `docker-compose.yml` : orchestration des deux services.
- `.dockerignore` : exclusion des fichiers inutiles du contexte Docker.
- `nginx/default.conf` : configuration du serveur Web et du proxy inverse.

Le Dockerfile de l'API utilise `python:3.11-slim`, installe les dépendances et copie le code ainsi que les fichiers du modèle.

Le dataset d'entraînement n'est pas copié dans l'image.

## 4. Démarrage de l'application

Commande utilisée :

`docker compose up -d --build`

La configuration a été vérifiée avec :

`docker compose config --quiet`

Les deux images ont été construites et les deux conteneurs ont démarré correctement.

Résultat de `docker compose ps` :
- `logiai-api` : Up, état `healthy`.
- `logiai-web` : Up.

## 5. Tests effectués

| Test | Résultat |
|---|---|
| Configuration Docker Compose | Validée |
| Construction de l'image API | Réussie |
| Construction de l'image Web | Réussie |
| Démarrage des deux conteneurs | Réussi |
| API `/health` sur le port 8001 | HTTP 200 |
| Interface Web sur le port 8081 | HTTP 200 |
| Proxy Nginx `/api/health` | HTTP 200 |
| Route de prédiction appelée en GET | HTTP 405 attendu, car la route accepte POST |
| Prédiction avec clé API valide | HTTP 200 |
| Affichage de la prédiction dans le navigateur | Réussi |

### Résultat d'une prédiction depuis l'interface

- Probabilité de retard : 9,72 %
- Alerte : Non
- Seuil : 0,4
- Version du modèle : 1.0

Une autre requête de test avec des paramètres différents a retourné une probabilité de 47,1 % et une alerte positive.

## 6. Test de panne de l'API

L'API a été arrêtée temporairement avec :

`docker compose stop api`

Résultats :
- La page Web a continué à répondre en HTTP 200.
- Le proxy `/api/health` a répondu en HTTP 502 Bad Gateway.

L'API a ensuite été redémarrée avec :

`docker compose start api`

Après redémarrage, `docker compose ps` a confirmé son état `healthy` et `/health` a retourné :

`{"status":"ok","model_loaded":true,"auth_configured":true}`

## 7. Consommation des ressources

Mesure effectuée avec `docker stats --no-stream logiai-api logiai-web`.

| Ressource | API | Web |
|---|---:|---:|
| CPU | 0,29 % | 0,00 % |
| Mémoire utilisée | 119,4 MiB | 11,91 MiB |
| Nombre de processus | 32 | 15 |

La consommation mémoire observée est faible pour les deux services.

## 8. Sécurité

Les clés API sont fournies par le fichier `.env`, qui est exclu du dépôt Git.

Le fichier `.env.example` contient uniquement des valeurs fictives permettant de préparer la configuration.

Les fichiers du modèle sont versionnés afin de permettre la reconstruction de l'application.

Le fichier `.dockerignore` exclut notamment `.env`, `.git`, les environnements virtuels et les fichiers temporaires Python.

## 9. Décisions techniques

Les décisions de déploiement sont documentées dans :

`docs/adr/004-docker-deploiement.md`

L'ADR 004 présente notamment :
- La copie et le montage des fichiers du modèle.
- Le choix des ports 8001 et 8081.
- Le rôle de Nginx.
- Le healthcheck et les politiques de redémarrage.
- Les avantages et inconvénients des alternatives retenues.

## 10. Conclusion

L'application LogiAI est maintenant déployée avec Docker Compose.

L'API FastAPI et l'interface Web Nginx fonctionnent dans deux conteneurs indépendants. La communication entre les services, l'authentification, les prédictions, la supervision et le comportement en cas de panne ont été vérifiés.

Le démarrage de l'ensemble est simplifié grâce à une seule commande Docker Compose.

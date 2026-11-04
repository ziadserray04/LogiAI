# Compte rendu : tester, sécuriser et appeler l'API LogiAI

**Noms :** Ziad Serray  
**Groupe :** G3

## 1. Casser son API (activité 1)

| Cas | Requête (corps ou URL) | Prévu | Obtenu |
|---|---|---:|---:|
| Champ manquant | `poids_kg` absent | 422 | 422 |
| Valeur absurde | `poids_kg = 99999` | 422 | 422 |
| Texte au lieu d'un nombre | `distance_km = "cent vingt"` | 422 | 422 |
| Champ en trop | Ajout du champ `ville` | 422 | 422 |
| Mauvaise route | `/v1/route-inconnue` | 404 | 404 |

- Une requête acceptée alors qu'elle devait être refusée ? Aucune parmi les cinq requêtes testées.

## 2. Les 2 bugs (activité 2)

| Bug | Test qui l'a révélé | Comportement avant | Correction |
|---|---|---|---|
| 1 | `heure_depart = 24` | Requête acceptée (HTTP 200) | Remplacement de `le=24` par `le=23` |
| 2 | `nb_arrets = -1` | Requête acceptée (HTTP 200) | Ajout de `ge=0` |

- Sortie de `python -m pytest` à la fin de l'activité 2 :

`50 passed, 1 warning in 3.17s`

## 3. La clé API (sprint 1)

- Ma fonction `verify_api_key()` :

```python
def verify_api_key(x_api_key: str | None = Header(default=None)) -> str:
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="Clé API manquante",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if _egal(x_api_key, config.ADMIN_KEY):
        return "admin"

    if _egal(x_api_key, config.API_KEY):
        return "user"

    raise HTTPException(
        status_code=401,
        detail="Clé API invalide",
        headers={"WWW-Authenticate": "ApiKey"},
    )
```

| Requête | Code obtenu |
|---|---:|
| `/v1/predict` sans clé | 401 |
| `/v1/predict` fausse clé | 401 |
| `/v1/predict` clé utilisateur | 200 |
| `/v1/model-info` clé utilisateur | 403 |
| `/v1/model-info` clé administrateur | 200 |
| `/health` sans clé | 200 |

- Preuve que `.env` n'est pas dans Git : le fichier `.env` est ignoré par Git et ne doit pas apparaître dans les fichiers suivis.

## 4. Le client web (sprint 2)

- Mon `fetch` : coller ici le code réel présent dans `web/index.html`.

- Ce qui s'affiche :
  - Livraison normale : l'API retourne une prédiction.
  - Pluie de 500 mm : la validation de l'API refuse la requête si cette valeur dépasse la limite autorisée (HTTP 422).
  - Fausse clé : l'API refuse la requête (HTTP 401).

- Expérience CORS (page servie sur le port 5501) : le navigateur bloque l'appel si l'origine `http://localhost:5501` n'est pas autorisée dans la configuration CORS de l'API.

`curl` fonctionne quand même car CORS est une restriction appliquée par les navigateurs, pas une interdiction générale des requêtes HTTP.

- Où voyez-vous la clé dans F12 ?

Dans l'onglet Network, en ouvrant la requête API puis Request Headers, dans l'en-tête `X-API-Key`.

## 5. Questions de compréhension

**1. Quelle différence entre 401, 403 et 422 ?**

- 401 : clé API absente ou invalide.
- 403 : utilisateur authentifié, mais non autorisé à accéder à la ressource.
- 422 : données envoyées non conformes aux règles de validation.

**2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ?**

Pour protéger les informations sensibles et empêcher leur exposition. Les clés sont stockées dans `.env`, un fichier ignoré par Git.

**3. Pourquoi comparer avec `compare_digest` plutôt qu'avec `==` ?**

`compare_digest` effectue une comparaison en temps constant, ce qui limite les risques d'attaques par analyse du temps de comparaison.

**4. Pourquoi `curl` fonctionne-t-il alors que la page du port 5501 est bloquée ?**

Parce que CORS est appliqué par les navigateurs. `curl` n'applique pas cette restriction.

**5. Pourquoi la validation faite par le navigateur ne remplace-t-elle pas celle de l'API ?**

Parce qu'un utilisateur peut contourner la validation du navigateur et envoyer directement une requête HTTP. L'API doit donc vérifier elle-même les données reçues.

## 6. Lien de la pull request

https://github.com/ziadserray04/LogiAI/pull/1
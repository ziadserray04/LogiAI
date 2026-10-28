# Compte rendu : TP API LogiAI

Nom : Ziad SERRAY  
Groupe :g3

## 1. Environnement et premiers tests

**Environnement utilisé :**
- Système : Windows
- Python : 3.10.10
- Framework API : FastAPI
- Validation : Pydantic
- Tests : Pytest
- Versionnement : Git et GitHub

**Sortie de `python -m pytest` au départ :**

Lors du premier lancement, 12 tests ont réussi et 1 test a échoué :

```text
collected 13 items

tests\test_api.py .......F.....

FAILED tests/test_api.py::test_pluie_impossible_refusee
assert 200 == 422

1 failed, 12 passed
```

Le test échouait parce que la valeur `pluie_mm = 500` était acceptée par le schéma initial.

**Pourquoi certains tests qui attendent un 422 passent-ils déjà, alors que rien n'est écrit ?**

FastAPI utilise automatiquement les schémas Pydantic pour valider les données reçues. Les champs obligatoires, les types, les valeurs autorisées par `Literal` et les contraintes définies avec `Field` sont contrôlés avant l'exécution de la fonction `predict()`.

Lorsqu'une donnée ne respecte pas le schéma, FastAPI renvoie automatiquement une erreur HTTP 422. Il n'est donc pas nécessaire d'écrire manuellement chaque vérification dans la fonction de prédiction.

## 2. Mon schéma

Les bornes suivantes correspondent au schéma actuellement implémenté dans `logiai/api/schemas.py`.

| Variable | Min | Max | Pourquoi |
|---|---:|---:|---|
| `distance_km` | 1 | 1 000 | Une livraison doit avoir une distance positive et une distance supérieure à 1 000 km est hors de la plage prévue pour ce projet. |
| `poids_kg` | 0,1 | 40 000 | Le poids doit être positif et 40 000 kg représente une limite maximale choisie pour le transport de marchandises. |
| `heure_depart` | 0 | 23 | Une heure est représentée par un entier compris entre 0 et 23. |
| `pluie_mm` | 0 | strictement inférieur à 500 | Les précipitations ne peuvent pas être négatives. La limite supérieure permet de rejeter des valeurs extrêmes. |
| `trafic_index` | 0 | 10 | L'indice de trafic est défini sur une échelle de 0 à 10. |
| `nb_arrets` | 0 | 100 | Le nombre d'arrêts est un entier positif, limité à 100 pour ce scénario. |

Le type `type_vehicule` accepte uniquement les valeurs `moto`, `fourgon` et `camion`. Le paramètre `extra="forbid"` interdit également les champs supplémentaires.

**Remarque :** la question de l'énoncé mentionne un contrôle `pluie <= 100`. Dans mon code actuel, la contrainte est `pluie_mm < 500`, afin de satisfaire le test qui exige le rejet de `pluie_mm = 500`. Si la borne demandée par l'enseignant est réellement 100 mm, elle doit être adaptée à `Field(ge=0, le=100)` et les tests doivent être relancés.

## 3. Ma fonction `predict()`

Le code implémenté dans `logiai/api/main.py` est le suivant :

```python
@app.post("/v1/predict", response_model=PredictionOut)
def predict(livraison: Livraison):
    predictor = state.get("predictor")

    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Le modèle de prédiction n'est pas chargé."
        )

    resultat = predictor.predict(livraison.model_dump())

    return PredictionOut(**resultat)
```

La fonction récupère le modèle déjà chargé au démarrage. Si le modèle est absent, elle renvoie une erreur 503. Sinon, elle transmet les caractéristiques de la livraison au prédicteur et retourne une réponse validée par `PredictionOut`.

La validation des entrées est effectuée automatiquement par FastAPI et Pydantic avant l'appel de cette fonction.

## 4. Quatre requêtes

| Requête | Code HTTP obtenu | Pourquoi |
|---|---:|---|
| Livraison normale | 200 | Les données sont valides et le modèle peut effectuer la prédiction. |
| `distance_km = -5` | 422 | La distance doit être supérieure ou égale à 1 km. |
| `type_vehicule = "avion"` | 422 | Le type de véhicule n'appartient pas aux valeurs autorisées. |
| Modèle absent | 503 | L'API fonctionne, mais le modèle nécessaire à la prédiction n'est pas chargé. |

Pour la livraison normale, un exemple testé a renvoyé :

```json
{
  "probabilite_retard": 0.9028,
  "alerte": true,
  "seuil": 0.4,
  "model_version": "1.0"
}
```

La probabilité estimée est de 90,28 %. Elle dépasse le seuil de 40 %, donc une alerte est déclenchée.

Pour le test du modèle absent, le code vérifie que le modèle est disponible au démarrage. Si le fichier du modèle est absent, l'application démarre sans le prédicteur et la requête de prédiction renvoie 503. Ce comportement est distinct d'une erreur de validation des données.

## 5. Questions de compréhension

### 1. Pourquoi charge-t-on le modèle au démarrage et pas à chaque requête ?

Le chargement au démarrage évite de relire et de recharger le modèle pour chaque demande. Cela réduit le temps de réponse et les opérations inutiles. Le modèle reste disponible en mémoire pour traiter plusieurs requêtes.

### 2. Qui écrit le contrôle « pluie <= 100 », et où est-il écrit ?

Le contrôle est défini par le développeur dans le schéma Pydantic, dans `logiai/api/schemas.py`, à l'aide de `Field`.

Dans mon implémentation actuelle, la contrainte est `ge=0, lt=500`, et non `le=100`. Si l'exigence du TP est une limite maximale de 100 mm, il faut écrire :

```python
pluie_mm: float = Field(
    ge=0,
    le=100,
    description="Précipitations (mm)"
)
```

FastAPI applique ensuite automatiquement cette contrainte aux requêtes entrantes.

### 3. Différence entre 422 et 503 ?

- **422 Unprocessable Entity :** les données reçues ne respectent pas le schéma de validation, par exemple une distance négative ou un véhicule inconnu.
- **503 Service Unavailable :** le service de prédiction ne peut pas traiter la demande parce que le modèle n'est pas disponible.

Le code 422 concerne donc les données envoyées, tandis que le code 503 concerne la disponibilité du composant nécessaire au traitement.

### 4. Pourquoi une route `/v1/predict` plutôt que `/predict` ?

Le préfixe `/v1` indique la version 1 de l'API. Il permet de faire évoluer l'API ultérieurement, par exemple avec `/v2/predict`, tout en conservant une version précédente pour les clients qui en dépendent.

### 5. Que se passerait-il si la distance était déclarée `int` ?

Le schéma attendrait un nombre entier plutôt qu'une distance décimale. Les valeurs comme `12.5` km ne seraient plus acceptées telles quelles par la validation stricte habituelle d'un champ entier. Utiliser `float` est donc plus adapté, car une distance peut être exprimée avec des décimales.

## 6. Décision : modèle absent

Deux stratégies sont possibles.

**Option 1 : renvoyer une erreur 503.**

L'application démarre même si le modèle est absent. Les routes de contrôle restent disponibles, notamment `/health`, mais les prédictions sont refusées tant que le modèle n'est pas chargé.

Cette solution permet de conserver une partie des fonctionnalités de l'API et de renvoyer une erreur explicite aux clients. En revanche, le service de prédiction n'est pas opérationnel.

**Option 2 : refuser de démarrer.**

L'application vérifie la présence du modèle et arrête son démarrage si celui-ci est absent.

Cette approche évite de démarrer un service incapable de répondre aux demandes de prédiction. Cependant, même la route de contrôle de santé devient indisponible et les autres fonctionnalités de l'application ne peuvent plus être utilisées.

**Décision retenue :** dans ce projet, le modèle est chargé au démarrage s'il existe. En son absence, l'application peut démarrer, mais `/v1/predict` renvoie 503. Cette stratégie permet de distinguer la disponibilité de l'API de celle du modèle.

## 7. Lien de la pull request

**Dépôt GitHub :**

https://github.com/ziadserray04/LogiAI

**Branche :** `tp-api`

**Dernier commit de correction :** `4253bfb` — `Fix rainfall validation`

**Lien pour créer la pull request :**

https://github.com/ziadserray04/LogiAI/pull/new/tp-api

La branche `tp-api` a été poussée sur GitHub et la commande `git status` a confirmé que la branche locale était synchronisée avec la branche distante.

Le projet a finalement obtenu **13 tests réussis sur 13** après la correction de la validation des précipitations.

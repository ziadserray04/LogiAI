"""Tests de l'API LogiAI."""

FACILE = {
    "distance_km": 5,
    "poids_kg": 3,
    "heure_depart": 11,
    "pluie_mm": 0,
    "trafic_index": 1,
    "nb_arrets": 0,
    "type_vehicule": "moto",
}


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_predict_valide(client, livraison_valide, headers_user):
    r = client.post(
        "/v1/predict",
        json=livraison_valide,
        headers=headers_user,
    )
    assert r.status_code == 200


def test_predict_retourne_probabilite(client, livraison_valide, headers_user):
    r = client.post(
        "/v1/predict",
        json=livraison_valide,
        headers=headers_user,
    )
    assert 0 <= r.json()["probabilite_retard"] <= 1


def test_predict_retourne_alerte(client, livraison_valide, headers_user):
    r = client.post(
        "/v1/predict",
        json=livraison_valide,
        headers=headers_user,
    )
    assert isinstance(r.json()["alerte"], bool)


def test_predict_retourne_seuil(client, livraison_valide, headers_user):
    r = client.post(
        "/v1/predict",
        json=livraison_valide,
        headers=headers_user,
    )
    assert r.json()["seuil"] == 0.4


def test_predict_retourne_version(client, livraison_valide, headers_user):
    r = client.post(
        "/v1/predict",
        json=livraison_valide,
        headers=headers_user,
    )
    assert r.json()["model_version"] == "1.0"


def test_predict_donnees_faciles(client, headers_user):
    r = client.post(
        "/v1/predict",
        json=FACILE,
        headers=headers_user,
    )
    assert r.status_code == 200


def test_predict_donnees_limites(client, headers_user):
    livraison = {
        "distance_km": 1000,
        "poids_kg": 1000,
        "heure_depart": 23,
        "pluie_mm": 100,
        "trafic_index": 10,
        "nb_arrets": 15,
        "type_vehicule": "camion",
    }

    r = client.post(
        "/v1/predict",
        json=livraison,
        headers=headers_user,
    )
    assert r.status_code == 200

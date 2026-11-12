"""Tests des limites et détection des deux bugs volontaires."""

import pytest

CAS_LIMITES = [
    # Distance
    ("distance_km", 1, 200),
    ("distance_km", 0.9, 422),
    ("distance_km", 1000, 200),
    ("distance_km", 1001, 422),
    # Poids
    ("poids_kg", 0.1, 200),
    ("poids_kg", 0.09, 422),
    ("poids_kg", 3500, 200),
    ("poids_kg", 3500.1, 422),
    # Heure de départ
    ("heure_depart", 0, 200),
    ("heure_depart", -1, 422),
    ("heure_depart", 23, 200),
    ("heure_depart", 24, 422),
    ("heure_depart", 11.5, 422),
    # Pluie
    ("pluie_mm", 0, 200),
    ("pluie_mm", -0.1, 422),
    ("pluie_mm", 100, 200),
    ("pluie_mm", 100.1, 422),
    # Trafic
    ("trafic_index", 0, 200),
    ("trafic_index", -0.1, 422),
    ("trafic_index", 10, 200),
    ("trafic_index", 10.1, 422),
    # Nombre d'arrêts
    ("nb_arrets", 0, 200),
    ("nb_arrets", -1, 422),
    ("nb_arrets", 15, 200),
    ("nb_arrets", 16, 422),
    ("nb_arrets", 11.5, 422),
]


@pytest.mark.parametrize(
    "champ, valeur, attendu",
    CAS_LIMITES,
)
def test_valeurs_limites(
    client,
    headers_user,
    livraison_valide,
    champ,
    valeur,
    attendu,
):
    livraison = livraison_valide.copy()
    livraison[champ] = valeur

    response = client.post(
        "/v1/predict",
        json=livraison,
        headers=headers_user,
    )

    assert response.status_code == attendu, (
        f"{champ}={valeur} : attendu {attendu}, obtenu {response.status_code}"
    )

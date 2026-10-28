
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="LogiAI - Prédiction des retards",
    page_icon="🚚",
    layout="wide",
)

st.title("🚚 LogiAI — Prédiction des retards")
st.write("Renseignez les informations de la livraison pour estimer son risque de retard.")

with st.form("livraison_form"):
    col1, col2 = st.columns(2)

    with col1:
        distance_km = st.number_input(
            "Distance (km)", min_value=1.0, max_value=1000.0, value=120.0
        )
        poids_kg = st.number_input(
            "Poids (kg)", min_value=0.1, max_value=40000.0, value=1500.0
        )
        heure_depart = st.number_input(
            "Heure de départ", min_value=0, max_value=23, value=8, step=1
        )
        type_vehicule = st.selectbox(
            "Type de véhicule", ["moto", "fourgon", "camion"]
        )

    with col2:
        pluie_mm = st.number_input(
            "Précipitations (mm)", min_value=0.0, max_value=500.0, value=12.5
        )
        trafic_index = st.slider(
            "Indice de trafic", min_value=0.0, max_value=10.0, value=7.5
        )
        nb_arrets = st.number_input(
            "Nombre d'arrêts", min_value=0, max_value=100, value=5, step=1
        )

    submitted = st.form_submit_button(
        "🔍 Prédire le risque de retard", use_container_width=True
    )

if submitted:
    livraison = {
        "distance_km": distance_km,
        "poids_kg": poids_kg,
        "heure_depart": heure_depart,
        "pluie_mm": pluie_mm,
        "trafic_index": trafic_index,
        "nb_arrets": nb_arrets,
        "type_vehicule": type_vehicule,
    }

    try:
        with st.spinner("Analyse de la livraison en cours..."):
            response = requests.post(
                f"{API_URL}/v1/predict",
                json=livraison,
                timeout=10,
            )

        if response.status_code == 200:
            resultat = response.json()
            probabilite = resultat["probabilite_retard"]
            alerte = resultat["alerte"]

            st.subheader("Résultat de la prédiction")

            c1, c2, c3 = st.columns(3)
            c1.metric("Probabilité de retard", f"{probabilite:.2%}")
            c2.metric("Seuil d'alerte", f"{resultat['seuil']:.0%}")
            c3.metric("Version du modèle", resultat["model_version"])

            st.progress(float(probabilite))

            if alerte:
                st.error("⚠️ Risque élevé : une alerte de retard est déclenchée.")
            else:
                st.success("✅ Le seuil d'alerte n'est pas atteint.")

            with st.expander("Voir les données envoyées à l'API"):
                st.json(livraison)

        else:
            try:
                detail = response.json().get("detail", response.text)
            except ValueError:
                detail = response.text
            st.error(f"Erreur API ({response.status_code}) : {detail}")

    except requests.exceptions.ConnectionError:
        st.error(
            "Impossible de contacter l'API. Vérifiez que FastAPI fonctionne "
            "dans le premier terminal sur http://127.0.0.1:8000."
        )
    except requests.exceptions.Timeout:
        st.error("L'API met trop de temps à répondre. Réessayez.")
    except requests.exceptions.RequestException as erreur:
        st.error(f"Erreur de communication avec l'API : {erreur}")

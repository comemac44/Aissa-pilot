import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date, datetime
import hashlib

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Aissa Pilot v3", layout="wide", page_icon="🏗️")

# --- SÉCURITÉ ---
USERS = {"Aissa": hashlib.sha256("27021985".encode()).hexdigest()}

# --- CONNEXION GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🏗️ Accès Aissa Pilot")
    u = st.text_input("Nom d'utilisateur")
    p = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if u in USERS and hashlib.sha256(p.encode()).hexdigest() == USERS[u]:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Identifiants incorrects")
else:
    # --- INTERFACE PRINCIPALE ---
    st.sidebar.title(f"Bonjour Aissa")
    
    # Lien vers votre dossier Drive pour les photos
    # REMPLACEZ par votre lien copié précédemment
    url_drive_photos = "VOTRE_LIEN_DOSSIER_DRIVE_ICI"
    st.sidebar.link_button("📸 Ouvrir mes Photos Drive", url_drive_photos)
    
    if st.sidebar.button("🚪 Déconnexion"):
        st.session_state.auth = False
        st.rerun()

    tab1, tab2, tab3 = st.tabs(["📝 Rapport & Paiement", "⚠️ Alertes Retard", "📁 Historique"])

    # --- TAB 1 : SAISIE ---
    with tab1:
        st.subheader("Enregistrement du jour")
        with st.form("main_form", clear_on_submit=True):
            proj = st.selectbox("Projet", ["Al Nour", "Villa Targa", "Immeuble Hay Riad", "Autre"])
            date_travail = st.date_input("Date", date.today())
            rapport = st.text_area("Rapport des travaux (Micro clavier 🎙️)")
            paiement = st.text_input("Avance ou Paiement urgent (ex: 500dh Ali)")
            date_echeance = st.date_input("Date limite de la tâche (pour alerte)", date.today())
            
            submit = st.form_submit_button("SAUVEGARDER DANS LE CLOUD")
            
            if submit:
                # Lecture du Sheets
                data = conn.read(worksheet="Sheet1")
                # Création de la ligne
                new_row = pd.DataFrame([{ "Date": str(date_travail), "Projet": proj, "Rapport": rapport, "Paiement": paiement, "Echeance": str(date_echeance)}])
                updated_df = pd.concat([data, new_row], ignore_index=True)
                # Envoi vers Google Sheets
                conn.update(worksheet="Sheet1", data=updated_df)
                st.success("✅ Données envoyées vers Google Sheets !")

    # --- TAB 2 : ALERTES ---
    with tab2:
        st.subheader("Tâches dépassant le temps programmé")
        data_alert = conn.read(worksheet="Sheet1")
        if not data_alert.empty:
            today = date.today()
            # On vérifie les dates d'échéance
            data_alert['Echeance'] = pd.to_datetime(data_alert['Echeance']).dt.date
            retards = data_alert[data_alert['Echeance'] < today]
            
            if not retards.empty:
                for index, row in retards.iterrows():
                    st.error(f"🚨 RETARD sur le projet {row['Projet']} ! Échéance dépassée le {row['Echeance']}")
            else:
                st.success("✅ Aucune tâche en retard pour le moment.")

    # --- TAB 3 : HISTORIQUE ---
    with tab3:
        st.subheader("Consultation des archives")
        history = conn.read(worksheet="Sheet1")
        st.dataframe(history.iloc[::-1]) # Du plus récent au plus ancien
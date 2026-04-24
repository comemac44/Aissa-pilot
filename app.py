import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime, date
import hashlib

# ─── CONFIGURATION DE LA PAGE ────────────────────────────────────────────────
st.set_page_config(
    page_title="ChantierPro Aissa",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── PARAMÈTRES ET DOSSIERS ──────────────────────────────────────────────────
USERS = {"Aissa": hashlib.sha256("27021985".encode()).hexdigest()}
DATA_DIR = "data"
PHOTOS_DIR = "data/photos"
FILES = {
    "chantiers": os.path.join(DATA_DIR, "chantiers.csv"),
    "finances": os.path.join(DATA_DIR, "finances.csv"),
    "taches": os.path.join(DATA_DIR, "taches.csv"),
}
PROJETS = ["Résidence Al Nour", "Villa Targa", "Immeuble Hay Riad", "Chantier Centre-Ville", "Autre"]

# ─── FONCTIONS TECHNIQUES ────────────────────────────────────────────────────
def init_dirs():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(PHOTOS_DIR):
        os.makedirs(PHOTOS_DIR)


def load_csv(key, columns):
    path = FILES[key]
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=columns)

def save_csv(key, df):
    df.to_csv(FILES[key], index=False)

# ─── INTERFACE LOGIN ─────────────────────────────────────────────────────────
def login_page():
    st.markdown("<h1 style='text-align: center; color: #f97316;'>🏗️ CHANTIER PRO</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("---")
        u = st.text_input("Nom d'utilisateur")
        p = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter", use_container_width=True):
            hashed_p = hashlib.sha256(p.encode()).hexdigest()
            if u in USERS and USERS[u] == hashed_p:
                st.session_state.auth = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Identifiants incorrects")

# ─── APPLICATION PRINCIPALE ──────────────────────────────────────────────────
def main():
    init_dirs()
    
    if "auth" not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:
        login_page()
        return

    # Menu du haut
    st.sidebar.title(f"Bienvenue {st.session_state.user}")
    if st.sidebar.button("Déconnexion"):
        st.session_state.auth = False
        st.rerun()

    tabs = st.tabs(["🚀 Dashboard", "📝 Rapports", "🎯 Objectifs", "💸 Finance Flash"])

    # --- TAB 1 : DASHBOARD ---
    with tabs[0]:
        st.subheader("💡 La Grande Idée du Jour")
        st.info("Un chantier bien suivi est un chantier qui rapporte. Vérifiez vos alertes ci-dessous.")
        
        taches_df = load_csv("taches", ["Tâche", "Date", "Statut"])
        if not taches_df.empty:
            taches_df['Date'] = pd.to_datetime(taches_df['Date']).dt.date
            retards = taches_df[(taches_df['Date'] < date.today()) & (taches_df['Statut'] != 'Terminé')]
            if not retards.empty:
                st.error(f"⚠️ Vous avez {len(retards)} tâche(s) en retard !")
                st.table(retards)

    # --- TAB 2 : RAPPORTS ---
    with tabs[1]:
        st.subheader("Nouveau Rapport de Chantier")
        with st.form("form_rapport", clear_on_submit=True):
            proj = st.selectbox("Projet", PROJETS)
            txt = st.text_area("Rapport des travaux")
            remarque = st.text_input("Remarque rapide (Note Flash)")
            if st.form_submit_button("Enregistrer le Rapport"):
                df = load_csv("chantiers", ["Date", "Projet", "Rapport", "Remarque"])
                new_row = pd.DataFrame([{"Date": date.today(), "Projet": proj, "Rapport": txt, "Remarque": remarque}])
                save_csv("chantiers", pd.concat([df, new_row]))
                st.success("Enregistré avec succès !")

    # --- TAB 3 : OBJECTIFS ---
    with tabs[2]:
        st.subheader("Mes Objectifs & Tâches")
        with st.form("form_tache"):
            t_nom = st.text_input("Nom de la tâche")
            t_date = st.date_input("Échéance")
            if st.form_submit_button("Ajouter"):
                df = load_csv("taches", ["Tâche", "Date", "Statut"])
                new_t = pd.DataFrame([{"Tâche": t_nom, "Date": t_date, "Statut": "À faire"}])
                save_csv("taches", pd.concat([df, new_t]))
                st.rerun()
        st.dataframe(load_csv("taches", ["Tâche", "Date", "Statut"]), use_container_width=True)

    # --- TAB 4 : FINANCE FLASH ---
    with tabs[3]:
        st.subheader("Paiements & Avances Urgents")
        with st.form("form_finance"):
            montant = st.number_input("Montant (MAD)", min_value=0)
            dest = st.text_input("Bénéficiaire / Motif")
            if st.form_submit_button("Enregistrer le paiement"):
                df = load_csv("finances", ["Date", "Montant", "Bénéficiaire"])
                new_f = pd.DataFrame([{"Date": date.today(), "Montant": montant, "Bénéficiaire": dest}])
                save_csv("finances", pd.concat([df, new_f]))
                st.warning("Paiement enregistré pour saisie comptable ultérieure.")
        st.dataframe(load_csv("finances", ["Date", "Montant", "Bénéficiaire"]), use_container_width=True)

if __name__ == "__main__":
    main()
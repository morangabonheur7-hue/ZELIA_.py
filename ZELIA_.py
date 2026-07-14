import streamlit as st
import requests
import urllib.parse

# 💎 TES CLÉS RÉELLES CENTRALISÉES EN DUR (CONFIANCE ET STABILITÉ)
SUPABASE_URL = "https://qjfipgzuwkprfowgbimt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFqZmlwZ3p1d2twcmZvd2diaW10Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA3NjAyNDksImV4cCI6MjA5NjMzNjI0OX0.rA17-omiRtXuECi0b7RW8wNe583Qa8swoV1HrgcQ9wM"

st.set_page_config(page_title="ZELIA GLOBAL - Panneau de Contrôle Suprême", page_icon="🛰️", layout="centered")

def injecter_dans_supabase(metier, ville, quartier, texte, telephone, lien, plateforme):
    url = f"{SUPABASE_URL}/rest/v1/leads"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}
    payload = [{
        "metier": metier.lower().strip(), 
        "ville": ville.lower().strip(), 
        "quartier": quartier.lower().strip(),
        "texte": texte, 
        "telephone": telephone.strip(), 
        "lien": lien, 
        "plateforme": plateforme
    }]
    try: requests.post(url, json=payload, headers=headers, timeout=10)
    except: pass

# 🎨 DESIGN MINIMALISTE MILITAIRE BLEU ROI PREMIUM
st.markdown("""
    <style>
    .main-title { color: #1E3A8A; font-size: 26px; font-weight: bold; text-align: center; margin-bottom: 5px; }
    .sub-title { color: #0F172A; font-size: 13px; text-align: center; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🛰️ ZELIA COMMAND CENTER</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Tableau de Bord Exclusif de Distribution Manuelle Internationale</div>', unsafe_allow_html=True)

onglet_scan, onglet_ajout = st.tabs(["🔍 SCANNER UNE VILLE DU MONDE", "📥 INJECTER UN CHANTIER"])

# ==========================================
# 1. SCANNER ET PILOTER UNE VILLE INTERNATIONALE
# ==========================================
with onglet_scan:
    st.markdown("### 🌍 Recherche Globale Supabase")
    
    search_c1, search_c2 = st.columns(2)
    with search_c1: S_metier = st.selectbox("Métier à chercher :", ["Plombier", "Électricien", "Serrurier", "Mécanicien"], key="s_metier")
    with search_c2: S_ville = st.text_input("✍️ Écris la ville cible (Ex: Paris, London, Miami...) :", value="Bruxelles", key="s_ville")
    
    st.markdown("---")
    
    # Extraction en direct de TOUS les chantiers de la table pour le métier sélectionné
    url_fetch = f"{SUPABASE_URL}/rest/v1/leads?metier=eq.{S_metier.lower()}&order=id.desc"
    headers_fetch = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    
    try:
        res = requests.get(url_fetch, headers=headers_fetch, timeout=10)
        if res.status_code == 200:
            leads = res.json()
            compteur = 0
            
            for lead in leads:
                l_ville = lead.get("ville", "").lower().strip()
                l_quartier = lead.get("quartier", "").lower().strip()
                
                # 🎯 COMPARAISON RADICALE : Si la ville correspond, on affiche TOUT, peu importe le quartier !
                if l_ville == S_ville.lower().strip():
                    compteur += 1
                    
                    st.markdown(f"""
                    <div style="background-color: #FFFFFF; border-left: 5px solid #1E3A8A; padding: 15px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0px 2px 4px rgba(0,0,0,0.05);">
                        <h4 style="color: #1E3A8A; margin: 0; font-size: 15px;">📡 CHANTIER ENREGISTRÉ</h4>
                        <p style="color: #0F172A; margin: 5px 0; font-size: 13px;"><b>Spécialité :</b> {lead['metier'].upper()} | <b>🌍 Ville :</b> {l_ville.upper()}</p>
                        <p style="color: #1E3A8A; margin: 5px 0; font-size: 13px;"><b>📍 Quartier / Saisie :</b> {l_quartier.upper()}</p>
                        <p style="color: #334155; font-size: 13px; margin-top: 8px; background: #F8FAFC; padding: 8px; border-radius: 4px;">{lead['texte']}</p>
                        <p style="color: #0F172A; font-size: 14px; margin-top: 5px;"><b>📱 Téléphone en clair :</b> {lead['telephone']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Nettoyage chirurgical du numéro pour éviter les bugs d'ouverture d'applications
                    tel_propre = "".join(c for c in lead['telephone'] if c.isdigit() or c == "+")
                    
                    c1, c2 = st.columns(2)
                    with c1: 
                        st.link_button(f"📞 Appel direct", f"tel:{tel_propre}", use_container_width=True)
                    with c2: 
                        # 🚀 OUVERTURE SANS BUG : Lance directement la discussion WhatsApp avec le numéro du bloc
                        st.link_button("🟢 Discuter sur WhatsApp", f"https://whatsapp.com{tel_propre}", use_container_width=True)

            if compteur == 0:
                st.info(f"🛰️ Aucune donnée active trouvée dans la table pour la ville de {S_ville.upper()}.")
                
    except Exception as e:
        st.error(f"Erreur de lecture de la base de données : {e}")

# ==========================================
# 2. INJECTER UN PARTICULIER DIRECTEMENT
# ==========================================
with onglet_ajout:
    st.markdown("### 📥 Insertion Manuelle de Leads")
    
    i_c1, i_c2 = st.columns(2)
    with i_c1: v_metier = st.selectbox("Métier :", ["Plombier", "Électricien", "Serrurier", "Mécanicien"], key="p_metier")
    with i_c2: v_ville = st.text_input("🌍 Ville d'urgence :", value="Paris", key="p_ville")
    
    v_quartier = st.text_input("📍 Zone / Quartier résidentiel :", value="Centre", key="p_quartier")
    v_tel = st.text_input("📱 Téléphone du contact :", placeholder="Ex: +33612345678", key="p_tel")
    v_desc = st.text_area("📝 Contenu brut de l'annonce ou de l'urgence :", key="p_desc")
    
    if st.button("🚀 Pousser dans la Table Supabase", use_container_width=True):
        if not v_tel or not v_desc:
            st.error("⚠️ Saisie incomplète.")
        else:
            texte_final = f"🚨 ACCÈS DIRECT COMMANDER:\n📢 Urgence {v_metier} à {v_ville} ({v_quartier})\n📝 Détails : {v_desc}"
            injecter_dans_supabase(v_metier, v_ville, v_quartier, texte_final, v_tel, "https://tinyurl.com", "Zelia Control Dashboard")
            st.success(f"✅ Lead enregistré avec succès pour {v_ville.upper()} !")
    

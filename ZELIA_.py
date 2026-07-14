import streamlit as st
import requests
import urllib.parse

# 💎 TES CLÉS RÉELLES CENTRALISÉES EN DUR (ZÉRO BUG)
SUPABASE_URL = "https://qjfipgzuwkprfowgbimt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFqZmlwZ3p1d2twcmZvd2diaW10Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA3NjAyNDksImV4cCI6MjA5NjMzNjI0OX0.rA17-omiRtXuECi0b7RW8wNe583Qa8swoV1HrgcQ9wM"

st.set_page_config(page_title="ZELIA GLOBAL - Radar International", page_icon="🚨", layout="centered")

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

# 🎨 DESIGN DE CONFIANCE BLEU ROI PREMIUM
st.markdown("""
    <style>
    .main-title { color: #1E3A8A; font-size: 28px; font-weight: bold; text-align: center; margin-bottom: 5px; }
    .sub-title { color: #0F172A; font-size: 14px; text-align: center; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚨 ZELIA GLOBAL NETWORK</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Centrale de Distribution d\'Urgences et de Dépannages</div>', unsafe_allow_html=True)

onglet_particulier, onglet_artisan = st.tabs(["🟢 DÉPOSER UNE URGENCE", "🔵 RADAR DE RECHERCHE PRO"])

# ==========================================
# 1. INTERFACE PARTICULIER (SAISIE SIMPLE)
# ==========================================
with onglet_particulier:
    st.markdown("### 📢 Signalement d'intervention immédiate")
    
    c1, c2 = st.columns(2)
    with c1: v_metier = st.selectbox("Métier requis :", ["Plombier", "Électricien", "Serrurier", "Mécanicien"], key="p_metier")
    with c2: v_ville = st.text_input("🌍 Ville concernée :", value="Bruxelles", key="p_ville")
    
    v_quartier = st.text_input("📍 Quartier / Zone Résidentielle :", value="Centre", key="p_quartier")
    v_tel = st.text_input("📱 Numéro de téléphone direct :", placeholder="Ex: +32488990011 ou +242055555555", key="p_tel")
    v_desc = st.text_area("📝 Détails de la panne ou du problème urgent :", key="p_desc")
    
    if st.button("🚀 Diffuser l'Urgence sur le Réseau", use_container_width=True):
        if not v_tel or not v_desc:
            st.error("⚠️ Veuillez fournir un numéro de téléphone et une description.")
        else:
            texte_final = f"🚨 CLIENT INTERCEPTÉ LIVE:\n📢 Urgence {v_metier} à {v_ville} ({v_quartier})\n📝 Détails : {v_desc}"
            injecter_dans_supabase(v_metier, v_ville, v_quartier, texte_final, v_tel, "https://tinyurl.com", "Zelia Global App v4")
            st.success(f"✅ Alerte injectée pour {v_ville.upper()} !")

# ==========================================
# 2. RADAR SIMPLE ET EFFICACE (RECHERCHE GLOBALE VILLE)
# ==========================================
with onglet_artisan:
    st.markdown("### 🛰️ Scanner de Chantiers International")
    
    search_c1, search_c2 = st.columns(2)
    with search_c1: S_metier = st.selectbox("Spécialité à scanner :", ["Plombier", "Électricien", "Serrurier", "Mécanicien"], key="s_metier")
    with search_c2: S_ville = st.text_input("🌍 Ville à cibler :", value="Bruxelles", key="s_ville")
    
    st.markdown("---")
    
    # Lecture directe de TOUS les chantiers du métier choisi
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
                
                # 🎯 MULTI-QUARTIER : On affiche TOUS les chantiers de la ville tapée, peu importe le quartier
                if l_ville == S_ville.lower().strip():
                    compteur += 1
                    
                    st.markdown(f"""
                    <div style="background-color: #FFFFFF; border-left: 5px solid #1E3A8A; padding: 15px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0px 2px 4px rgba(0,0,0,0.05);">
                        <h4 style="color: #1E3A8A; margin: 0; font-size: 15px;">🚨 CHANTIER DETECTÉ</h4>
                        <p style="color: #0F172A; margin: 5px 0; font-size: 13px;"><b>Métier :</b> {lead['metier'].upper()} | <b>🌍 Ville :</b> {l_ville.upper()}</p>
                        <p style="color: #1E3A8A; margin: 5px 0; font-size: 13px;"><b>📍 Quartier / Secteur :</b> {l_quartier.upper()}</p>
                        <p style="color: #334155; font-size: 13px; margin-top: 8px; background: #F8FAFC; padding: 8px; border-radius: 4px;">{lead['texte']}</p>
                        <p style="color: #0F172A; font-size: 14px; margin-top: 5px;"><b>📞 Contact direct :</b> {lead['telephone']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Nettoyage propre du numéro pour les liens téléphoniques et WhatsApp
                    tel_propre = "".join(c for c in lead['telephone'] if c.isdigit() or c == "+")
                    
                    # 🚀 BOUTONS D'ACTIONS SANS AUCUN BEUG ET SANS PAGE BLANCHE
                    c1, c2 = st.columns(2)
                    with c1: 
                        st.link_button(f"📞 Appel Normal", f"tel:{tel_propre}", use_container_width=True)
                    with c2: 
                        # Format universel pour ouvrir directement l'application WhatsApp sur n'importe quel téléphone
                        st.link_button("🟢 Ouvrir WhatsApp", f"https://whatsapp.com{tel_propre}", use_container_width=True)

            if compteur == 0:
                st.info(f"🛰️ Le radar n'a détecté aucune alerte active sur {S_ville.upper()} pour l'instant.")
                
    except Exception as e:
        st.error(f"Erreur de connexion au réseau : {e}")
                           

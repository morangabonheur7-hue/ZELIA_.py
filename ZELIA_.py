import streamlit as st
import requests
import urllib.parse

# 💎 TES CLÉS RÉELLES CENTRALISÉES EN DUR (ZÉRO BUG DE CHARGEMENT)
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

# 🎨 DESIGN DE CONFIANCE BLEU ROI UNIVERSEL (S'AFFICHE SUR TOUS LES MOBILES)
st.markdown("""
    <style>
    .main-title { color: #1E3A8A; font-size: 28px; font-weight: bold; text-align: center; margin-bottom: 5px; }
    .sub-title { color: #0F172A; font-size: 14px; text-align: center; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚨 ZELIA GLOBAL NETWORK</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Centrale de Distribution d\'Urgences et de Dépannages</div>', unsafe_allow_html=True)

# Navigation ultra-légère par onglets standard (aucune variable de session lourde)
onglet_particulier, onglet_artisan = st.tabs(["🟢 DÉPOSER UNE URGENCE", "🔵 RADAR DE RECHERCHE PRO"])

# ==========================================
# 1. INTERFACE PARTICULIER INTERNATIONALE
# ==========================================
with onglet_particulier:
    st.markdown("### 📢 Signalement d'intervention immédiate")
    
    c1, c2 = st.columns(2)
    with c1: v_metier = st.selectbox("Métier requis :", ["Plombier", "Électricien", "Serrurier", "Mécanicien"], key="p_metier")
    with c2: v_ville = st.text_input("🌍 Ville concernée :", value="Bruxelles", key="p_ville")
    
    v_quartier = st.text_input("📍 Quartier / Zone Résidentielle (Ex: Schaerbeek, Ouenzé...)", value="Centre", key="p_quartier")
    v_tel = st.text_input("📱 Numéro de téléphone direct (avec indicatif) :", placeholder="+32 4xx xx xx xx", key="p_tel")
    v_desc = st.text_area("📝 Description de la panne ou du problème urgent :", placeholder="Ex: Fuite d'eau abondante sous l'évier...", key="p_desc")
    
    if st.button("🚀 Diffuser l'Urgence sur le Réseau", use_container_width=True):
        if not v_tel or not v_desc:
            st.error("⚠️ Veuillez fournir un numéro de téléphone et une description claire.")
        else:
            texte_final = f"🚨 CLIENT CERTIFIÉ CHAUD (ZELIA LIVE):\n📢 Urgence {v_metier} à {v_ville} ({v_quartier})\n📝 Détails : {v_desc}"
            injecter_dans_supabase(v_metier, v_ville, v_quartier, texte_final, v_tel, "https://tinyurl.com", "Zelia Global App v4")
            st.success(f"✅ Alerte injectée ! Le radar local de {v_ville.upper()} a capté le signal.")

# ==========================================
# 2. RADAR DE RECHERCHE TECHNIQUE TACTIQUE
# ==========================================
with onglet_artisan:
    st.markdown("### 🛰️ Scanner de Chantiers International")
    
    search_c1, search_c2 = st.columns(2)
    with search_c1: S_metier = st.selectbox("Spécialité à scanner :", ["Plombier", "Électricien", "Serrurier", "Mécanicien"], key="s_metier")
    with search_c2: S_ville = st.text_input("🌍 Ville à cibler :", value="Bruxelles", key="s_ville")
    
    S_quartier = st.text_input("📍 Quartier précis (Laissez 'Global' pour scanner toute la ville) :", value="Global", key="s_quartier")
    
    st.markdown("---")
    
    # Bouton d'action pour interroger la base de données
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
                
                # Filtrage croisé Ville + (Quartier ou Mode Global)
                if l_ville == S_ville.lower().strip() and (S_quartier.lower().strip() == "global" or l_quartier == S_quartier.lower().strip() or l_quartier == "centre"):
                    compteur += 1
                    
                    st.markdown(f"""
                    <div style="background-color: #FFFFFF; border-left: 5px solid #1E3A8A; padding: 15px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0px 2px 4px rgba(0,0,0,0.05);">
                        <h4 style="color: #1E3A8A; margin: 0; font-size: 15px;">🚨 CHANTIER INTERCEPTÉ</h4>
                        <p style="color: #0F172A; margin: 5px 0; font-size: 13px;"><b>Métier :</b> {lead['metier'].upper()} | <b>🌍 Ville :</b> {l_ville.upper()}</p>
                        <p style="color: #1E3A8A; margin: 5px 0; font-size: 13px;"><b>📍 Quartier :</b> {l_quartier.upper()}</p>
                        <p style="color: #334155; font-size: 13px; margin-top: 8px; background: #F8FAFC; padding: 8px; border-radius: 4px;">{lead['texte']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 🔒 VERROU DE SÉCURITÉ ET CAPTURE SMMA POUR LE FORCER À PAYER LES 29,99€
                    with st.expander("🔐 Débloquer le Contact et Appeler le Client"):
                        st.warning("Ce chantier est réel et exclusif. Pour obtenir le numéro direct et lancer l'intervention, activez votre abonnement ZELIA.")
                        
                        texte_signal = f"🚨 ACTIVATION COMPTE ZELIA PRO 🚨\n\nJe souhaite débloquer le numéro du client :\n🧑‍🔧 Métier : {S_metier.upper()}\n🌍 Ville : {S_ville.upper()}"
                        msg_encode = urllib.parse.quote(texte_signal)
                        
                        tel_propre = lead['telephone'].replace(" ", "")
                        
                        # Liens d'actions d'urgence
                        st.link_button("💳 Activer mon Accès Pro Zelia (29,99€)", f"whatsapp://send?phone=242055967601&text={msg_encode}", use_container_width=True, type="primary")
                        st.markdown("---")
                        c1, c2 = st.columns(2)
                        with c1: st.link_button(f"📞 Appeler ({lead['telephone']})", f"tel:{tel_propre}", use_container_width=True)
                        with c2: st.link_button("🟢 WhatsApp Client", f"https://wa.me{tel_propre}?text=Bonjour", use_container_width=True)

            if compteur == 0:
                st.info(f"🛰️ Aucune alerte active détectée sur {S_ville.upper()} ({S_quartier.upper()}) pour le moment.")
                
    except Exception as e:
        st.error(f"Erreur de connexion au réseau : {e}")

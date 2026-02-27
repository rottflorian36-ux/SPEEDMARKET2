"""
SMART EXCHANGE - Application de Facturation Pro
v3.0 — Zero-Error Edition
Architecture: Claude extrait les lignes BRUTES → Python calcule TOUT
"""
import streamlit as st
import pandas as pd
import base64
import io
import os
import re
import json
import requests
from datetime import datetime, date
from fpdf import FPDF
from collections import defaultdict, OrderedDict
from decimal import Decimal, ROUND_HALF_UP

# ═══════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════
st.set_page_config(
    page_title="SMART EXCHANGE · Facturation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

COMPANY = {
    "name": "SMART EXCHANGE",
    "siren": "982 412 132",
    "siret": "982 412 132 00010",
    "tva": "FR48982412132",
    "email": "Smartexchange673@gmail.com",
}

# ═══════════════════════════════════════
# IMAGES
# ═══════════════════════════════════════
def load_image_b64(filename):
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filename),
        os.path.join(os.getcwd(), filename),
        filename,
    ]
    for path in candidates:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return ""

BANNER_B64 = load_image_b64("banner.png")
BG_B64 = load_image_b64("bg.png")

# ═══════════════════════════════════════
# CSS (identical to v2)
# ═══════════════════════════════════════
st.markdown(f"""
<style>
    .stApp {{
        background: #0a0a14 !important;
        color: #FFFFFF !important;
    }}
    .stApp > div, .stApp > div > div {{ color: #FFFFFF !important; }}
    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{ color: #FFFFFF !important; }}
    p, span, div, label, h1, h2, h3, h4, h5, h6 {{ color: inherit; }}
    .element-container {{ color: #FFFFFF !important; }}
    .stApp::before {{
        content: '';
        position: fixed;
        inset: 0;
        background-image: url("data:image/png;base64,{BG_B64}");
        background-size: cover;
        background-position: center;
        opacity: 0.05;
        pointer-events: none;
        z-index: 0;
    }}
    #MainMenu {{visibility: hidden}}
    footer {{visibility: hidden}}
    header {{visibility: hidden}}
    .block-container {{
        padding-top: 0.5rem !important;
        max-width: 1100px;
    }}
    .banner {{
        width: 100%;
        border-radius: 20px;
        overflow: hidden;
        position: relative;
        margin-bottom: 1rem;
        box-shadow: 0 8px 40px rgba(255,140,50,0.12);
        border: 1px solid rgba(255,160,50,0.3);
    }}
    .banner img {{
        width: 100%;
        height: 180px;
        object-fit: cover;
        object-position: center 30%;
        display: block;
    }}
    .banner-ov {{
        position: absolute;
        inset: 0;
        background: linear-gradient(180deg, rgba(10,10,20,0.1) 0%, rgba(10,10,20,0.85) 100%);
        display: flex;
        align-items: flex-end;
        padding: 1.2rem 1.5rem;
    }}
    .b-title {{
        font-family: Impact, 'Arial Black', sans-serif;
        font-size: 2.2rem;
        color: white;
        letter-spacing: 4px;
        line-height: 1;
        text-shadow: 0 2px 20px rgba(255,140,50,0.3);
    }}
    .b-title span {{ color: #FF8C32; }}
    .b-sub {{
        font-size: 0.72rem;
        color: #FFB347;
        letter-spacing: 3px;
        font-weight: 600;
        text-transform: uppercase;
        margin-top: 2px;
    }}
    .b-line {{
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, #FF8C32, #FFB347, transparent);
    }}
    .sec {{
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 1.3rem;
        margin: 0.7rem 0;
        backdrop-filter: blur(16px);
    }}
    .sec:hover {{ border-color: rgba(255,160,50,0.3); }}
    .sec-h {{
        color: #FF8C32;
        font-size: 0.95rem;
        font-weight: 700;
        margin-bottom: 0.9rem;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .tot-box {{
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
    }}
    .tot-box .lbl {{
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 4px;
    }}
    .tot-box .val {{
        font-size: 1.6rem;
        font-weight: 900;
        font-family: 'Courier New', monospace;
    }}
    .tot-ht {{
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
    }}
    .tot-ht .lbl {{ color: rgba(255,255,255,0.4); }}
    .tot-ht .val {{ color: #eaeaf2; }}
    .tot-tva {{
        background: rgba(255,140,50,0.06);
        border: 1px solid rgba(255,160,50,0.3);
    }}
    .tot-tva .lbl {{ color: rgba(255,140,50,0.7); }}
    .tot-tva .val {{ color: #FF8C32; }}
    .tot-ttc {{
        background: linear-gradient(135deg, #FF6B1A, #FF8C32, #FFB347);
        box-shadow: 0 6px 30px rgba(255,140,50,0.25);
    }}
    .tot-ttc .lbl {{ color: rgba(10,10,20,0.5); }}
    .tot-ttc .val {{ color: #0a0a14; font-size: 1.8rem; }}
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stTextArea > div > div > textarea {{
        background: rgba(26,26,46,0.95) !important;
        border: 1px solid rgba(255,140,50,0.2) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
    }}
    .stTextInput > div > div > input::placeholder {{ color: rgba(255,255,255,0.4) !important; }}
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {{
        border-color: #FF8C32 !important;
        box-shadow: 0 0 0 2px rgba(255,140,50,0.15) !important;
    }}
    .stTextInput label, .stNumberInput label, .stSelectbox label,
    .stDateInput label, .stTextArea label {{ color: #FFFFFF !important; }}
    .stDateInput > div > div > input {{
        background: rgba(26,26,46,0.95) !important;
        border: 1px solid rgba(255,140,50,0.2) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
    }}
    .stButton > button {{
        background: linear-gradient(135deg, #FF6B1A, #FF8C32, #FFB347) !important;
        color: #0a0a14 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.5rem 1.5rem !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px rgba(255,140,50,0.35) !important;
    }}
    .stDownloadButton > button {{
        background: linear-gradient(135deg, #FF6B1A, #FF8C32, #FFB347) !important;
        color: #0a0a14 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        width: 100%;
    }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 3px; }}
    .stTabs [data-baseweb="tab"] {{
        background: rgba(255,255,255,0.03);
        border-radius: 10px 10px 0 0;
        border: 1px solid rgba(255,255,255,0.06);
        color: white;
        padding: 8px 18px;
    }}
    .stTabs [aria-selected="true"] {{
        background: rgba(255,140,50,0.12) !important;
        border-bottom: 2px solid #FF8C32 !important;
    }}
    .sep {{ height: 1px; background: linear-gradient(90deg, transparent, rgba(255,160,50,0.3), transparent); margin: 0.4rem 0; }}
    .foot {{ text-align: center; padding: 1rem; color: rgba(255,255,255,0.25); font-size: 0.7rem; }}
    .badge {{
        display: inline-block;
        background: rgba(255,140,50,0.12);
        color: #FF8C32;
        border: 1px solid rgba(255,160,50,0.3);
        border-radius: 20px;
        padding: 3px 13px;
        font-size: 0.7rem;
        font-weight: 700;
    }}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════
if "lines" not in st.session_state:
    st.session_state.lines = []
if "lid" not in st.session_state:
    st.session_state.lid = 0
if "clients" not in st.session_state:
    st.session_state.clients = {}

DEFAULT_CLIENTS = {
    "RAF MARKET": {
        "addr": "196 avenue du Maine\n75014 Paris",
        "siret": "990 314 007 00016",
        "tva": "FR37990314007",
    },
}

CLIENTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clients.json")

def load_clients():
    clients = dict(DEFAULT_CLIENTS)
    try:
        if os.path.exists(CLIENTS_FILE):
            with open(CLIENTS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                clients.update(saved)
    except:
        pass
    return clients

def save_clients(clients_dict):
    try:
        with open(CLIENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(clients_dict, f, ensure_ascii=False, indent=2)
    except:
        pass

if not st.session_state.clients:
    st.session_state.clients = load_clients()
for k, v in DEFAULT_CLIENTS.items():
    if k not in st.session_state.clients:
        st.session_state.clients[k] = v


# ═══════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")
    st.markdown("**📋 Infos entreprise**")
    st.markdown(f"""
    <div style='font-size:.75rem;color:rgba(255,255,255,0.5);line-height:1.6'>
    {COMPANY['name']}<br>
    SIREN: {COMPANY['siren']}<br>
    TVA: {COMPANY['tva']}<br>
    {COMPANY['email']}
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════
# HELPERS — Decimal precision
# ═══════════════════════════════════════
D = Decimal

def d(val):
    """Convert to Decimal safely"""
    if isinstance(val, Decimal):
        return val
    return D(str(val))

def ht_from_ttc(ttc, tva_rate):
    """TTC → HT with proper rounding"""
    ttc_d = d(ttc)
    rate_d = d(tva_rate)
    if rate_d <= 0:
        return float(ttc_d)
    ht = (ttc_d / (D("1") + rate_d / D("100"))).quantize(D("0.01"), rounding=ROUND_HALF_UP)
    return float(ht)

def ttc_from_ht(ht, tva_rate):
    """HT → TTC with proper rounding"""
    ht_d = d(ht)
    rate_d = d(tva_rate)
    ttc = (ht_d * (D("1") + rate_d / D("100"))).quantize(D("0.01"), rounding=ROUND_HALF_UP)
    return float(ttc)

def fmt(val):
    return f"{val:,.2f} €".replace(",", " ").replace(".", ",")

def add_line(desc="", qty=1, pu_ht=0.0, tva=20.0, tot_ttc_override=None):
    st.session_state.lid += 1
    st.session_state.lines.append({
        "id": st.session_state.lid,
        "desc": desc, "qty": qty, "pu_ht": pu_ht, "tva": tva,
        "tot_ttc_override": tot_ttc_override,
    })


# ═══════════════════════════════════════
# SCAN v3 — RAW LINE EXTRACTION
# Claude extracts RAW lines, Python aggregates
# ═══════════════════════════════════════

SCAN_PROMPT = """Tu es un extracteur de donnees ultra-precis. Tu lis une facture fournisseur et extrais chaque ligne.

REGLE ABSOLUE: NE RECALCULE JAMAIS RIEN. Copie les chiffres EXACTEMENT tels qu'ils apparaissent sur la facture.

═══════════════════════════════════════
DETECTION DU TYPE DE FACTURE
═══════════════════════════════════════

METRO: On voit des colonnes "Prix unitaire | VE | Qte | Montant | TVA" et des lignes "COTIS. SECURITE SOCIALE"
CARREFOUR/SUPERMARCHE: On voit des colonnes "TVA% | Produit | QTE x P.U. | Montant TTC" avec des "Remise immediate"
AUTRE: Adapte-toi au format visible

═══════════════════════════════════════
INSTRUCTIONS SPECIFIQUES METRO (TRES IMPORTANT)
═══════════════════════════════════════

Sur une facture Metro, chaque produit a PLUSIEURS lignes:
  Ligne 1: NOM PRODUIT   [prix_unit]   [VE]   [Qte_colis]   [MONTANT_HT]   [TVA_CODE]
  Ligne 2: "COTIS. SECURITE SOCIALE"   [montant_cotis]   [TVA_CODE]
  (optionnel) Ligne 3: "Offre Achetez Plus Payez Moins"   [-remise]

REGLES METRO:
1. Le MONTANT_HT visible sur la ligne produit = montant AVANT cotisation sociale
2. La COTIS. SECURITE SOCIALE doit etre AJOUTEE au montant HT du produit precedent
3. L'"Offre Achetez Plus Payez Moins" est une REMISE → SOUSTRAIRE du montant HT (une seule fois meme si apparait 2 fois de suite pour le meme produit)
4. Le montant_final_HT = MONTANT_HT_produit + COTIS_SECURITE_SOCIALE - remises_eventuelles
5. La quantite totale = VE (unites par colis) × Qte_colis (nombre de colis)
6. Codes TVA Metro: B=5.5%, C=20%, D=20%

EXEMPLE METRO:
  VODKA POLIAKOV 37.5D 70CL   7.640   6   1   45.84   D
  COTIS. SECURITE SOCIALE   9.60   D
  Offre Achetez Plus Payez Moins   -9.12

  → desc: "VODKA POLIAKOV 37.5D 70CL"
  → qte: 6 × 1 = 6
  → montant_ht_final: 45.84 + 9.60 - 9.12 = 46.32
  → tva: 20.0

AUTRE EXEMPLE (2 lignes colis du meme produit):
  VODKA POLIAKOV 37.5D 70CL   7.640   6   1   45.84   D
  COTIS. SECURITE SOCIALE   9.60   D
  Offre Achetez Plus Payez Moins   -9.12
  VODKA POLIAKOV 37.5D 70CL   7.640   6   3   137.52   D
  COTIS. SECURITE SOCIALE   28.80   D
  Offre Achetez Plus Payez Moins   -9.12

  → On fusionne en UNE seule ligne:
  → desc: "VODKA POLIAKOV 37.5D 70CL"
  → qte: (6×1) + (6×3) = 24
  → montant_ht_final: (45.84 + 9.60 - 9.12) + (137.52 + 28.80 - 9.12) = 203.52
  → tva: 20.0

═══════════════════════════════════════
INSTRUCTIONS SPECIFIQUES CARREFOUR/SUPERMARCHE
═══════════════════════════════════════

- Chaque ligne produit: desc, qte, pu_ttc, montant_ttc, tva_rate
- "Remise immediate -X.XX" → soustraire du montant_ttc du produit precedent
- Les montants sont en TTC
- Fusionner les lignes identiques du meme produit

═══════════════════════════════════════
TOTAUX DE LA FACTURE
═══════════════════════════════════════

Extrais imperativement les totaux affiches sur la facture:
- total_ht: le montant HT total affiche
- total_tva: le montant TVA total affiche
- total_ttc: le montant TTC total affiche (= "Total a payer" sur Metro)
- La ventilation TVA si presente (base HT par taux, montant TVA, montant TTC)

Sur Metro page 10/11: le tableau de ventilation TVA et le "Total a payer" sont la reference.

═══════════════════════════════════════
FORMAT JSON DE REPONSE
═══════════════════════════════════════

{
  "type": "metro" ou "carrefour" ou "autre",
  "totaux": {
    "total_ht": nombre ou null,
    "total_tva": nombre ou null,
    "total_ttc": nombre,
    "ventilation_tva": [
      {"taux": 5.5, "base_ht": nombre, "montant_tva": nombre},
      {"taux": 20.0, "base_ht": nombre, "montant_tva": nombre}
    ]
  },
  "lignes": [
    {
      "desc": "NOM PRODUIT EXACT",
      "qte": nombre_total_unites,
      "montant": nombre_ht_final_apres_cotis_et_remises,
      "type_montant": "ht",
      "tva": 5.5 ou 20.0
    }
  ]
}

Pour Carrefour: "type_montant": "ttc" et montant = montant TTC apres remises

VERIFICATION FINALE:
- Pour Metro: somme de tous les montants_ht_final doit etre proche du total_ht affiche
- Pour Carrefour: somme des montants TTC doit etre proche du total_ttc

REPONDS UNIQUEMENT AVEC LE JSON. Pas de ```, pas d'explication, pas de commentaire."""


def scan_invoice_v3(file_bytes, mime_type="image/jpeg"):
    """v3: Extract RAW lines from invoice, let Python do all calculations."""
    api_key = ""
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    except Exception:
        pass
    if not api_key:
        api_key = st.session_state.get("anthropic_key", "")
    if not api_key:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None, "Cle API non trouvee. Ajoutez ANTHROPIC_API_KEY dans Settings → Secrets."

    api_key = api_key.strip()
    if not api_key.startswith("sk-"):
        return None, "Format de cle invalide (doit commencer par sk-)."

    # Extract images + text from PDF
    images_b64 = []
    pdf_text = ""
    if mime_type == "application/pdf":
        try:
            import fitz
            pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page_num in range(min(len(pdf_doc), 12)):
                page = pdf_doc[page_num]
                page_text = page.get_text("text")
                if page_text.strip():
                    pdf_text += f"\n--- PAGE {page_num+1} ---\n{page_text}"
                mat = fitz.Matrix(2.0, 2.0)
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                images_b64.append({
                    "b64": base64.b64encode(img_data).decode("ascii"),
                    "media": "image/png",
                })
            pdf_doc.close()
        except ImportError:
            return None, "Installez PyMuPDF: ajoutez 'PyMuPDF>=1.23.0' dans requirements.txt"
        except Exception as e:
            return None, f"Erreur lecture PDF: {str(e)}"
    else:
        media = "image/jpeg"
        if mime_type == "image/png":
            media = "image/png"
        elif mime_type == "image/webp":
            media = "image/webp"
        images_b64.append({
            "b64": base64.b64encode(file_bytes).decode("ascii"),
            "media": media,
        })

    if not images_b64:
        return None, "Aucune image extraite"

    content_blocks = []
    if pdf_text.strip():
        content_blocks.append({
            "type": "text",
            "text": f"TEXTE EXTRAIT DU PDF (PRIORITAIRE pour les chiffres):\n{pdf_text[:40000]}",
        })
    for img in images_b64:
        content_blocks.append({
            "type": "image",
            "source": {"type": "base64", "media_type": img["media"], "data": img["b64"]},
        })
    content_blocks.append({"type": "text", "text": SCAN_PROMPT})

    try:
        models = ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022"]
        resp = None
        for model in models:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": 32000,
                    "messages": [{"role": "user", "content": content_blocks}],
                },
                timeout=300,
            )
            if resp.status_code == 200:
                break
            if resp.status_code in (404, 400) and "model" in resp.text.lower():
                continue
            break

        if resp.status_code == 401:
            return None, "Erreur authentification API (401). Verifiez votre cle."
        if resp.status_code == 429:
            return None, "Limite API atteinte. Reessayez dans quelques secondes."
        if resp.status_code != 200:
            err = ""
            try:
                err = resp.json().get("error", {}).get("message", "")
            except:
                err = resp.text[:300]
            return None, f"Erreur API ({resp.status_code}): {err}"

        data = resp.json()
        content = data.get("content", [{}])[0].get("text", "").strip()
        raw = content

        # Parse JSON
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        content = content.strip()

        parsed = None
        try:
            parsed = json.loads(content)
        except:
            match = re.search(r'\{[\s\S]*\}', content)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                except:
                    pass

        if not parsed or not isinstance(parsed, dict):
            return None, f"Reponse invalide. Debut: {raw[:300]}"

        return parsed, None

    except requests.exceptions.Timeout:
        return None, "Timeout — reduisez la taille du fichier."
    except Exception as e:
        return None, f"Erreur: {str(e)}"


def process_raw_scan(raw_data):
    """
    PYTHON does ALL the math. Takes raw lines from Claude (already aggregated per product),
    produces articles with exact HT/TTC totals.
    
    For METRO: Claude delivers montant_ht_final (product HT + cotis - remises) per product.
    For CARREFOUR: Claude delivers montant_ttc_final per product.
    """
    lignes = raw_data.get("lignes", [])
    totaux = raw_data.get("totaux", {})
    facture_type = raw_data.get("type", "autre")
    
    if not lignes:
        return [], totaux

    articles = []
    for lg in lignes:
        desc = lg.get("desc", "").strip()
        if not desc:
            continue
        montant = float(lg.get("montant", 0))
        qte = int(lg.get("qte", 0)) or 1
        tva_rate = float(lg.get("tva", 20.0))
        type_m = lg.get("type_montant", "ttc")

        # Skip section headers, totals, palettes, etc.
        desc_up = desc.upper()
        skip_kw = ["***", "SOUS-TOTAL", "PALETTE", "PAL.", "PAL ", "CHEP", 
                   "LOGIPAL", "LPR", "CONSIGN", "80X120", "AVOIR", "TRANSPORT",
                   "FRAIS DE PORT", "PRIX AU KG", "COTIS.", "OFFRE ACHETEZ"]
        if any(kw in desc_up for kw in skip_kw):
            continue

        if montant == 0:
            continue

        if type_m == "ht":
            # Metro: montant is already the final HT (product + cotis - remises)
            total_ht = round(montant, 2)
            total_ttc = round(total_ht * (1 + tva_rate / 100), 2)
        else:
            # Carrefour: montant is TTC
            total_ttc = round(montant, 2)
            total_ht = ht_from_ttc(total_ttc, tva_rate)

        pu_ht = round(total_ht / qte, 4)
        pu_ttc = round(total_ttc / qte, 4)

        articles.append({
            "desc": desc,
            "qte": qte,
            "pu_ht": pu_ht,
            "pu_ttc": pu_ttc,
            "tva": tva_rate,
            "total_ht": total_ht,
            "total_ttc": total_ttc,
        })

    return articles, totaux


# ═══════════════════════════════════════
# COMPUTE (for manual lines)
# ═══════════════════════════════════════
def del_line(lid):
    st.session_state.lines = [l for l in st.session_state.lines if l["id"] != lid]

def compute(line):
    pu_ttc = ttc_from_ht(line["pu_ht"], line["tva"])
    if line.get("tot_ttc_override") is not None:
        tot_ttc = line["tot_ttc_override"]
        tot_ht = ht_from_ttc(tot_ttc, line["tva"])
    else:
        tot_ht = round(line["qty"] * line["pu_ht"], 2)
        tot_ttc = ttc_from_ht(tot_ht, 0) if line["tva"] == 0 else ttc_from_ht(tot_ht, -line["tva"])  
        # Simpler: just compute from ht
        tot_ttc = round(tot_ht * (1 + line["tva"] / 100), 2)
    pu_ht = line["pu_ht"]
    if line.get("tot_ttc_override") is not None and line["qty"] > 0:
        pu_ht = round(tot_ht / line["qty"], 2)
        pu_ttc = round(tot_ttc / line["qty"], 2)
    return {**line, "pu_ht": pu_ht, "pu_ttc": pu_ttc, "tot_ht": tot_ht, "tot_ttc": tot_ttc}


# ═══════════════════════════════════════
# PDF GENERATOR
# ═══════════════════════════════════════
class InvoicePDF(FPDF):
    def __init__(self, client_name, client_addr, inv_num, inv_date):
        super().__init__()
        self.c_name = client_name
        self.c_addr = client_addr
        self.inv_num = inv_num
        self.inv_date = inv_date

    def header(self):
        self.set_fill_color(26, 26, 46)
        self.rect(0, 0, 210, 48, "F")
        self.set_fill_color(255, 140, 50)
        self.rect(0, 48, 210, 2.5, "F")
        self.set_font("Helvetica", "B", 26)
        self.set_text_color(255, 255, 255)
        self.set_xy(15, 10)
        self.cell(0, 12, "SMART EXCHANGE", 0, 0, "L")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(255, 179, 71)
        self.set_xy(15, 23)
        self.cell(0, 6, "FACTURATION", 0, 0, "L")
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(255, 255, 255)
        self.set_xy(120, 18)
        self.cell(0, 6, f"Facture : {self.inv_num}", 0, 0, "R")
        self.set_font("Helvetica", "", 9)
        self.set_xy(120, 25)
        self.cell(0, 6, f"Date : {self.inv_date}", 0, 0, "R")
        self.ln(55)

    def footer(self):
        self.set_y(-25)
        self.set_draw_color(255, 140, 50)
        self.set_line_width(0.4)
        self.line(15, self.get_y(), 195, self.get_y())
        self.set_font("Helvetica", "", 6.5)
        self.set_text_color(140, 140, 160)
        self.ln(3)
        self.cell(0, 3.5, f"{COMPANY['name']} | SIREN : {COMPANY['siren']} | SIRET : {COMPANY['siret']}", 0, 1, "C")
        self.cell(0, 3.5, f"TVA Intracommunautaire : {COMPANY['tva']} | Email : {COMPANY['email']}", 0, 1, "C")
        self.cell(0, 3.5, f"Page {self.page_no()}/{{nb}}", 0, 0, "C")


def gen_pdf(client_name, client_addr, computed_lines, inv_num, inv_date_str, client_siret="", client_tva="", ticket_totaux=None):
    pdf = InvoicePDF(client_name, client_addr, inv_num, inv_date_str)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=30)

    y = pdf.get_y()

    # Emitter
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(255, 140, 50)
    pdf.cell(90, 5, "EMETTEUR", 0, 1)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(70, 70, 90)
    for info in [COMPANY["name"], f"SIREN : {COMPANY['siren']}", f"SIRET : {COMPANY['siret']}", f"TVA : {COMPANY['tva']}", f"Email : {COMPANY['email']}"]:
        pdf.cell(90, 4.5, info, 0, 1)
    y_after = pdf.get_y()

    # Client
    pdf.set_xy(120, y)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(255, 140, 50)
    pdf.cell(75, 5, "CLIENT", 0, 1)
    pdf.set_x(120)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(26, 26, 46)
    pdf.cell(75, 5, client_name, 0, 1)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(70, 70, 90)
    for al in client_addr.split("\n"):
        pdf.set_x(120)
        pdf.cell(75, 4.5, al.strip(), 0, 1)
    if client_siret.strip():
        pdf.set_x(120)
        pdf.cell(75, 4.5, f"SIRET : {client_siret.strip()}", 0, 1)
    if client_tva.strip():
        pdf.set_x(120)
        pdf.cell(75, 4.5, f"TVA : {client_tva.strip()}", 0, 1)

    pdf.set_y(max(y_after, pdf.get_y()) + 8)

    # Table
    cw = [58, 14, 24, 16, 24, 22, 24]
    headers = ["Description", "Qte", "PU HT", "TVA", "PU TTC", "Total HT", "Total TTC"]
    pdf.set_fill_color(26, 26, 46)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 7.5)
    for i, h in enumerate(headers):
        pdf.cell(cw[i], 7.5, h, 1, 0, "C", True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 7.5)
    fill = False
    for ln in computed_lines:
        if fill:
            pdf.set_fill_color(248, 248, 253)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(50, 50, 70)
        pdf.cell(cw[0], 6.5, str(ln["desc"])[:38], 1, 0, "L", True)
        pdf.cell(cw[1], 6.5, str(ln["qty"]), 1, 0, "C", True)
        pdf.cell(cw[2], 6.5, f'{ln["pu_ht"]:.2f}', 1, 0, "R", True)
        pdf.cell(cw[3], 6.5, f'{ln["tva"]:.1f}%', 1, 0, "C", True)
        pdf.cell(cw[4], 6.5, f'{ln["pu_ttc"]:.2f}', 1, 0, "R", True)
        pdf.cell(cw[5], 6.5, f'{ln["tot_ht"]:.2f}', 1, 0, "R", True)
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(255, 107, 26)
        pdf.cell(cw[6], 6.5, f'{ln["tot_ttc"]:.2f}', 1, 0, "R", True)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.ln()
        fill = not fill

    pdf.ln(5)
    if pdf.get_y() > 240:
        pdf.add_page()
        pdf.ln(10)

    # Use ticket totals if available (PRIORITAIRE — inclut cotis. securite sociale Metro)
    if ticket_totaux and ticket_totaux.get("total_ttc"):
        total_ttc = float(ticket_totaux["total_ttc"])
        total_ht = float(ticket_totaux.get("total_ht") or (total_ttc / 1.2))
        total_tva = round(total_ttc - total_ht, 2)
        if ticket_totaux.get("total_tva"):
            total_tva = float(ticket_totaux["total_tva"])
            total_ht = round(total_ttc - total_tva, 2)
    else:
        # Fallback: calculate from lines using TVA group method
        tva_groups = defaultdict(float)
        for l in computed_lines:
            tva_groups[l["tva"]] += l["tot_ht"]
        total_ht = round(sum(tva_groups.values()), 2)
        total_tva = 0.0
        total_ttc = 0.0
        for tva_rate, group_ht in tva_groups.items():
            group_ht_r = round(group_ht, 2)
            group_tva = round(group_ht_r * tva_rate / 100, 2)
            total_tva += group_tva
            total_ttc += group_ht_r + group_tva
        total_tva = round(total_tva, 2)
        total_ttc = round(total_ttc, 2)

    xL, xV = 133, 178

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(70, 70, 90)
    pdf.set_x(xL)
    pdf.cell(30, 6, "Total HT :", 0, 0, "R")
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(30, 6, f"{total_ht:.2f} EUR", 0, 1, "R")

    # TVA detail — use ticket ventilation if available
    if ticket_totaux and ticket_totaux.get("ventilation_tva"):
        for vt in ticket_totaux["ventilation_tva"]:
            taux = vt.get("taux", 20.0)
            mt = vt.get("montant_tva", 0)
            if mt and float(mt) > 0:
                pdf.set_font("Helvetica", "", 8)
                pdf.set_x(xL)
                pdf.cell(30, 5, f"  dont TVA {taux}% :", 0, 0, "R")
                pdf.cell(30, 5, f"{float(mt):.2f} EUR", 0, 1, "R")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_x(xL)
    pdf.cell(30, 6, "Total TVA :", 0, 0, "R")
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(30, 6, f"{total_tva:.2f} EUR", 0, 1, "R")

    # TTC box
    pdf.ln(2)
    y_ttc = pdf.get_y()
    pdf.set_fill_color(255, 140, 50)
    pdf.rect(xL - 3, y_ttc - 1, 70, 11, "F")
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(xL, y_ttc)
    pdf.cell(30, 9, "TOTAL TTC :", 0, 0, "R")
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(35, 9, f"{total_ttc:.2f} EUR", 0, 1, "R")

    pdf.ln(14)
    pdf.set_font("Helvetica", "I", 7.5)
    pdf.set_text_color(120, 120, 140)
    pdf.cell(0, 4.5, "Conditions de paiement : Paiement comptant.", 0, 1, "L")
    pdf.cell(0, 4.5, "En cas de retard, une indemnite forfaitaire de 40 EUR sera appliquee.", 0, 1, "L")

    return bytes(pdf.output())


# ═══════════════════════════════════════
# UI
# ═══════════════════════════════════════

# Banner
if BANNER_B64:
    st.markdown(f"""
    <div class="banner">
        <img src="data:image/png;base64,{BANNER_B64}" alt="Smart Exchange">
        <div class="banner-ov">
            <div>
                <div class="b-title">SMART <span>EXCHANGE</span></div>
                <div class="b-sub">Systeme de Facturation Pro v3.0</div>
            </div>
        </div>
        <div class="b-line"></div>
    </div>
    """, unsafe_allow_html=True)

# ── Client ──
st.markdown('<div class="sec"><div class="sec-h">👤 Client</div>', unsafe_allow_html=True)

for field in ["client_name", "client_addr", "client_siret", "client_tva"]:
    if field not in st.session_state:
        st.session_state[field] = ""

saved_clients = list(st.session_state.clients.keys())
sel_col, btn_col = st.columns([3, 1])
with sel_col:
    selected = st.selectbox("📂 Client enregistre", ["— Nouveau client —"] + saved_clients, key="client_selector")
with btn_col:
    st.markdown("<br>", unsafe_allow_html=True)
    if selected != "— Nouveau client —":
        if st.button("🗑️ Supprimer", key="del_client"):
            if selected in st.session_state.clients:
                del st.session_state.clients[selected]
                save_clients(st.session_state.clients)
                st.rerun()

if selected != "— Nouveau client —" and selected in st.session_state.clients:
    cdata = st.session_state.clients[selected]
    if isinstance(cdata, dict):
        st.session_state["client_name"] = selected
        st.session_state["client_addr"] = cdata.get("addr", "")
        st.session_state["client_siret"] = cdata.get("siret", "")
        st.session_state["client_tva"] = cdata.get("tva", "")

c1, c2 = st.columns(2)
with c1:
    client_name = st.text_input("Nom / Raison sociale", value=st.session_state["client_name"], placeholder="Ex: RAF MARKET", key="cn_input")
with c2:
    client_addr = st.text_area("Adresse", value=st.session_state["client_addr"], placeholder="196 avenue du Maine\n75014 Paris", height=75, key="ca_input")

c3, c4 = st.columns(2)
with c3:
    client_siret = st.text_input("SIRET client", value=st.session_state["client_siret"], placeholder="990 314 007 00016", key="cs_input")
with c4:
    client_tva = st.text_input("N° TVA client", value=st.session_state["client_tva"], placeholder="FR37990314007", key="ct_input")

if st.button("💾 Sauvegarder ce client", use_container_width=True):
    if client_name.strip():
        st.session_state.clients[client_name.strip()] = {
            "addr": client_addr, "siret": client_siret, "tva": client_tva,
        }
        save_clients(st.session_state.clients)
        st.success(f"✅ {client_name} sauvegarde !")
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ── Facture details ──
st.markdown('<div class="sec"><div class="sec-h">📋 Facture</div>', unsafe_allow_html=True)
d1, d2, d3 = st.columns(3)
with d1:
    inv_num = st.text_input("N° Facture", value=f"SE-{datetime.now().strftime('%Y%m%d')}-001")
with d2:
    inv_date = st.date_input("Date", value=date.today())
with d3:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<span class="badge">TVA : {COMPANY["tva"]}</span>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Lines ──
st.markdown('<div class="sec"><div class="sec-h">⚡ Articles & Prestations</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📷 Scan & Refacturation", "✏️ Saisie Manuelle"])

with tab2:
    if st.button("➕ Ajouter une ligne", key="add"):
        add_line()

    for idx, line in enumerate(st.session_state.lines):
        cols = st.columns([3, 0.8, 1.2, 0.6, 0.6, 0.3])
        with cols[0]:
            line["desc"] = st.text_input("Desc", value=line["desc"], key=f"d{line['id']}", label_visibility="collapsed", placeholder="Description")
        with cols[1]:
            new_qty = st.number_input("Qte", value=line["qty"], min_value=1, step=1, key=f"q{line['id']}", label_visibility="collapsed")
            if new_qty != line["qty"]:
                line["tot_ttc_override"] = None
            line["qty"] = new_qty
        with cols[2]:
            new_pu = st.number_input("PU HT", value=line["pu_ht"], min_value=0.0, step=0.01, format="%.2f", key=f"p{line['id']}", label_visibility="collapsed")
            if abs(new_pu - line["pu_ht"]) > 0.001:
                line["tot_ttc_override"] = None
            line["pu_ht"] = new_pu
        with cols[3]:
            current_tva = line.get("tva", 20.0)
            tva_color = "#26de81" if current_tva == 5.5 else "#FF8C32" if current_tva == 20.0 else "#54a0ff"
            st.markdown(f"<div style='text-align:center;font-weight:700;color:{tva_color};padding:6px 0;font-size:.85rem'>{current_tva}%</div>", unsafe_allow_html=True)
        with cols[4]:
            if st.button("TVA", key=f"ctva{line['id']}"):
                tva_cycle = {20.0: 5.5, 5.5: 10.0, 10.0: 2.1, 2.1: 0.0, 0.0: 20.0}
                line["tva"] = tva_cycle.get(current_tva, 20.0)
                line["tot_ttc_override"] = None
                st.rerun()
        with cols[5]:
            if st.button("🗑️", key=f"x{line['id']}"):
                del_line(line["id"])
                st.rerun()

    if st.session_state.lines:
        computed = [compute(l) for l in st.session_state.lines]
        df = pd.DataFrame([{
            "Description": l["desc"] or "—",
            "Qte": l["qty"],
            "PU HT": f'{l["pu_ht"]:.2f} €',
            "TVA": f'{l["tva"]}%',
            "PU TTC": f'{l["pu_ttc"]:.2f} €',
            "Total HT": f'{l["tot_ht"]:.2f} €',
            "Total TTC": f'{l["tot_ttc"]:.2f} €',
        } for l in computed])
        st.dataframe(df, use_container_width=True, hide_index=True)

with tab1:
    st.markdown("**📎 Scannez votre facture fournisseur (Metro, Carrefour, etc.)**")
    st.caption("v3.0 — L'IA extrait les lignes brutes, Python fait tous les calculs = zero erreur")

    # API Key check
    has_key = False
    try:
        if st.secrets.get("ANTHROPIC_API_KEY", ""):
            has_key = True
    except:
        pass
    if not has_key and os.environ.get("ANTHROPIC_API_KEY", ""):
        has_key = True
    if not has_key and st.session_state.get("anthropic_key", ""):
        has_key = True

    if not has_key:
        st.markdown("""
        <div style="background:rgba(255,140,50,0.08);border:1px solid rgba(255,160,50,0.3);border-radius:12px;padding:12px 16px;margin-bottom:10px">
            <b style="color:#FF8C32">🔑 Cle API requise</b><br>
            <span style="font-size:.82rem;color:rgba(255,255,255,0.6)">
                Mettez votre cle dans <b>Settings → Secrets</b> :<br>
                <code>ANTHROPIC_API_KEY = "sk-ant-api03-..."</code>
            </span>
        </div>
        """, unsafe_allow_html=True)
        api_key_input = st.text_input("🔑 Cle API (temporaire)", type="password", key="anthropic_key_input", placeholder="sk-ant-api03-...")
        if api_key_input:
            st.session_state["anthropic_key"] = api_key_input
            has_key = True
            st.rerun()
    else:
        st.markdown("<span style='color:#26de81;font-size:.8rem;font-weight:700'>✅ Cle API detectee — scan pret</span>", unsafe_allow_html=True)

    uploaded = st.file_uploader("Glissez votre facture ici", type=["png", "jpg", "jpeg", "pdf"], key="scan")

    if uploaded:
        sc_l, sc_r = st.columns([1.2, 1])

        with sc_l:
            if uploaded.type.startswith("image"):
                st.image(uploaded, caption="📄 Facture fournisseur", use_container_width=True)
            elif uploaded.type == "application/pdf":
                st.info(f"📄 **{uploaded.name}** ({uploaded.size // 1024} Ko)")

            if has_key:
                if st.button("🤖 SCANNER TOUTE LA FACTURE", type="primary", use_container_width=True, key="scan_btn"):
                    with st.spinner("L'IA extrait les lignes brutes..."):
                        uploaded.seek(0)
                        raw_data, err = scan_invoice_v3(uploaded.read(), uploaded.type)
                        if err:
                            st.error(f"❌ {err}")
                        elif raw_data:
                            # Store raw for debug
                            st.session_state["raw_scan"] = raw_data
                            # Python processes everything
                            articles, totaux = process_raw_scan(raw_data)
                            if articles:
                                st.session_state["scan_articles"] = articles
                                st.session_state["scan_totaux"] = totaux
                                st.session_state["scan_added"] = False
                                
                                # Show results
                                calc_ht = round(sum(a["total_ht"] for a in articles), 2)
                                calc_ttc = round(sum(a["total_ttc"] for a in articles), 2)
                                ticket_ttc = totaux.get("total_ttc") or 0
                                ticket_ht = totaux.get("total_ht") or 0
                                
                                st.success(f"✅ {len(articles)} articles extraits")
                                
                                # Compare with ticket totals
                                if ticket_ttc:
                                    diff_ttc = abs(calc_ttc - ticket_ttc)
                                    if diff_ttc < 1.0:
                                        st.success(f"✅ TTC ticket: {ticket_ttc:.2f}€ — Calcule: {calc_ttc:.2f}€ — Ecart: {diff_ttc:.2f}€")
                                    elif diff_ttc < 10:
                                        st.warning(f"⚠️ TTC ticket: {ticket_ttc:.2f}€ — Calcule: {calc_ttc:.2f}€ — Ecart: {diff_ttc:.2f}€")
                                    else:
                                        st.error(f"❌ TTC ticket: {ticket_ttc:.2f}€ — Calcule: {calc_ttc:.2f}€ — Ecart: {diff_ttc:.2f}€")
                                if ticket_ht:
                                    diff_ht = abs(calc_ht - ticket_ht)
                                    if diff_ht < 1.0:
                                        st.success(f"✅ HT ticket: {ticket_ht:.2f}€ — Calcule: {calc_ht:.2f}€ — Ecart: {diff_ht:.2f}€")
                                    elif diff_ht < 10:
                                        st.warning(f"⚠️ HT ticket: {ticket_ht:.2f}€ — Calcule: {calc_ht:.2f}€ — Ecart: {diff_ht:.2f}€")
                                
                                st.rerun()
                            else:
                                st.warning("Aucun article detecte")

        with sc_r:
            st.markdown("**🔄 Articles extraits**")

            if "scan_articles" in st.session_state and st.session_state["scan_articles"]:
                articles = st.session_state["scan_articles"]
                totaux = st.session_state.get("scan_totaux", {})
                
                # Show articles table
                calc_ttc = round(sum(a["total_ttc"] for a in articles), 2)
                calc_ht = round(sum(a["total_ht"] for a in articles), 2)
                
                # Prefer ticket totals if available
                disp_ht = totaux.get("total_ht") or calc_ht
                disp_ttc = totaux.get("total_ttc") or calc_ttc
                
                st.caption(f"{len(articles)} articles — HT: {disp_ht:.2f}€ — TTC: {disp_ttc:.2f}€")
                
                # Editable scan lines
                if "scan_lines" not in st.session_state:
                    st.session_state.scan_lines = []
                
                # Init from scan
                if not st.session_state.scan_lines or st.session_state.get("scan_refresh"):
                    st.session_state.scan_lines = []
                    st.session_state["scan_refresh"] = False
                    for i, a in enumerate(articles):
                        st.session_state.scan_lines.append({
                            "id": i,
                            "desc": a["desc"],
                            "qty": a["qte"],
                            "ttc": a["total_ttc"],
                            "tva": a["tva"],
                        })

                scan_results = []
                for idx, sl in enumerate(st.session_state.scan_lines):
                    sid = sl["id"]
                    st.markdown(f"<div style='background:rgba(255,140,50,0.05);border:1px solid rgba(255,160,50,0.2);border-radius:10px;padding:3px 8px;margin-bottom:2px'><b style='color:#FF8C32;font-size:.7rem'>Art. {idx+1}</b></div>", unsafe_allow_html=True)
                    
                    sc_desc = st.text_input("Desc", value=sl.get("desc", ""), key=f"sd{sid}", label_visibility="collapsed")
                    c1, c2, c3, c4 = st.columns([1, 0.6, 0.4, 1])
                    with c1:
                        sc_qty = st.number_input("Qte", value=sl.get("qty", 1), min_value=1, step=1, key=f"sq{sid}")
                    with c2:
                        sc_tva = float(sl.get("tva", 20.0))
                        tva_color = "#26de81" if sc_tva == 5.5 else "#FF8C32"
                        st.markdown(f"<div style='text-align:center;font-weight:700;color:{tva_color};padding:8px 0;font-size:.82rem'>{sc_tva}%</div>", unsafe_allow_html=True)
                    with c3:
                        if st.button("↻", key=f"ctva_s{sid}"):
                            tva_cycle = {20.0: 5.5, 5.5: 10.0, 10.0: 2.1, 2.1: 0.0, 0.0: 20.0}
                            sl["tva"] = tva_cycle.get(sc_tva, 20.0)
                            st.rerun()
                    with c4:
                        sc_ttc = st.number_input("Total TTC", value=float(sl.get("ttc", 0.0)), min_value=-999.0, step=0.01, format="%.2f", key=f"sp{sid}")

                    if sc_qty > 0 and sc_ttc != 0:
                        tot_ht_s = ht_from_ttc(sc_ttc, sc_tva)
                        pu_ht_s = round(tot_ht_s / sc_qty, 2)
                        pu_ttc_s = round(sc_ttc / sc_qty, 2)
                        st.markdown(f"<span style='color:#26de81;font-size:.72rem;font-weight:700'>→ PU TTC: {pu_ttc_s:.2f}€ | PU HT: {pu_ht_s:.2f}€ | Tot HT: {tot_ht_s:.2f}€</span>", unsafe_allow_html=True)
                        scan_results.append({
                            "desc": sc_desc or "Article",
                            "qty": sc_qty,
                            "pu_ht": pu_ht_s,
                            "tot_ht": tot_ht_s,
                            "tot_ttc": sc_ttc,
                            "tva": sc_tva,
                        })

                st.markdown("---")
                if scan_results:
                    already_added = st.session_state.get("scan_added", False)
                    if already_added:
                        st.success("✅ Articles ajoutes a la facture !")
                        if st.button("🗑️ Effacer le scan", key="clear_scan", use_container_width=True):
                            st.session_state.scan_lines = []
                            st.session_state["scan_articles"] = []
                            st.session_state["scan_totaux"] = {}
                            st.session_state["scan_added"] = False
                            st.rerun()
                    else:
                        if st.button(f"📥 AJOUTER {len(scan_results)} ARTICLES", type="primary", key="add_all_scan", use_container_width=True):
                            for sr in scan_results:
                                add_line(desc=sr["desc"], qty=sr["qty"], pu_ht=sr["pu_ht"], tva=sr["tva"], tot_ttc_override=sr["tot_ttc"])
                            st.session_state["scan_added"] = True
                            st.success(f"✅ {len(scan_results)} articles ajoutes !")
                            st.rerun()
                
                # Debug
                with st.expander("🔍 Debug: lignes brutes Claude", expanded=False):
                    raw = st.session_state.get("raw_scan", {})
                    st.json(raw)

            else:
                st.info("Cliquez sur 'Scanner toute la facture'")
    else:
        st.markdown("""
        <div style="border:2px dashed rgba(255,160,50,0.3);border-radius:16px;padding:2rem;text-align:center;background:rgba(255,140,50,0.02)">
            <div style="font-size:2.5rem;margin-bottom:0.5rem">📸</div>
            <div style="color:rgba(255,255,255,0.6);font-weight:600;font-size:0.9rem">Uploadez votre facture fournisseur</div>
            <div style="color:rgba(255,255,255,0.3);font-size:0.75rem;margin-top:4px">
                Metro, Carrefour, Promocash...<br>
                L'IA extrait les lignes brutes, Python calcule tout = zero erreur
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Totals ──
all_comp = [compute(l) for l in st.session_state.lines]

tva_groups = defaultdict(float)
for l in all_comp:
    tva_groups[l["tva"]] += l["tot_ht"]

g_ht = round(sum(tva_groups.values()), 2)
g_tva = 0.0
g_ttc = 0.0
for tva_rate, group_ht in tva_groups.items():
    group_ht_r = round(group_ht, 2)
    group_tva = round(group_ht_r * tva_rate / 100, 2)
    g_tva += group_tva
    g_ttc += group_ht_r + group_tva
g_tva = round(g_tva, 2)
g_ttc = round(g_ttc, 2)

st.markdown('<div class="sec"><div class="sec-h">💰 Totaux</div>', unsafe_allow_html=True)
t1, t2, t3 = st.columns([1, 1, 1.3])
with t1:
    st.markdown(f'<div class="tot-box tot-ht"><div class="lbl">Total HT</div><div class="val">{fmt(g_ht)}</div></div>', unsafe_allow_html=True)
with t2:
    st.markdown(f'<div class="tot-box tot-tva"><div class="lbl">Total TVA</div><div class="val">{fmt(g_tva)}</div></div>', unsafe_allow_html=True)
with t3:
    st.markdown(f'<div class="tot-box tot-ttc"><div class="lbl">Total TTC</div><div class="val">{fmt(g_ttc)}</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── PDF Export ──
st.markdown('<div class="sec"><div class="sec-h">🚀 Export</div>', unsafe_allow_html=True)
can_gen = len(st.session_state.lines) > 0 and client_name.strip() != ""
if not can_gen:
    st.info("Renseignez le client et ajoutez au moins une ligne.")

def reset_after_download():
    st.session_state.lines = []
    st.session_state.lid = 0
    st.session_state.scan_lines = []
    st.session_state["scan_articles"] = []
    st.session_state["scan_totaux"] = {}
    st.session_state["scan_added"] = False
    st.session_state["pdf_ready"] = None

if st.button("🚀 GENERER LA FACTURE PDF", disabled=not can_gen, type="primary", use_container_width=True):
    with st.spinner("Generation..."):
        # Use ticket totaux if from scan
        ticket_totaux = st.session_state.get("scan_totaux", None)
        pdf_bytes = gen_pdf(
            client_name.strip(),
            client_addr.strip(),
            all_comp,
            inv_num,
            inv_date.strftime("%d/%m/%Y"),
            client_siret=client_siret.strip() if client_siret else "",
            client_tva=client_tva.strip() if client_tva else "",
            ticket_totaux=ticket_totaux,
        )
        safe = client_name.strip().replace(" ", "_")[:20]
        fname = f"Facture_{inv_num}_{safe}.pdf"
        st.session_state["pdf_ready"] = pdf_bytes
        st.session_state["pdf_fname"] = fname
        st.success("✅ Facture generee !")

if st.session_state.get("pdf_ready"):
    st.download_button(
        "📥 Telecharger le PDF",
        data=st.session_state["pdf_ready"],
        file_name=st.session_state.get("pdf_fname", "facture.pdf"),
        mime="application/pdf",
        use_container_width=True,
        on_click=reset_after_download
    )

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
st.markdown(f'<div class="foot">{COMPANY["name"]} · SIREN {COMPANY["siren"]} · TVA {COMPANY["tva"]}<br>{COMPANY["email"]} · v3.0 Zero-Error</div>', unsafe_allow_html=True)

import json
import re
import os

import streamlit as st
from PIL import Image
from google import genai
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# API KEY — pulled from .env (GEMINI_APIKEY=...). Never hardcode it in source.
# ---------------------------------------------------------------------------
API_KEY = os.getenv("GEMINI_APIKEY")
MODEL = "gemini-2.5-flash"  # update to whichever Gemini vision model you have access to

# ---------------------------------------------------------------------------
# GRADING PROMPT
# Includes an is_onion validation gate so non-onion images are rejected
# instead of silently graded.
# ---------------------------------------------------------------------------
GRADING_PROMPT = """
You are ONION GRADE AI, a visual quality assessment system for onions,
calibrated to align with Indian government onion grading standards —
AGMARK (Directorate of Marketing & Inspection, Ministry of Agriculture)
and the ICAR-DOGR size classification system.

STEP 1 — VALIDATION (do this first, before any grading):
Check whether the image actually shows one or more onions (whole bulb
onions, with or without skin/leaves attached). It must NOT be a
different vegetable, a cut/processed onion dish, a random object, a
person, text, or an unclear/blank image.

If the image does NOT clearly show onion(s), respond with ONLY this
JSON object and nothing else:
{
  "is_onion": false,
  "detected_subject": "<brief description of what the image actually shows>",
  "message": "<one short, friendly sentence telling the user to upload a clear photo of an onion instead>"
}

STEP 2 — GRADING (only if the image clearly shows onion(s)):
Analyze the onion(s) and evaluate the following parameters, each on a
0-100 scale:

1. size - Score against the ICAR-DOGR size classification:
   - Grade A: bulb diameter > 80mm (large)
   - Grade B: bulb diameter 50-80mm (medium — preferred for domestic
     market and most export orders)
   - Grade C: bulb diameter 30-50mm (small)
   - Below 30mm or highly irregular sizing within the same lot should
     score low, as uniformity within a batch is itself a grading factor.
   - Note: government procurement (NAFED) treats 35-70mm as the
     practically acceptable market range — bulbs far outside this band
     should score lower even if botanically healthy.

2. color - Uniformity and natural healthy coloration for the variety
   (e.g. deep red/pink for red onion varieties, coppery-brown for
   yellow varieties). Discoloration, greenish necks, or patchy fading
   should reduce the score.

3. shape - Roundness/regularity typical of the variety, free from
   forking, doubling, or bolting-induced deformation.

4. surface_condition - Skin condition and dryness (well-cured, tight
   outer skin is preferred per AGMARK appearance criteria), absence of
   sprouting, and absence of discoloration/blemishes on the skin.

5. defects_damage - Cuts, bruises, rot, mold, pest damage, or visible
   decay. AGMARK certification requires freedom from disease and
   damage — this parameter should be scored strictly, as decay and rot
   are typically zero-tolerance disqualifiers in Indian grading
   practice, not minor deductions.

Weight the parameters as follows to compute the overall quality score
(weights sum to 100):
- size: 20%
- color: 15%
- shape: 15%
- surface_condition: 25%
- defects_damage: 25%

Map the overall score to a grade:
- A: 85-100 (Premium / AGMARK Special-Grade equivalent)
- B: 65-84 (Standard / AGMARK Standard-Grade equivalent)
- C: below 65 (Below standard — flag for review/rejection)

Respond with ONLY a valid JSON object (no markdown fences, no extra
text) in exactly this shape:

{
  "is_onion": true,
  "parameters": {
    "size": {"score": <int 0-100>, "size_band": "<A|B|C|Below C>", "notes": "<short observation>"},
    "color": {"score": <int 0-100>, "notes": "<short observation>"},
    "shape": {"score": <int 0-100>, "notes": "<short observation>"},
    "surface_condition": {"score": <int 0-100>, "notes": "<short observation>"},
    "defects_damage": {"score": <int 0-100>, "notes": "<short observation>"}
  },
  "overall_score": <int 0-100>,
  "grade": "<A|B|C>",
  "agmark_equivalent": "<Special Grade|Standard Grade|General Grade|Below Standard>",
  "summary": "<2-3 sentence overall assessment>"
}
"""


def extract_json(text: str) -> dict:
    """Pull the JSON object out of the model's response, tolerating stray text/fences."""
    cleaned = text.strip().strip("`")
    cleaned = re.sub(r"^json", "", cleaned, flags=re.IGNORECASE).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model response.")
    return json.loads(match.group(0))


# ---------------------------------------------------------------------------
# THEME — matched to the "How's My Onion?" dashboard (magenta/plum on soft
# lavender, rounded white cards, friendly stat tiles).
# ---------------------------------------------------------------------------
PLUM = "#7A2C56"
PLUM_DARK = "#5E2143"
MAGENTA = "#8B2F6B"
BG = "#FBF3F8"
CARD_BG = "#FFFFFF"
INK = "#2B2130"
INK_MUTED = "#7A6E77"
GREEN = "#2E9E5B"
GREEN_BG = "#E8F7EE"
LILAC_BG = "#F3E6EF"
RED_BG = "#FDEDEC"
RED = "#C0392B"

st.set_page_config(page_title="How's My Onion? — ONION GRADE AI", page_icon="🧅", layout="wide")

st.markdown(
    f"""
    <style>
        html, body, [class*="css"] {{
            font-family: 'Poppins', 'Segoe UI', sans-serif;
        }}
        .stApp {{
            background-color: {BG};
        }}
        h1, h2, h3 {{
            color: {INK};
        }}
        div[data-testid="stFileUploader"] section {{
            background-color: {CARD_BG};
            border: 2px dashed {MAGENTA}55;
            border-radius: 16px;
        }}
        .stButton > button {{
            background-color: {MAGENTA};
            color: white;
            border-radius: 12px;
            border: none;
            padding: 0.6rem 1.6rem;
            font-weight: 600;
            font-size: 1rem;
        }}
        .stButton > button:hover {{
            background-color: {PLUM_DARK};
            color: white;
        }}
        .onion-hero {{
            background: linear-gradient(135deg, {LILAC_BG} 0%, {BG} 100%);
            border-radius: 20px;
            padding: 1.8rem 2rem;
            margin-bottom: 1.2rem;
        }}
        .onion-kicker {{
            color: {MAGENTA};
            font-weight: 700;
            font-size: 0.78rem;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }}
        .stat-card {{
            background-color: {CARD_BG};
            border-radius: 16px;
            padding: 1.1rem 1.3rem;
            box-shadow: 0 2px 10px rgba(122, 44, 86, 0.08);
            text-align: left;
        }}
        .stat-icon {{
            width: 42px; height: 42px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.3rem; margin-bottom: 0.5rem;
        }}
        .stat-label {{ color: {INK_MUTED}; font-size: 0.85rem; margin-bottom: 0.15rem; }}
        .stat-value {{ color: {INK}; font-size: 1.7rem; font-weight: 700; }}
        .stat-note {{ color: {INK_MUTED}; font-size: 0.78rem; margin-top: 0.2rem; }}
        .grade-pill {{
            display: inline-block; border-radius: 999px; padding: 0.35rem 1.1rem;
            font-weight: 700; font-size: 1.1rem; color: white;
        }}
        .error-card {{
            background-color: {RED_BG};
            border-radius: 16px;
            padding: 1.4rem 1.6rem;
            border-left: 5px solid {RED};
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


def stat_card(col, icon, icon_bg, label, value, note=""):
    with col:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-icon" style="background-color:{icon_bg};">{icon}</div>
                <div class="stat-label">{label}</div>
                <div class="stat-value">{value}</div>
                <div class="stat-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def grade_color(grade: str) -> str:
    return {"A": GREEN, "B": "#D68910", "C": RED}.get(grade, INK_MUTED)


def render_result(result: dict):
    grade = result.get("grade", "?")
    st.markdown(
        f"""
        <div class="onion-hero">
            <div class="onion-kicker">ONION QUALITY CHECK — RESULT</div>
            <h2 style="margin:0.3rem 0 0.2rem 0;">
                Grade <span class="grade-pill" style="background-color:{grade_color(grade)};">{grade}</span>
                &nbsp;·&nbsp; {result.get('overall_score', '?')}/100
            </h2>
            <div style="color:{INK_MUTED};">AGMARK equivalent: <b>{result.get('agmark_equivalent', 'N/A')}</b></div>
            <p style="margin-top:0.8rem; color:{INK};">{result.get('summary', '')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Parameter breakdown")
    params = result.get("parameters", {})
    icons = {"size": "📏", "color": "🎨", "shape": "⚪", "surface_condition": "🧴", "defects_damage": "🩹"}
    icon_bgs = {"size": LILAC_BG, "color": LILAC_BG, "shape": LILAC_BG, "surface_condition": GREEN_BG, "defects_damage": RED_BG}
    cols = st.columns(len(params) if params else 1)
    for col, (name, data) in zip(cols, params.items()):
        label = name.replace("_", " ").title()
        note = data.get("notes", "")
        band = f" (Band {data.get('size_band')})" if name == "size" and data.get("size_band") else ""
        stat_card(col, icons.get(name, "🧅"), icon_bgs.get(name, LILAC_BG), label + band, f"{data.get('score', '?')}/100", note)


def render_not_onion(result: dict):
    st.markdown(
        f"""
        <div class="error-card">
            <b>⚠️ This doesn't look like an onion.</b><br/>
            {result.get('message', "Please upload a clear photo of an onion.")}<br/>
            <span style="color:{INK_MUTED}; font-size:0.85rem;">
                Detected instead: {result.get('detected_subject', 'unknown subject')}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div style="display:flex; align-items:center; gap:0.7rem; margin-bottom:0.2rem;">
        <div style="font-size:2rem;">🧅</div>
        <div>
            <div style="font-size:1.5rem; font-weight:700; line-height:1.1;">How's My Onion?</div>
            <div style="color:#7A6E77; font-size:0.85rem;">Onion Quality Check — powered by AI</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")

image_path = st.file_uploader("Upload a photo of your onion", type=["png", "jpg", "jpeg"])
extra_notes = st.text_input("Optional: add context (e.g. variety, storage duration)", value="")

if image_path is not None:
    image = Image.open(image_path)
    st.image(image, caption="Uploaded image", use_container_width=False, width=320)

    if st.button("Check My Onion  →"):
        if not API_KEY:
            st.error("Missing GEMINI_APIKEY — set it in your .env file.")
        else:
            with st.spinner("Analyzing size, color, shape, surface condition, and defects..."):
                try:
                    client = genai.Client(api_key=API_KEY)
                    prompt = GRADING_PROMPT
                    if extra_notes:
                        prompt += f"\n\nAdditional context from user: {extra_notes}"

                    response = client.models.generate_content(
                        model=MODEL,
                        contents=[image, prompt],
                    )
                    result = extract_json(response.text)

                    if not result.get("is_onion", False):
                        render_not_onion(result)
                    else:
                        render_result(result)

                    with st.expander("Raw model output"):
                        st.code(response.text)
                except Exception as e:
                    st.error(f"Grading failed: {e}")
else:
    st.info("Upload an image to begin.")
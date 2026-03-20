"""
AI Learning Lab — Module 1: Organisatie & Omgeving
Kwaliteitscyclus Web App — Visueel Redesign
"""

import streamlit as st
import json
import csv
from datetime import datetime
# Cloud version - no local file paths

# --- Config (Cloud) ---
# Data stored in session_state (no local filesystem)
if "zelfinschattingen" not in st.session_state:
    st.session_state["zelfinschattingen"] = []
if "docentbeoordelingen" not in st.session_state:
    st.session_state["docentbeoordelingen"] = []

st.set_page_config(
    page_title="AI Learning Lab — Module 1",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

    /* Global */
    .block-container { padding-top: 1.5rem; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Headers */
    .main-header {
        font-size: 2.2rem; font-weight: 900; color: #c00000;
        margin-bottom: 0.2rem; letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 1.15rem; color: #666; margin-bottom: 1.5rem;
        border-bottom: 3px solid #c00000; padding-bottom: 0.8rem;
    }

    /* Step cards on Start page */
    .step-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 2px solid #e0e0e0; border-radius: 16px;
        padding: 1.5rem; margin: 0.5rem 0; text-align: center;
        transition: all 0.3s ease; min-height: 260px;
    }
    .step-card:hover { border-color: #c00000; transform: translateY(-2px); box-shadow: 0 8px 25px rgba(192,0,0,0.1); }
    .step-icon { font-size: 3rem; margin-bottom: 0.5rem; }
    .step-number {
        display: inline-block; background: #c00000; color: white;
        width: 32px; height: 32px; border-radius: 50%; line-height: 32px;
        font-weight: 900; font-size: 0.9rem; margin-bottom: 0.5rem;
    }
    .step-title { font-size: 1.2rem; font-weight: 700; color: #1a1a1a; margin: 0.5rem 0; }
    .step-desc { font-size: 0.9rem; color: #666; line-height: 1.5; }
    .step-output {
        background: #e8f5e9; border-radius: 8px; padding: 0.5rem 0.8rem;
        margin-top: 0.8rem; font-size: 0.82rem; color: #2e7d32;
    }

    /* Tool cards */
    .tool-card {
        background: white; border: 2px solid #e0e0e0; border-radius: 14px;
        padding: 1.3rem; margin: 0.5rem 0; transition: all 0.2s;
    }
    .tool-card:hover { border-color: #c00000; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }
    .tool-card-blue { border-left: 5px solid #1565c0; }
    .tool-card-green { border-left: 5px solid #2e7d32; }
    .tool-card-orange { border-left: 5px solid #e65100; }
    .tool-card-purple { border-left: 5px solid #6a1b9a; }
    .tool-card-red { border-left: 5px solid #c00000; }
    .tool-title { font-size: 1.05rem; font-weight: 700; color: #1a1a1a; margin-bottom: 0.3rem; }
    .tool-subtitle { font-size: 0.85rem; color: #888; margin-bottom: 0.6rem; }

    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-radius: 12px; padding: 1rem 1.2rem; margin: 0.8rem 0;
    }
    .info-box-green {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-radius: 12px; padding: 1rem 1.2rem; margin: 0.8rem 0;
    }
    .info-box-orange {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-radius: 12px; padding: 1rem 1.2rem; margin: 0.8rem 0;
    }
    .info-box-red {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border-radius: 12px; padding: 1rem 1.2rem; margin: 0.8rem 0;
    }

    /* Badges */
    .ko-badge {
        background: #c00000; color: white; padding: 3px 10px;
        border-radius: 12px; font-size: 0.78rem; font-weight: 700;
    }
    .nko-badge {
        background: #1565c0; color: white; padding: 3px 10px;
        border-radius: 12px; font-size: 0.78rem; font-weight: 700;
    }

    /* Level cards */
    .level-card { padding: 0.9rem 1rem; border-radius: 10px; margin: 0.4rem 0; }
    .level-1 { background: #ffebee; border-left: 5px solid #c62828; }
    .level-3 { background: #fff3e0; border-left: 5px solid #e65100; }
    .level-55 { background: #fff8e1; border-left: 5px solid #f9a825; }
    .level-8 { background: #e8f5e9; border-left: 5px solid #2e7d32; }
    .level-10 { background: #e3f2fd; border-left: 5px solid #1565c0; }

    /* Cycle arrow */
    .cycle-step {
        background: white; border: 2px solid #e0e0e0; border-radius: 12px;
        padding: 0.8rem 1rem; margin: 0.3rem 0; display: flex; align-items: center; gap: 0.8rem;
    }
    .cycle-step:hover { border-color: #c00000; }
    .cycle-num {
        background: #c00000; color: white; width: 28px; height: 28px;
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 0.8rem; flex-shrink: 0;
    }
    .cycle-active { border-color: #c00000; background: #fff5f5; }

    /* Buttons */
    .stButton > button {
        background-color: #c00000; color: white; border: none;
        border-radius: 10px; font-weight: 600; padding: 0.5rem 1.5rem;
    }
    .stButton > button:hover { background-color: #8b0000; color: white; }

    /* Sidebar - werkt in light EN dark mode */
    section[data-testid="stSidebar"] { background: white !important; }
    section[data-testid="stSidebar"] h2 { color: #c00000 !important; }
    section[data-testid="stSidebar"] p { color: #333 !important; }
    section[data-testid="stSidebar"] strong { color: #c00000 !important; }
    section[data-testid="stSidebar"] hr { border-color: #ddd !important; }
    /* Radio buttons groot en duidelijk */
    section[data-testid="stSidebar"] .stRadio label { color: #222 !important; font-size: 1.05rem !important; font-weight: 700 !important; }
    section[data-testid="stSidebar"] .stRadio label:hover { color: #c00000 !important; }
    section[data-testid="stSidebar"] .stRadio label p { color: #222 !important; font-size: 1.05rem !important; font-weight: 700 !important; }
    section[data-testid="stSidebar"] .stRadio label span { color: #222 !important; }
    section[data-testid="stSidebar"] .stRadio div[data-testid="stMarkdownContainer"] p { color: #222 !important; font-weight: 700 !important; }
    /* Forceer witte achtergrond op hele pagina ook in dark mode */
    .stApp, .stApp > div { background-color: #ffffff !important; color: #333 !important; }
    .stApp header { background-color: #ffffff !important; }
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span { color: #333 !important; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #1a1a1a !important; }

    /* Expectation box */
    .expect-box {
        background: #f0faf0; border: 1px solid #a5d6a7; border-radius: 10px;
        padding: 0.8rem 1rem; margin: 0.5rem 0;
    }
    .expect-label {
        font-weight: 700; color: #2e7d32; font-size: 0.82rem;
        text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.3rem;
    }

    /* Warning box */
    .warn-box {
        background: #fff8e1; border: 1px solid #ffe082; border-radius: 10px;
        padding: 0.8rem 1rem; margin: 0.5rem 0;
    }

    /* KO fout card */
    .ko-fout-card {
        background: white; border: 1px solid #ffcdd2; border-left: 5px solid #c62828;
        border-radius: 10px; padding: 1rem; margin: 0.6rem 0;
    }
    .ko-fout-title { font-weight: 700; color: #c62828; margin-bottom: 0.3rem; }
    .ko-fout-fix { color: #2e7d32; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.markdown("## 🎓 AI Learning Lab")
st.sidebar.markdown("**Module 1: Organisatie & Omgeving**")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "📍 Navigatie",
    [
        "🏠 Start",
        "📊 Zelfinschatting",
        "🤖 AI Feedbackcoach",
        "🎙️ CGI Oefencoach",
        "🎧 Video & Podcast",
        "📋 Rubrics Naslagwerk",
        "👨‍🏫 Docent Dashboard",
    ],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="background: #ffebee; border: 1px solid #c00000; border-radius: 10px; padding: 0.8rem; margin-top: 0.5rem;">
    <p style="color: #333; font-size: 0.82rem; margin: 0;">
        ⚠️ <strong style="color: #c00000;">Belangrijk:</strong> De AI geeft geen cijfers. De docent blijft verantwoordelijk voor de beoordeling.
    </p>
</div>
""", unsafe_allow_html=True)

# --- Rubric Data ---
RUBRIC = {
    "criterium_1": {
        "naam": "Analyse & onderbouwing",
        "weging": "40%",
        "ko": True,
        "icon": "🔍",
        "kleur": "#c00000",
        "niveaus": {
            1: "Geen analyse of slechts 1 element. Geen verbanden. Geen bronnen.",
            3: "3-4 elementen beschreven zonder onderlinge verbanden. Bronnen beperkt of ontbrekend.",
            5.5: "Alle elementen geanalyseerd met onderlinge verbanden. Min. 3 relevante bronnen. Misalignment concreet benoemd.",
            8: "Grondige analyse met kwantitatieve onderbouwing. Modellen onderling gekoppeld. Stakeholderanalyse geintegreerd.",
            10: "Systemische analyse: causaliteit aangetoond. Duurzaamheidsperspectief (SDG/Kapitalen) geintegreerd. Academisch niveau.",
        },
    },
    "criterium_2": {
        "naam": "Advies & onderbouwing",
        "weging": "35%",
        "ko": True,
        "icon": "💡",
        "kleur": "#e65100",
        "niveaus": {
            1: "Geen advies of niet verbonden aan analyse. Vrijblijvend.",
            3: "Voorstel aanwezig maar vaag. Geen SMART KPI. Geen SDG-koppeling.",
            5.5: "Concreet en stellig advies verbonden aan analyse. Min. 1 SMART KPI. SDG-koppeling met specifiek target.",
            8: "Meerdere alternatieven gewogen. Implementatieperspectief met tijdlijn. Leading/lagging KPIs.",
            10: "Businesscase met kosten-baten. Trade-offs Zes Kapitalen expliciet. Schaalbaarheidsperspectief.",
        },
    },
    "criterium_3": {
        "naam": "Professioneel handelen, reflectie & AI",
        "weging": "25%",
        "ko": False,
        "icon": "🧠",
        "kleur": "#1565c0",
        "niveaus": {
            1: "Geen AI-logboek. Geen reflectie. Bronnen ontbreken.",
            3: "AI-logboek onvolledig. Reflectie oppervlakkig. Beperkte bronvermelding.",
            5.5: "AI-logboek per sessie met reflectie. Eigen verwerking zichtbaar. APA correct. Professionele rapportage.",
            8: "Kritische reflectie op AI: correcties gedocumenteerd. Bewuste inzet per fase. Bronnen divers en relevant.",
            10: "Strategische AI-inzet met meta-reflectie. Toont hoe AI denken versterkte zonder te vervangen. Academisch schrijfniveau.",
        },
    },
}

FEEDBACK_PROMPT = """Je bent een formatieve feedbackcoach voor Module 1 "Organisatie & Omgeving" van de opleiding AD Bedrijfskunde aan Avans Hogeschool. Je geeft GEEN cijfer. Je bent een spiegel, geen beoordelaar.

## Jouw rol
- Je analyseert studentwerk op basis van de drie rubriccriteria hieronder
- Je geeft per criterium aan op welk niveau het werk zich bevindt (1/3/5,5/8/10)
- Je formuleert feedback als vragen en suggesties, niet als oordelen
- Je wijst op concrete verbeterpunten met voorbeelden uit het werk van de student
- Je bent eerlijk maar constructief

## De drie rubriccriteria

### Criterium 1 — Analyse & onderbouwing (40%, KO-criterium)
| Niveau | Beschrijving |
|--------|-------------|
| 1 | Geen analyse of slechts 1 element. Geen verbanden. Geen bronnen. |
| 3 | 3-4 elementen beschreven zonder onderlinge verbanden. Bronnen beperkt of ontbrekend. |
| 5,5 | Alle elementen geanalyseerd met onderlinge verbanden. Min. 3 relevante bronnen. Misalignment concreet benoemd. |
| 8 | Grondige analyse met kwantitatieve onderbouwing. Modellen onderling gekoppeld. Stakeholderanalyse geintegreerd. |
| 10 | Systemische analyse: causaliteit aangetoond. Duurzaamheidsperspectief geintegreerd. Academisch niveau. |

### Criterium 2 — Advies & onderbouwing (35%, KO-criterium)
| Niveau | Beschrijving |
|--------|-------------|
| 1 | Geen advies of niet verbonden aan analyse. Vrijblijvend. |
| 3 | Voorstel aanwezig maar vaag. Geen SMART KPI. Geen SDG-koppeling. |
| 5,5 | Concreet advies verbonden aan analyse. Min. 1 SMART KPI. SDG-koppeling met specifiek target. |
| 8 | Meerdere alternatieven gewogen. Implementatieperspectief met tijdlijn. Leading/lagging KPIs. |
| 10 | Businesscase met kosten-baten. Trade-offs Zes Kapitalen expliciet. Schaalbaarheidsperspectief. |

### Criterium 3 — Professioneel handelen, reflectie & AI (25%, niet-KO)
| Niveau | Beschrijving |
|--------|-------------|
| 1 | Geen AI-logboek. Geen reflectie. Bronnen ontbreken. |
| 3 | AI-logboek onvolledig. Reflectie oppervlakkig. Beperkte bronvermelding. |
| 5,5 | AI-logboek per sessie met reflectie. Eigen verwerking zichtbaar. APA correct. |
| 8 | Kritische reflectie op AI: correcties gedocumenteerd. Bewuste inzet per fase. Bronnen divers. |
| 10 | Strategische AI-inzet met meta-reflectie. Toont hoe AI denken versterkte. Academisch schrijfniveau. |

## Veelgemaakte KO-fouten (waarschuw expliciet)
- SBMC-bouwstenen leeg of vaag
- 7S zonder misalignment-analyse
- BCG zonder databron voor marktgroei
- AI-logboek ontbreekt of is minimaal
- DESTEP niet gekoppeld aan de specifieke organisatie
- SWOT zonder confrontatiematrix
- Advies zonder onderbouwing of SDG-koppeling

## Instructies
Geef feedback in dit format per criterium:
**Huidig niveau:** [niveau]
**Wat gaat goed:** [concreet]
**Wat ontbreekt of kan beter:** [concreet]
**Vraag om over na te denken:** [reflectievraag]

Sluit af met:
**KO-check:** [eventuele risico's]
**Sterkste punt:** [...]
**Belangrijkste verbeterpunt:** [...]
**Concrete eerste stap:** [wat nu aanpakken]

Geef NOOIT een cijfer. Zeg altijd: "Dit is formatieve feedback, geen beoordeling."
"""


# ============================
# PAGE: Start
# ============================
def page_start():
    st.markdown('<p class="main-header">🎓 AI Learning Lab</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Module 1: Organisatie & Omgeving — Kwaliteitscyclus</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        <strong>👋 Welkom!</strong> Deze app helpt je om de kwaliteit van je rapport te herkennen en te verbeteren.
        Je gebruikt AI-tools als <strong>spiegel</strong> — niet als beoordelaar. Jij blijft in de lead, de docent geeft het cijfer.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # --- 3 Step Cards (using pure Streamlit for clickability) ---
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("#### :red[1] :bar_chart: Zelfinschatting")
            st.markdown("Schat per criterium in op welk niveau je eigen werk zit. Bekijk de niveaubeschrijvingen en kies eerlijk.")
            st.caption("**Wat je levert:** Score per criterium + motivatie")
            if st.button("Start Zelfinschatting", key="btn_zi", use_container_width=True, type="primary"):
                st.session_state["nav"] = "📊 Zelfinschatting"
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("#### :red[2] :robot_face: AI Feedbackcoach")
            st.markdown("Plak je tekst en ontvang feedback per criterium. De AI vertelt wat goed gaat en wat beter kan.")
            st.caption("**Wat je terugkrijgt:** Niveau-inschatting + verbeterpunten")
            if st.button("Start Feedbackcoach", key="btn_fb", use_container_width=True, type="primary"):
                st.session_state["nav"] = "🤖 AI Feedbackcoach"
                st.rerun()

    with col3:
        with st.container(border=True):
            st.markdown("#### :red[3] :studio_microphone: CGI Oefencoach")
            st.markdown("Oefen je mondeling met een AI-beoordelaar die doorvraagt. Met voice of avatar.")
            st.caption("**Wat je terugkrijgt:** Gesproken feedback + tips")
            if st.button("Start CGI Coach", key="btn_cgi", use_container_width=True, type="primary"):
                st.session_state["nav"] = "🎙️ CGI Oefencoach"
                st.rerun()

    st.markdown("")
    st.markdown("---")

    # --- Kwaliteitscyclus ---
    st.markdown("### 🔄 De Kwaliteitscyclus — zo gebruik je deze app")

    steps = [
        ("📝", "Lever je tussenproduct in", "Je onderdeel (7S, DESTEP, SWOT, advies) is klaar als concept"),
        ("📊", "Doe de zelfinschatting", "Schat per criterium in: op welk niveau zit ik? Waarom?"),
        ("🤖", "Vraag AI-feedback", "Plak je tekst in de Feedbackcoach en lees de analyse"),
        ("🔀", "Vergelijk", "Waar verschilt je eigen inschatting van de AI-feedback?"),
        ("✍️", "Schrijf reflectie", "Wat heb je geleerd? Wat ga je aanpassen?"),
        ("🔧", "Pas je werk aan", "Verbeter je rapport op basis van de feedback"),
        ("👨‍🏫", "Docent beoordeelt", "De docent geeft het definitieve cijfer (summatief)"),
    ]

    for i, (icon, title, desc) in enumerate(steps):
        active = " cycle-active" if i in [1, 2, 3] else ""
        st.markdown(f"""
        <div class="cycle-step{active}">
            <div class="cycle-num">{i+1}</div>
            <div><strong>{icon} {title}</strong><br><span style="color:#888; font-size:0.85rem;">{desc}</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box-green" style="margin-top: 1rem;">
        <strong>💡 Tip:</strong> Stap 2, 3 en 4 (gemarkeerd) kun je meerdere keren herhalen. Hoe vaker je de cyclus doorloopt, hoe beter je kwaliteitsbewustzijn wordt.
    </div>
    """, unsafe_allow_html=True)


# ============================
# PAGE: Zelfinschatting
# ============================
def page_zelfinschatting():
    st.markdown('<p class="main-header">📊 Zelfinschatting</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Schat in op welk niveau je eigen werk zich bevindt</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        <strong>🎯 Doel:</strong> Leer herkennen hoe goed je eigen werk is. Dit telt <strong>niet</strong> mee voor je cijfer.<br>
        <strong>📥 Wat je invoert:</strong> Je naam, het onderdeel dat je inlevert, en je inschatting per criterium.<br>
        <strong>📤 Wat er gebeurt:</strong> Je inschatting wordt opgeslagen. Na de AI-feedback kun je terugkomen voor reflectie.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # Student info
    col1, col2 = st.columns(2)
    with col1:
        naam = st.text_input("👤 Naam en studentnummer", placeholder="bijv. Jan Jansen — 2345678")
    with col2:
        onderdeel = st.selectbox("📄 Welk onderdeel lever je in?", [
            "7S-analyse (interne analyse)",
            "DESTEP + Porter (externe analyse)",
            "SWOT + confrontatiematrix",
            "Strategisch advies",
            "Volledig rapport",
        ])

    week = st.selectbox("📅 Meetmoment", ["Week 4 (Formatief 1)", "Week 6 (Formatief 2)", "Week 8 (Voor inleveren)"])

    st.markdown("---")
    st.markdown("### Jouw inschatting per criterium")

    scores = {}
    motivaties = {}

    for key, crit in RUBRIC.items():
        badge = f'<span class="ko-badge">⚠️ KO-criterium</span>' if crit["ko"] else '<span class="nko-badge">Niet-KO</span>'
        st.markdown(f"### {crit['icon']} {crit['naam']} ({crit['weging']}) {badge}", unsafe_allow_html=True)

        if crit["ko"]:
            st.markdown("""
            <div class="warn-box">
                <strong>⚠️ Let op:</strong> Dit is een KO-criterium. Bij een onvoldoende (<5,5) is je maximale eindcijfer een 4,5.
            </div>
            """, unsafe_allow_html=True)

        with st.expander("👁️ Bekijk de niveaubeschrijvingen — klik om te openen"):
            for niveau, beschrijving in crit["niveaus"].items():
                level_class = {1: "level-1", 3: "level-3", 5.5: "level-55", 8: "level-8", 10: "level-10"}
                emoji = {1: "🔴", 3: "🟠", 5.5: "🟡", 8: "🟢", 10: "🔵"}
                st.markdown(
                    f'<div class="level-card {level_class[niveau]}">{emoji[niveau]} <strong>Niveau {niveau}:</strong> {beschrijving}</div>',
                    unsafe_allow_html=True,
                )

        score_options = [1, 3, 5.5, 8, 10]
        score_labels = ["🔴 1 — Onvoldoende", "🟠 3 — Matig", "🟡 5,5 — Voldoende", "🟢 8 — Goed", "🔵 10 — Uitstekend"]
        selected = st.select_slider(
            f"Jouw inschatting voor {crit['naam']}",
            options=score_options,
            format_func=lambda x: score_labels[score_options.index(x)],
            value=5.5,
            key=f"score_{key}",
        )
        scores[key] = selected

        motivatie = st.text_area(
            f"💬 Waarom denk je dat je op dit niveau zit? Geef een concreet voorbeeld uit je rapport.",
            key=f"mot_{key}",
            height=100,
            placeholder="bijv. 'Ik heb 4 bronnen gebruikt en de misalignment tussen Strategie en Structuur benoemd...'"
        )
        motivaties[key] = motivatie

        st.markdown("---")

    # Reflectie na AI-feedback
    st.markdown("### ✍️ Reflectie na AI-feedback")
    st.markdown("""
    <div class="info-box-orange">
        <strong>⏱️ Vul dit later in</strong> — nadat je de AI Feedbackcoach hebt gebruikt. Kom dan terug naar deze pagina.
    </div>
    """, unsafe_allow_html=True)

    reflectie_verschil = st.text_area("🔀 Op welke punten verschilde de AI-feedback van je eigen inschatting?", key="refl_verschil", height=100)
    reflectie_verrassing = st.text_area("😮 Welk feedbackpunt verraste je het meest? Waarom?", key="refl_verrassing", height=100)
    reflectie_actie = st.text_area("✅ Wat ga je concreet aanpassen? Noem minimaal 2 actiepunten.", key="refl_actie", height=100)

    # Submit
    st.markdown("")
    if st.button("💾 Zelfinschatting opslaan", type="primary", use_container_width=True):
        if not naam:
            st.error("⚠️ Vul je naam en studentnummer in.")
            return

        entry = {
            "timestamp": datetime.now().isoformat(),
            "naam": naam,
            "onderdeel": onderdeel,
            "week": week,
            "score_c1": scores["criterium_1"],
            "score_c2": scores["criterium_2"],
            "score_c3": scores["criterium_3"],
            "motivatie_c1": motivaties["criterium_1"],
            "motivatie_c2": motivaties["criterium_2"],
            "motivatie_c3": motivaties["criterium_3"],
            "reflectie_verschil": reflectie_verschil,
            "reflectie_verrassing": reflectie_verrassing,
            "reflectie_actie": reflectie_actie,
        }

        st.session_state["zelfinschattingen"].append(entry)

        st.success("✅ Zelfinschatting opgeslagen!")
        st.markdown("""
        <div class="info-box-green">
            <strong>👉 Volgende stap:</strong> Ga naar de <strong>AI Feedbackcoach</strong> om feedback te krijgen op je werk.
            Kom daarna hier terug om de reflectie in te vullen.
        </div>
        """, unsafe_allow_html=True)


# ============================
# PAGE: AI Feedbackcoach
# ============================
def page_feedbackcoach():
    st.markdown('<p class="main-header">🤖 AI Feedbackcoach</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Ontvang feedback op je rapport per criterium</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        <strong>🎯 Doel:</strong> De AI analyseert je tekst op de 3 rubriccriteria en geeft feedback.<br>
        <strong>📥 Wat je invoert:</strong> Een stuk tekst uit je rapport (7S, DESTEP, SWOT, advies).<br>
        <strong>📤 Wat je terugkrijgt:</strong> Per criterium: huidig niveau, wat goed gaat, wat beter kan, en een reflectievraag.<br>
        <strong>⚠️ Belangrijk:</strong> De AI geeft <strong>geen cijfer</strong>. Dit is een spiegel, geen beoordeling.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # Two options
    tab_api, tab_manual = st.tabs(["Direct in de app (met API key)", "Handmatig via Claude.ai (gratis)"])

    with tab_api:
        with st.container(border=True):
            st.markdown("**Directe AI-feedback in de app**")
            st.markdown("Plak je tekst, klik op de knop, en ontvang direct feedback hieronder.")

        with st.form("feedback_form"):
            api_key = st.text_input("Anthropic API Key", type="password",
                                    help="Vraag je docent om de API key, of maak een gratis account op console.anthropic.com")

            onderdeel = st.selectbox("Welk onderdeel wil je laten checken?", [
                "7S-analyse", "DESTEP", "Porter 5 krachten", "SWOT",
                "Confrontatiematrix", "Strategisch advies", "Volledig rapport",
            ])

            student_text = st.text_area(
                "Plak hier je tekst",
                height=300,
                placeholder="Kopieer het onderdeel uit je rapport en plak het hier. Minimaal 50 tekens.",
            )

            submitted = st.form_submit_button("Vraag feedback", type="primary", use_container_width=True)

        if submitted:
            if not api_key:
                st.error("Vul je API key in.")
            elif not student_text or len(student_text) < 50:
                st.error("Plak een tekst van minimaal 50 tekens.")
            else:
                try:
                    import anthropic
                    client = anthropic.Anthropic(api_key=api_key)

                    with st.spinner("AI analyseert je werk op basis van de rubriccriteria..."):
                        message = client.messages.create(
                            model="claude-sonnet-4-20250514",
                            max_tokens=4000,
                            messages=[{
                                "role": "user",
                                "content": f"{FEEDBACK_PROMPT}\n\nDe student levert het volgende onderdeel in: {onderdeel}\n\nHier is de tekst van de student:\n\n{student_text}",
                            }],
                        )

                    st.markdown("---")
                    st.markdown("### Feedback van de AI Feedbackcoach")
                    st.markdown(message.content[0].text)
                    st.info("Dit is formatieve feedback, geen beoordeling. De docent geeft het definitieve cijfer. Ga nu terug naar de Zelfinschatting om je reflectie in te vullen.")

                except Exception as e:
                    st.error(f"Er ging iets mis: {e}")

    with tab_manual:
        st.markdown("""
        <div class="tool-card tool-card-green">
            <div class="tool-title">📋 Handmatig via Claude.ai (gratis)</div>
            <div class="tool-subtitle">Kopieer de feedbackprompt, plak in Claude.ai, en voeg je eigen tekst toe.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-box-green">
            <strong>Hoe het werkt — 4 stappen:</strong>
            <ol style="margin: 0.5rem 0 0 1.2rem;">
                <li>Kopieer de prompt hieronder</li>
                <li>Open <a href="https://claude.ai" target="_blank">claude.ai</a> en start een nieuw gesprek</li>
                <li>Plak de prompt, gevolgd door je eigen tekst</li>
                <li>Lees de feedback en ga terug naar <strong>Zelfinschatting</strong> voor je reflectie</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")
        with st.expander("📋 Klik hier om de volledige feedbackprompt te zien en te kopieren", expanded=False):
            st.code(FEEDBACK_PROMPT, language=None)

        st.markdown("""
        <div class="expect-box" style="margin-top: 1rem;">
            <div class="expect-label">📤 Wat je terugkrijgt in Claude.ai</div>
            Per criterium: huidig niveau, wat goed gaat, wat beter kan, een reflectievraag.<br>
            Plus: KO-check, sterkste punt, belangrijkste verbeterpunt, en een concrete eerste stap.
        </div>
        """, unsafe_allow_html=True)


# ============================
# PAGE: CGI Oefencoach
# ============================
def page_cgi():
    st.markdown('<p class="main-header">🎙️ CGI Oefencoach</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Oefen je mondeling met een AI-beoordelaar</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        <strong>🎯 Doel:</strong> Oefen je CGI-verdediging met een AI die doorvraagt zoals een echte beoordelaar.<br>
        <strong>📥 Wat je doet:</strong> Kies een tool, open de link, en beantwoord vragen over je rapport.<br>
        <strong>📤 Wat je terugkrijgt:</strong> Gesproken of geschreven feedback op je antwoorden + tips voor verbetering.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # Three tool cards
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="tool-card tool-card-green">
            <div class="tool-title">🗣️ ChatGPT Voice — Gesproken CGI-oefening</div>
            <div class="tool-subtitle">Gratis met ChatGPT Plus • Echt heen-en-weer gesprek</div>
            <ul style="font-size: 0.9rem; margin: 0.5rem 0;">
                <li>Open de link → tik op 🎙️ microfoon</li>
                <li>De AI stelt vragen, jij antwoordt sprekend</li>
                <li>Krijg direct gesproken feedback</li>
                <li>Zeg "ik wil feedback op mijn werk" voor feedbackmodus</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("🟢 Open CGI Coach in ChatGPT", "https://chatgpt.com/g/g-69bab0ada134819198327518226cd7e3-cgi-coach-module-1-organisatie-omgeving", use_container_width=True)

    with col2:
        st.markdown("""
        <div class="tool-card tool-card-purple">
            <div class="tool-title">👤 Graham Avatar — Sprekende beoordelaar</div>
            <div class="tool-subtitle">HeyGen LiveAvatar • Je ziet een persoon die praat</div>
            <ul style="font-size: 0.9rem; margin: 0.5rem 0;">
                <li>Open de link → klik "Chat now"</li>
                <li>Graham stelt CGI-vragen met beeld en geluid</li>
                <li>Jij antwoordt via je microfoon</li>
                <li>Realistischer dan alleen stem</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("🟣 Open CGI Avatar Coach (Graham)", "https://app.liveavatar.com/e9844e6d-847e-4964-a92b-7ecd066f69df", use_container_width=True)

    st.markdown("")
    st.markdown("""
    <div class="info-box-green">
        <strong>💡 Tip:</strong> Oefen minimaal 2 keer: 1x met je rapport erbij, 1x zonder. Oefen staand — net als bij het echte CGI.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Vragenbank
    st.markdown("### 📝 Vragenbank — bereid je voor op deze vragen")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="tool-card tool-card-red">
            <div class="tool-title">🔍 Analysevragen (Criterium 1 — KO)</div>
        </div>
        """, unsafe_allow_html=True)
        questions_c1 = [
            "Waarom heb je juist het 7S-model gebruikt voor deze organisatie?",
            "Welke misalignment in het 7S-model vond je het meest opvallend en waarom?",
            "Je plaatst product X als Question Mark in de BCG. Hoe weet je dat de markt groeit?",
            "Wat zou er veranderen in je SBMC als de organisatie morgen failliet gaat?",
            "Kun je een concreet verband leggen tussen twee S-elementen die niet op elkaar aansluiten?",
        ]
        for q in questions_c1:
            st.markdown(f"- {q}")

    with col2:
        st.markdown("""
        <div class="tool-card tool-card-orange">
            <div class="tool-title">💡 Adviesvragen (Criterium 2 — KO)</div>
        </div>
        """, unsafe_allow_html=True)
        questions_c2 = [
            "Waarom is deze kans specifiek voor JULLIE organisatie, en niet voor de hele sector?",
            "Wat is het grootste risico van jullie advies?",
            "Hoe weet je dat de confrontatiematrix-keuze de juiste is?",
            "Hoe hangt je advies samen met een specifiek SDG-target?",
            "Als de directeur vraagt 'waarom dit en niet iets anders?' — wat zeg je?",
        ]
        for q in questions_c2:
            st.markdown(f"- {q}")

    st.markdown("""
    <div class="tool-card tool-card-blue">
        <div class="tool-title">🧠 AI-transparantievragen (altijd)</div>
    </div>
    """, unsafe_allow_html=True)
    questions_ai = [
        "Hoe heb je AI gebruikt in dit rapport? Waarvoor precies?",
        "Geef een voorbeeld waarbij AI iets verkeerd had dat jij hebt gecorrigeerd.",
        "Waar ligt voor jou de grens van AI-gebruik?",
    ]
    for q in questions_ai:
        st.markdown(f"- {q}")

    st.markdown("---")

    # PAIA
    st.markdown("### 🏗️ PAIA — Zo bouw je een sterk antwoord op")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="tool-card tool-card-red" style="text-align:center;">
            <div style="font-size: 2rem;">🎯</div>
            <div class="tool-title">P — Punt</div>
            <div style="font-size: 0.85rem;">Begin met je kernboodschap</div>
            <div style="font-size: 0.8rem; color: #888; margin-top: 0.3rem;"><em>"Ons advies is digitalisering omdat..."</em></div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="tool-card tool-card-orange" style="text-align:center;">
            <div style="font-size: 2rem;">📊</div>
            <div class="tool-title">A — Argumenten</div>
            <div style="font-size: 0.85rem;">2-3 concrete bewijzen</div>
            <div style="font-size: 0.8rem; color: #888; margin-top: 0.3rem;"><em>"SWOT toont... CBS-data..."</em></div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="tool-card tool-card-green" style="text-align:center;">
            <div style="font-size: 2rem;">💡</div>
            <div class="tool-title">I — Illustratie</div>
            <div style="font-size: 0.85rem;">Concreet voorbeeld</div>
            <div style="font-size: 0.8rem; color: #888; margin-top: 0.3rem;"><em>"Buurtzorg: 30% minder admin"</em></div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="tool-card tool-card-blue" style="text-align:center;">
            <div style="font-size: 2rem;">🏁</div>
            <div class="tool-title">A — Afsluiting</div>
            <div style="font-size: 0.85rem;">Herhaal conclusie</div>
            <div style="font-size: 0.8rem; color: #888; margin-top: 0.3rem;"><em>"Daarom is ICT de beste koers"</em></div>
        </div>
        """, unsafe_allow_html=True)


# ============================
# PAGE: Video & Podcast
# ============================
def page_media():
    st.markdown('<p class="main-header">🎧 Video & Podcast</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Luister, kijk en leer — op je eigen tempo</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        <strong>🎯 Doel:</strong> Begrijp de rubrics, vermijd KO-fouten, en bereid je voor op het CGI.<br>
        <strong>📥 Wat je doet:</strong> Luister de podcasts en stel vragen via NotebookLM.<br>
        <strong>📤 Wat je leert:</strong> Hoe de beoordeling werkt, waar studenten falen, en hoe je je mondeling aanpakt.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="tool-card tool-card-red">
            <div class="tool-title">🎧 Podcast 1: Voorkom een KO bij je bedrijfsrapport</div>
            <div class="tool-subtitle">~15 minuten • Rubrics, KO-fouten, niveauverschillen</div>
        </div>
        """, unsafe_allow_html=True)

        st.info("🎧 Luister via NotebookLM — klik op de link onderaan deze pagina.")

        st.markdown("""
        <div class="expect-box">
            <div class="expect-label">📤 Wat je leert</div>
            • Hoe de 3 beoordelingscriteria werken<br>
            • Wat de KO-regel concreet betekent<br>
            • Het verschil tussen niveau 3, 5,5 en 8<br>
            • De 7 meest gemaakte KO-fouten<br>
            • Hoe je AI slim en verantwoord gebruikt
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="tool-card tool-card-orange">
            <div class="tool-title">🎧 Podcast 2: Zo overleef je het beruchte CGI</div>
            <div class="tool-subtitle">~18 minuten • PAIA-methode, moeilijkste vragen, AI-transparantie</div>
        </div>
        """, unsafe_allow_html=True)

        st.info("🎧 Luister via NotebookLM — klik op de link onderaan deze pagina.")

        st.markdown("""
        <div class="expect-box">
            <div class="expect-label">📤 Wat je leert</div>
            • Wat het CGI wel en niet toetst<br>
            • De PAIA-antwoordstructuur<br>
            • De 3 moeilijkste vragen en hoe je ze beantwoordt<br>
            • Omgaan met AI-vragen in het CGI<br>
            • Wat te doen als je vastloopt
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div class="tool-card tool-card-blue">
        <div class="tool-title">🔎 NotebookLM — Stel je eigen vragen over de rubric</div>
        <div class="tool-subtitle">Open het notebook, stel een vraag, en krijg antwoord op basis van de bronnen.</div>
    </div>
    """, unsafe_allow_html=True)

    st.link_button("🔵 Open Kwaliteitsspiegel in NotebookLM", "https://notebooklm.google.com/notebook/ba023c5c-1004-4868-97ef-2a3d056570fd", use_container_width=True)


# ============================
# PAGE: Rubrics Naslagwerk
# ============================
def page_rubrics():
    st.markdown('<p class="main-header">📋 Rubrics Naslagwerk</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">De volledige beoordelingscriteria — altijd bij de hand</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        <strong>📖 Gebruik deze pagina als referentie</strong> terwijl je werkt aan je rapport.
        Bekijk per criterium wat je nodig hebt voor elk niveau.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    for key, crit in RUBRIC.items():
        badge = "⚠️ KO-criterium" if crit["ko"] else "Niet-KO"
        badge_class = "ko-badge" if crit["ko"] else "nko-badge"

        st.markdown(f'### {crit["icon"]} {crit["naam"]} ({crit["weging"]}) <span class="{badge_class}">{badge}</span>', unsafe_allow_html=True)

        for niveau, beschrijving in crit["niveaus"].items():
            level_class = {1: "level-1", 3: "level-3", 5.5: "level-55", 8: "level-8", 10: "level-10"}
            emoji = {1: "🔴", 3: "🟠", 5.5: "🟡", 8: "🟢", 10: "🔵"}
            st.markdown(
                f'<div class="level-card {level_class[niveau]}">{emoji[niveau]} <strong>Niveau {niveau}:</strong> {beschrijving}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("")

    st.markdown("---")

    st.markdown("### 🚨 KO-fouten — vermijd deze!")
    st.markdown("""
    <div class="info-box-red">
        <strong>Als je een van deze fouten maakt, riskeer je een KO (onvoldoende).</strong>
        Check je rapport op elk punt voordat je inlevert.
    </div>
    """, unsafe_allow_html=True)

    ko_fouten = [
        ("SBMC bouwstenen leeg of vaag", "Schrijf concrete cijfers, certificeringen of externe rapporten. Geen marketingclaims.", "🏢"),
        ("7S zonder misalignment-analyse", "Benoem verbanden EN botsingen tussen elementen. Minimaal 2 misalignments.", "🔗"),
        ("BCG zonder databron voor marktgroei", "Noem altijd een bron (CBS, brancherapport) voor marktgroei EN marktaandeel.", "📈"),
        ("AI-logboek ontbreekt of is minimaal", "Gebruik het format: datum / tool / prompt / output / verificatie / aanpassing.", "🤖"),
        ("DESTEP niet gekoppeld aan organisatie", "Voeg altijd toe: 'Dit beinvloedt [bedrijf] doordat... Dit is een kans/bedreiging omdat...'", "🌍"),
        ("SWOT zonder confrontatiematrix", "Maak altijd een 2x2 confrontatiematrix. Zonder matrix = KO.", "📊"),
        ("Advies zonder onderbouwing of SDG-koppeling", "Gebruik: 'Op basis van [combinatie] adviseren wij [maatregel]. Dit draagt bij aan SDG [nummer].'", "🎯"),
    ]

    for i, (fout, oplossing, icon) in enumerate(ko_fouten, 1):
        st.markdown(f"""
        <div class="ko-fout-card">
            <div class="ko-fout-title">{icon} Fout {i}: {fout}</div>
            <div class="ko-fout-fix">✅ Oplossing: {oplossing}</div>
        </div>
        """, unsafe_allow_html=True)


# ============================
# PAGE: Docent Dashboard
# ============================
def page_dashboard():
    st.markdown('<p class="main-header">👨‍🏫 Docent Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Overzicht, beoordeling en inschatfout-analyse</p>', unsafe_allow_html=True)

    password = st.text_input("🔒 Docentwachtwoord", type="password")
    if password != "avans2026":
        st.markdown("""
        <div class="info-box-orange">
            <strong>🔐 Beveiligd.</strong> Voer het docentwachtwoord in om het dashboard te openen.
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown("""
    <div class="info-box-green">
        <strong>✅ Ingelogd als docent.</strong> Hier zie je alle zelfinschattingen, kun je docentcijfers invoeren, en de inschatfout analyseren.
    </div>
    """, unsafe_allow_html=True)

    # Upload option for cloud
    uploaded = st.file_uploader("📤 Upload eerder geexporteerde zelfinschattingen (CSV)", type="csv")
    if uploaded:
        import pandas as pd
        df_up = pd.read_csv(uploaded)
        st.session_state["zelfinschattingen"] = df_up.to_dict("records")
        st.success(f"✅ {len(df_up)} zelfinschattingen geladen.")

    data = st.session_state["zelfinschattingen"]
    if not data:
        st.info("📭 Nog geen zelfinschattingen ontvangen.")
        return

    import pandas as pd
    df = pd.DataFrame(data)

    # Summary
    st.markdown(f"### 📊 Overzicht — {len(df)} zelfinschattingen")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📝 Totaal inzendingen", len(df))
    with col2:
        st.metric("🔍 Gem. C1 (Analyse)", f"{df['score_c1'].mean():.1f}")
    with col3:
        st.metric("💡 Gem. C2 (Advies)", f"{df['score_c2'].mean():.1f}")
    with col4:
        st.metric("🧠 Gem. C3 (Prof.)", f"{df['score_c3'].mean():.1f}")

    st.markdown("---")

    # Per week
    if "week" in df.columns:
        st.markdown("### 📅 Per meetmoment")
        for week in df["week"].unique():
            week_df = df[df["week"] == week]
            with st.expander(f"**{week}** — {len(week_df)} inzendingen"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("C1 Analyse", f"{week_df['score_c1'].mean():.1f}")
                with col2:
                    st.metric("C2 Advies", f"{week_df['score_c2'].mean():.1f}")
                with col3:
                    st.metric("C3 Prof.", f"{week_df['score_c3'].mean():.1f}")

    st.markdown("---")

    # Distribution
    st.markdown("### 📈 Verdeling scores")
    tab1, tab2, tab3 = st.tabs(["🔍 Criterium 1", "💡 Criterium 2", "🧠 Criterium 3"])
    with tab1:
        st.bar_chart(df["score_c1"].value_counts().sort_index())
    with tab2:
        st.bar_chart(df["score_c2"].value_counts().sort_index())
    with tab3:
        st.bar_chart(df["score_c3"].value_counts().sort_index())

    st.markdown("---")

    # Docentbeoordeling
    st.markdown("### ✏️ Docentbeoordeling invoeren")
    st.markdown("""
    <div class="info-box">
        <strong>Hoe het werkt:</strong> Selecteer een student, bekijk hun zelfinschatting, en voer jouw beoordeling in.
        De app berekent automatisch de inschatfout (verschil tussen zelfinschatting en docentcijfer).
    </div>
    """, unsafe_allow_html=True)

    studenten = df["naam"].unique()
    selected_student = st.selectbox("👤 Selecteer student", studenten)

    if selected_student:
        student_df = df[df["naam"] == selected_student]
        st.dataframe(student_df[["week", "onderdeel", "score_c1", "score_c2", "score_c3"]], use_container_width=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            db_c1 = st.number_input("🔍 Docentcijfer C1", min_value=1.0, max_value=10.0, step=0.5, value=5.5, key="db_c1")
        with col2:
            db_c2 = st.number_input("💡 Docentcijfer C2", min_value=1.0, max_value=10.0, step=0.5, value=5.5, key="db_c2")
        with col3:
            db_c3 = st.number_input("🧠 Docentcijfer C3", min_value=1.0, max_value=10.0, step=0.5, value=5.5, key="db_c3")

        if st.button("💾 Beoordeling opslaan", use_container_width=True):
            beoordeling = {
                "timestamp": datetime.now().isoformat(),
                "naam": selected_student,
                "docent_c1": db_c1,
                "docent_c2": db_c2,
                "docent_c3": db_c3,
            }
            st.session_state["docentbeoordelingen"].append(beoordeling)
            st.success(f"✅ Beoordeling voor {selected_student} opgeslagen.")

    st.markdown("---")

    # Inschatfout analyse
    beo = st.session_state["docentbeoordelingen"]
    if beo:
        st.markdown("### 🎯 Inschatfout-analyse")
        st.markdown("""
        <div class="info-box-orange">
            <strong>Wat is de inschatfout?</strong> Het absolute verschil tussen de zelfinschatting van de student en het docentcijfer.
            Een lagere inschatfout = beter kwaliteitsbewustzijn.
        </div>
        """, unsafe_allow_html=True)

        beo_df = pd.DataFrame(beo)
        latest_zi = df.sort_values("timestamp").groupby("naam").last().reset_index()
        merged = latest_zi.merge(beo_df.groupby("naam").last().reset_index(), on="naam", suffixes=("_zi", "_db"))

        if len(merged) > 0:
            merged["fout_c1"] = abs(merged["score_c1"] - merged["docent_c1"])
            merged["fout_c2"] = abs(merged["score_c2"] - merged["docent_c2"])
            merged["fout_c3"] = abs(merged["score_c3"] - merged["docent_c3"])

            st.dataframe(
                merged[["naam", "score_c1", "docent_c1", "fout_c1", "score_c2", "docent_c2", "fout_c2", "score_c3", "docent_c3", "fout_c3"]],
                use_container_width=True,
            )

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🎯 Gem. inschatfout C1", f"{merged['fout_c1'].mean():.1f}")
            with col2:
                st.metric("🎯 Gem. inschatfout C2", f"{merged['fout_c2'].mean():.1f}")
            with col3:
                st.metric("🎯 Gem. inschatfout C3", f"{merged['fout_c3'].mean():.1f}")

    # Export
    st.markdown("---")
    st.markdown("### 📥 Data exporteren")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 Download zelfinschattingen (CSV)",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="zelfinschattingen_export.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col2:
        if st.session_state["docentbeoordelingen"]:
            beo_df = pd.DataFrame(st.session_state["docentbeoordelingen"])
            st.download_button(
                "📥 Download docentbeoordelingen (CSV)",
                data=beo_df.to_csv(index=False).encode("utf-8"),
                file_name="docentbeoordelingen_export.csv",
                mime="text/csv",
                use_container_width=True,
            )


# ============================
# ROUTER
# ============================
if "nav" in st.session_state:
    page = st.session_state["nav"]
    del st.session_state["nav"]

if page == "🏠 Start":
    page_start()
elif page == "📊 Zelfinschatting":
    page_zelfinschatting()
elif page == "🤖 AI Feedbackcoach":
    page_feedbackcoach()
elif page == "🎙️ CGI Oefencoach":
    page_cgi()
elif page == "🎧 Video & Podcast":
    page_media()
elif page == "📋 Rubrics Naslagwerk":
    page_rubrics()
elif page == "👨‍🏫 Docent Dashboard":
    page_dashboard()

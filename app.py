"""
Document Anonymizer — Gevoelige informatie anonimiseren
Upload een PDF of Word-document en anonimiseer automatisch:
namen, adressen, telefoonnummers, e-mails, BSN/belastingnummers,
studentnummers, bedrijfsnamen, IBAN-nummers en meer.
"""

import streamlit as st
import re
import io
import tempfile
import os

# --- Page Config ---
st.set_page_config(
    page_title="Document Anonymizer",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

    .block-container { padding-top: 1.5rem; max-width: 1000px; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main-header {
        font-size: 2.2rem; font-weight: 900; color: #c00000;
        margin-bottom: 0.2rem; letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 1.1rem; color: #666; margin-bottom: 1.5rem;
        border-bottom: 3px solid #c00000; padding-bottom: 0.8rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
        border: 2px solid #e0e0e0; border-radius: 12px;
        padding: 1rem; text-align: center; margin: 0.3rem 0;
    }
    .stat-number { font-size: 1.8rem; font-weight: 900; color: #c00000; }
    .stat-label { font-size: 0.85rem; color: #888; }
    .highlight-box {
        background: #fff3cd; border-left: 4px solid #ffc107;
        padding: 0.8rem 1rem; border-radius: 0 8px 8px 0;
        margin: 0.5rem 0; font-size: 0.9rem;
    }
    .success-box {
        background: #d4edda; border-left: 4px solid #28a745;
        padding: 0.8rem 1rem; border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
    }
    .anon-tag {
        background: #c00000; color: white; padding: 2px 8px;
        border-radius: 4px; font-weight: 600; font-size: 0.85rem;
    }
    .category-header {
        font-weight: 700; color: #37474f; margin-top: 0.8rem;
        margin-bottom: 0.3rem; font-size: 0.95rem;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #e0e0e0; border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- Regex Patterns for Dutch / International sensitive data ---
PATTERNS = {
    "E-mailadres": r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b',
    "Telefoonnummer": (
        r'(?:\+31[\s\-]?|0031[\s\-]?|0)'
        r'(?:[1-9]\d{1,2}[\s\-]?\d{6,7}|\d[\s\-]?\d{3}[\s\-]?\d{4}|'
        r'\d{2}[\s\-]?\d{3}[\s\-]?\d{3,4}|\d{3}[\s\-]?\d{2}[\s\-]?\d{2}[\s\-]?\d{2})'
    ),
    "BSN (Burgerservicenummer)": r'\b\d{9}\b',
    "IBAN": r'\b[A-Z]{2}\d{2}[\s]?[A-Z]{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2,4}[\s]?\d{0,2}\b',
    "Postcode (NL)": r'\b\d{4}\s?[A-Z]{2}\b',
    "KvK-nummer": r'\b\d{8}\b',
    "Studentnummer": r'\b[sS]?\d{6,8}\b',
    "Datum": r'\b\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{2,4}\b',
}

# Base placeholder labels for each category (used to generate indexed placeholders)
PLACEHOLDER_BASE = {
    "E-mailadres": "E-MAIL",
    "Telefoonnummer": "TELEFOON",
    "BSN (Burgerservicenummer)": "BSN",
    "IBAN": "IBAN",
    "Postcode (NL)": "POSTCODE",
    "KvK-nummer": "KVK",
    "Studentnummer": "STUDENTNR",
    "Datum": "DATUM",
    "Persoonsnaam": "NAAM",
    "Bedrijfsnaam": "BEDRIJF",
    "Adres": "ADRES",
    "Locatie": "LOCATIE",
    "Handmatig": "VERBORGEN",
}

# Legacy PLACEHOLDER_MAP kept for display/export compatibility
PLACEHOLDER_MAP = {cat: f"[{base}]" for cat, base in PLACEHOLDER_BASE.items()}


def _index_label(index: int) -> str:
    """Return A-Z for 0-25, then 1, 2, 3... for 26+."""
    if index < 26:
        return chr(ord('A') + index)
    return str(index - 25)


def build_placeholder_mapping(entities_to_replace: dict) -> dict:
    """Build a mapping from each unique entity value to a consistent indexed placeholder.

    Returns dict: {original_value: (placeholder_string, category)}
    When a category has only one unique value, no index suffix is added.
    """
    mapping = {}
    for category, values in entities_to_replace.items():
        base = PLACEHOLDER_BASE.get(category, category.upper())
        sorted_values = sorted(values, key=lambda v: v.lower())
        if len(sorted_values) == 1:
            # Single value: no suffix needed
            mapping[sorted_values[0]] = (f"[{base}]", category)
        else:
            for i, value in enumerate(sorted_values):
                label = _index_label(i)
                mapping[value] = (f"[{base}_{label}]", category)
    return mapping


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"Fout bij het lezen van PDF: {e}")
        return ""


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a Word document."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        st.error(f"Fout bij het lezen van Word-document: {e}")
        return ""


def load_spacy_model():
    """Load spaCy NLP model for NER."""
    import spacy
    try:
        return spacy.load("nl_core_news_lg")
    except OSError:
        try:
            return spacy.load("nl_core_news_md")
        except OSError:
            try:
                return spacy.load("nl_core_news_sm")
            except OSError:
                st.warning(
                    "Geen Nederlands spaCy-model gevonden. "
                    "Installeer met: `python -m spacy download nl_core_news_sm`\n\n"
                    "NER-detectie (namen, bedrijven, locaties) is uitgeschakeld. "
                    "Regex-patronen werken nog steeds."
                )
                return None


def detect_entities_spacy(text: str, nlp) -> dict:
    """Detect named entities using spaCy NER."""
    entities = {
        "Persoonsnaam": set(),
        "Bedrijfsnaam": set(),
        "Locatie": set(),
    }
    if nlp is None:
        return entities

    # Process in chunks to handle large documents
    max_len = 100000
    chunks = [text[i:i + max_len] for i in range(0, len(text), max_len)]

    for chunk in chunks:
        doc = nlp(chunk)
        for ent in doc.ents:
            cleaned = ent.text.strip()
            if len(cleaned) < 2:
                continue
            if ent.label_ == "PER" or ent.label_ == "PERSON":
                entities["Persoonsnaam"].add(cleaned)
            elif ent.label_ == "ORG":
                entities["Bedrijfsnaam"].add(cleaned)
            elif ent.label_ in ("LOC", "GPE", "FAC"):
                entities["Locatie"].add(cleaned)

    return entities


def detect_entities_regex(text: str, selected_categories: list) -> dict:
    """Detect entities using regex patterns."""
    found = {}
    for category in selected_categories:
        if category in PATTERNS:
            matches = set(re.findall(PATTERNS[category], text))
            # Filter out very short matches that are likely false positives
            if category == "Studentnummer":
                matches = {m for m in matches if len(m) >= 6}
            if category == "KvK-nummer":
                matches = {m for m in matches if len(m) == 8}
            if matches:
                found[category] = matches
    return found


def anonymize_text(text: str, entities_to_replace: dict) -> tuple:
    """Replace all detected entities with consistent indexed placeholders.

    Returns (anonymized_text, replacement_count, placeholder_mapping).
    The placeholder_mapping maps original values to their assigned placeholders.
    """
    anonymized = text
    total_replacements = 0

    # Build consistent placeholder mapping
    mapping = build_placeholder_mapping(entities_to_replace)

    # Sort by length (longest first) to avoid partial replacements
    sorted_items = sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True)

    for value, (placeholder, category) in sorted_items:
        escaped = re.escape(value)
        pattern = re.compile(escaped, re.IGNORECASE)
        count = len(pattern.findall(anonymized))
        if count > 0:
            anonymized = pattern.sub(placeholder, anonymized)
            total_replacements += count

    return anonymized, total_replacements, mapping


def create_pdf(text: str) -> bytes:
    """Create a PDF from anonymized text."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.units import mm
    from reportlab.lib.enums import TA_LEFT

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=6,
    )
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=14,
        leading=18,
        spaceAfter=12,
        textColor='#c00000',
    )

    story = []
    story.append(Paragraph("Geanonimiseerd Document", title_style))
    story.append(Spacer(1, 6 * mm))

    # Process text line by line
    for line in text.split('\n'):
        safe_line = (
            line.replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
        )
        # Highlight anonymized placeholders in red (match [LABEL] and [LABEL_X])
        _ph_re = re.compile(r'\[([A-Z][A-Z\-]*(?:_[A-Z0-9]+)?)\]')
        parts = _ph_re.split(safe_line)
        if len(parts) > 1:
            rebuilt = ""
            for idx, part in enumerate(parts):
                if idx % 2 == 0:
                    rebuilt += part
                else:
                    rebuilt += f'<font color="#c00000"><b>[{part}]</b></font>'
            safe_line = rebuilt
        if safe_line.strip():
            story.append(Paragraph(safe_line, normal_style))
        else:
            story.append(Spacer(1, 3 * mm))

    doc.build(story)
    return buffer.getvalue()


def create_docx(text: str) -> bytes:
    """Create a Word document from anonymized text."""
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    # Title
    title = doc.add_heading("Geanonimiseerd Document", level=1)
    for run in title.runs:
        run.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)

    # Process text — match any [LABEL] or [LABEL_X] placeholder
    placeholder_pattern = re.compile(r'(\[[A-Z][A-Z\-]*(?:_[A-Z0-9]+)?\])')

    for line in text.split('\n'):
        if not line.strip():
            doc.add_paragraph("")
            continue

        paragraph = doc.add_paragraph()
        parts = placeholder_pattern.split(line)

        for part in parts:
            if placeholder_pattern.match(part):
                run = paragraph.add_run(part)
                run.bold = True
                run.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
                run.font.size = Pt(10)
            else:
                run = paragraph.add_run(part)
                run.font.size = Pt(10)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


# ===================== MAIN APP =====================

st.markdown('<div class="main-header">🔒 Document Anonymizer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">'
    'Upload een document en anonimiseer automatisch gevoelige informatie'
    '</div>',
    unsafe_allow_html=True,
)

# --- Sidebar: Settings ---
with st.sidebar:
    st.markdown("### ⚙️ Instellingen")
    st.markdown("---")

    st.markdown("**Categorieën om te detecteren:**")

    regex_categories = list(PATTERNS.keys())
    ner_categories = ["Persoonsnaam", "Bedrijfsnaam", "Locatie"]

    st.markdown('<div class="category-header">📝 Regex-detectie</div>', unsafe_allow_html=True)
    selected_regex = {}
    for cat in regex_categories:
        selected_regex[cat] = st.checkbox(cat, value=True, key=f"regex_{cat}")

    st.markdown('<div class="category-header">🤖 NER-detectie (spaCy)</div>', unsafe_allow_html=True)
    selected_ner = {}
    for cat in ner_categories:
        selected_ner[cat] = st.checkbox(cat, value=True, key=f"ner_{cat}")

    st.markdown("---")
    st.markdown("**Exportformaat:**")
    export_format = st.radio(
        "Kies formaat",
        ["PDF", "Word (.docx)", "Beide"],
        index=2,
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        '<div class="highlight-box">'
        '💡 <b>Tip:</b> Voor de beste resultaten met namen en '
        'bedrijven, installeer het Nederlandse spaCy-model:<br>'
        '<code>python -m spacy download nl_core_news_sm</code>'
        '</div>',
        unsafe_allow_html=True,
    )

# --- File Upload ---
st.markdown("### 📄 Document uploaden")
uploaded_file = st.file_uploader(
    "Sleep een bestand hierheen of klik om te uploaden",
    type=["pdf", "docx"],
    help="Ondersteunde formaten: PDF (.pdf), Word (.docx)",
)

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    file_name = uploaded_file.name
    file_ext = file_name.rsplit('.', 1)[-1].lower()

    st.markdown(
        f'<div class="success-box">✅ <b>{file_name}</b> succesvol geüpload '
        f'({len(file_bytes) / 1024:.1f} KB)</div>',
        unsafe_allow_html=True,
    )

    # Extract text
    with st.spinner("📖 Tekst extraheren uit document..."):
        if file_ext == "pdf":
            original_text = extract_text_from_pdf(file_bytes)
        elif file_ext == "docx":
            original_text = extract_text_from_docx(file_bytes)
        else:
            st.error("Niet-ondersteund bestandsformaat.")
            st.stop()

    if not original_text.strip():
        st.error(
            "Geen tekst gevonden in het document. "
            "Het bestand is mogelijk een gescande afbeelding. "
            "Gebruik een OCR-tool om het eerst naar tekst om te zetten."
        )
        st.stop()

    # Show original text preview
    with st.expander("👁️ Originele tekst bekijken", expanded=False):
        st.text_area(
            "Originele tekst",
            original_text[:5000] + ("..." if len(original_text) > 5000 else ""),
            height=200,
            disabled=True,
            label_visibility="collapsed",
        )

    # Detect entities
    st.markdown("### 🔍 Detectie & Anonimisering")

    with st.spinner("🔍 Gevoelige informatie detecteren..."):
        # Regex detection
        active_regex_cats = [cat for cat, active in selected_regex.items() if active]
        regex_entities = detect_entities_regex(original_text, active_regex_cats)

        # NER detection
        ner_entities = {}
        active_ner_cats = [cat for cat, active in selected_ner.items() if active]
        if active_ner_cats:
            nlp = load_spacy_model()
            if nlp is not None:
                all_ner = detect_entities_spacy(original_text, nlp)
                ner_entities = {
                    cat: vals for cat, vals in all_ner.items()
                    if cat in active_ner_cats and vals
                }

    # Combine all entities
    all_entities = {}
    all_entities.update(regex_entities)
    all_entities.update(ner_entities)

    # Show detection results
    total_items = sum(len(v) for v in all_entities.values())

    if total_items == 0:
        st.warning(
            "⚠️ Geen gevoelige informatie gedetecteerd. "
            "Het document bevat mogelijk geen herkenbare patronen, "
            "of de tekst kon niet goed worden geëxtraheerd."
        )
    else:
        # Stats row
        cols = st.columns(4)
        categories_found = len(all_entities)
        with cols[0]:
            st.markdown(
                f'<div class="stat-card">'
                f'<div class="stat-number">{total_items}</div>'
                f'<div class="stat-label">Items gevonden</div></div>',
                unsafe_allow_html=True,
            )
        with cols[1]:
            st.markdown(
                f'<div class="stat-card">'
                f'<div class="stat-number">{categories_found}</div>'
                f'<div class="stat-label">Categorieën</div></div>',
                unsafe_allow_html=True,
            )
        with cols[2]:
            words = len(original_text.split())
            st.markdown(
                f'<div class="stat-card">'
                f'<div class="stat-number">{words}</div>'
                f'<div class="stat-label">Woorden totaal</div></div>',
                unsafe_allow_html=True,
            )
        with cols[3]:
            st.markdown(
                f'<div class="stat-card">'
                f'<div class="stat-number">{len(original_text)}</div>'
                f'<div class="stat-label">Tekens totaal</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("")

        # Show found entities per category with option to deselect
        st.markdown("**Gevonden items per categorie:**")
        entities_to_replace = {}

        for category, values in all_entities.items():
            base = PLACEHOLDER_BASE.get(category, category.upper())
            if len(values) == 1:
                preview = f"`[{base}]`"
            else:
                preview = ", ".join(
                    f"`[{base}_{_index_label(i)}]`"
                    for i in range(min(len(values), 3))
                )
                if len(values) > 3:
                    preview += ", ..."
            with st.expander(
                f"{category} — {len(values)} gevonden → {preview}"
            ):
                items_list = sorted(values)
                selected_items = st.multiselect(
                    f"Selecteer items om te anonimiseren ({category})",
                    options=items_list,
                    default=items_list,
                    key=f"select_{category}",
                    label_visibility="collapsed",
                )
                if selected_items:
                    entities_to_replace[category] = set(selected_items)

        # Allow user to add custom terms
        st.markdown("---")
        custom_terms = st.text_area(
            "✏️ Extra termen om te anonimiseren (één per regel)",
            help="Voeg handmatig termen toe die niet automatisch zijn gedetecteerd.",
            height=80,
        )
        if custom_terms.strip():
            custom_list = {
                t.strip() for t in custom_terms.split('\n') if t.strip()
            }
            if custom_list:
                entities_to_replace["Handmatig"] = custom_list

        # Anonymize button
        st.markdown("")
        if st.button("🔒 Document Anonimiseren", type="primary", use_container_width=True):
            if not entities_to_replace:
                st.warning("Geen items geselecteerd om te anonimiseren.")
            else:
                with st.spinner("🔒 Bezig met anonimiseren..."):
                    anonymized_text, replacement_count, ph_mapping = anonymize_text(
                        original_text, entities_to_replace
                    )

                st.markdown(
                    f'<div class="success-box">'
                    f'✅ <b>{replacement_count}</b> vervangingen gemaakt in het document.'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                # Store in session state
                st.session_state["anonymized_text"] = anonymized_text
                st.session_state["replacement_count"] = replacement_count
                st.session_state["placeholder_mapping"] = ph_mapping

        # Show results if available
        if "anonymized_text" in st.session_state:
            anonymized_text = st.session_state["anonymized_text"]

            st.markdown("### 📋 Geanonimiseerd resultaat")

            with st.expander("👁️ Geanonimiseerde tekst bekijken", expanded=True):
                st.text_area(
                    "Geanonimiseerde tekst",
                    anonymized_text[:5000] + (
                        "..." if len(anonymized_text) > 5000 else ""
                    ),
                    height=300,
                    disabled=True,
                    label_visibility="collapsed",
                )

            # Show placeholder legend
            if "placeholder_mapping" in st.session_state and st.session_state["placeholder_mapping"]:
                with st.expander("🔑 Placeholder-legenda", expanded=False):
                    ph_map = st.session_state["placeholder_mapping"]
                    # Group by category
                    by_cat = {}
                    for orig, (ph, cat) in ph_map.items():
                        by_cat.setdefault(cat, []).append((orig, ph))
                    for cat, items in sorted(by_cat.items()):
                        st.markdown(f"**{cat}:**")
                        for orig, ph in sorted(items, key=lambda x: x[1]):
                            st.markdown(f"- `{ph}` ← {orig}")

            # Download buttons
            st.markdown("### 💾 Downloaden")
            dl_cols = st.columns(2)

            if export_format in ["PDF", "Beide"]:
                with dl_cols[0]:
                    with st.spinner("PDF genereren..."):
                        pdf_bytes = create_pdf(anonymized_text)
                    base_name = file_name.rsplit('.', 1)[0]
                    st.download_button(
                        label="📥 Download als PDF",
                        data=pdf_bytes,
                        file_name=f"{base_name}_geanonimiseerd.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

            if export_format in ["Word (.docx)", "Beide"]:
                with dl_cols[1]:
                    with st.spinner("Word-document genereren..."):
                        docx_bytes = create_docx(anonymized_text)
                    base_name = file_name.rsplit('.', 1)[0]
                    st.download_button(
                        label="📥 Download als Word",
                        data=docx_bytes,
                        file_name=f"{base_name}_geanonimiseerd.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )

else:
    # Landing state
    st.markdown("")
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.markdown(
            """
            <div style="text-align: center; padding: 3rem 1rem;
                        background: #f8f9fa; border-radius: 16px;
                        border: 2px dashed #ccc;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📄🔒</div>
                <div style="font-size: 1.2rem; font-weight: 700; color: #37474f;
                            margin-bottom: 0.5rem;">
                    Upload een document om te beginnen
                </div>
                <div style="color: #888; font-size: 0.9rem;">
                    Ondersteunde formaten: PDF, Word (.docx)
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")
    st.markdown("### 🛡️ Wat wordt er gedetecteerd?")

    detect_cols = st.columns(3)
    with detect_cols[0]:
        st.markdown(
            """
            **Persoonsgegevens**
            - Persoonsnamen
            - E-mailadressen
            - Telefoonnummers
            - BSN-nummers
            - Geboortedata
            """
        )
    with detect_cols[1]:
        st.markdown(
            """
            **Organisatie & Onderwijs**
            - Bedrijfsnamen
            - KvK-nummers
            - Studentnummers
            - IBAN-nummers
            """
        )
    with detect_cols[2]:
        st.markdown(
            """
            **Locatiegegevens**
            - Adressen
            - Postcodes
            - Steden & locaties
            """
        )

    st.markdown("---")
    st.markdown(
        '<div class="highlight-box">'
        '🔒 <b>Privacy:</b> Alle verwerking gebeurt lokaal op uw computer. '
        'Er worden geen gegevens naar externe servers gestuurd.'
        '</div>',
        unsafe_allow_html=True,
    )

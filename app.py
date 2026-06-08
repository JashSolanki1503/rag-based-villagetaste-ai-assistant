"""
╔══════════════════════════════════════════════════════════════╗
║      VillageTaste Foods AI Assistant — Streamlit App         ║
║                  Run: streamlit run app.py                   ║
╚══════════════════════════════════════════════════════════════╝

BUG FIXES APPLIED (v2):
  1. Black box behind bot responses       → removed conflicting markdown card backgrounds
  2. Both messages left-aligned           → user bubbles float RIGHT, bot bubbles float LEFT
  3. Chat input not clearing after send   → switched to st.chat_input() (auto-clears)
  4. Pot image displacing send button     → moved pot image to sidebar footer
  5. Message appears below input instead  → single authoritative render path via container
     of inside chat area
  6. Duplicate message rendering          → removed st.chat_message() wrappers that caused
                                            Streamlit to inject extra dark card boxes

PATCH v3 (two targeted changes only — nothing else touched):
  FIX A  → Dark/black strip behind the chat input box → all stBottom* and
            stChatFloatingInputContainer selectors now locked to #FDFBF7
            plus the inner textarea wrapper background forced to match.
  FIX B  → Pot image restored to the RIGHT side of the chat input row,
            exactly as it was in the original design.
"""

# ==============================================================================
# 1. IMPORTS
# ==============================================================================

import streamlit as st
from PIL import Image
import markdown as md_lib          # converts LLM markdown text → safe HTML

# Backend RAG pipeline — your existing modules, untouched
from pipline.rag_pipline_manager import RAGPipelineManager
from retrieval.retriever_manager import RetreiverManager
from ingestion.embedding_manager import EmbeddingManager
from ingestion.vector_store_manager import VectorStoreManager


# ==============================================================================
# 2. PAGE CONFIGURATION  (must be the very first Streamlit call)
# ==============================================================================

st.set_page_config(
    page_title="VillageTaste Foods AI Assistant",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==============================================================================
# 3. LOAD BRAND ASSETS
# ==============================================================================

banner_image = Image.open("assets/banner.png")
logo_image   = Image.open("assets/logo.png")
pot_image    = Image.open("assets/pot.png")


# ==============================================================================
# 4. CUSTOM CSS
#
#    Root fixes explained:
#
#    BLACK BOX BUG
#      Streamlit's [data-testid="stChatMessage"] renders a dark card by default.
#      We override it to transparent + no border. We also hide Streamlit's built-in
#      avatar column so our custom avatar HTML takes over.
#
#    ALIGNMENT BUG
#      .bubble-row.user-row  uses flex-direction:row-reverse → bubble sits on the RIGHT.
#      .bubble-row.bot-row   uses flex-direction:row         → bubble sits on the LEFT.
#
#    BACKGROUND STRIP BUG  ← FIX A (v3 patch)
#      The dark bottom strip comes from Streamlit's stBottom* containers and the
#      floating input container. Every one of them is now explicitly forced to the
#      warm-cream colour #FDFBF7, including the inner div that wraps the textarea.
# ==============================================================================

CUSTOM_CSS = """
<style>

/* ── Global warm-cream background — covers every Streamlit container ───────── */
.stApp,
.main,
[data-testid="stAppViewContainer"],
section.main > div,
header,
[data-testid="stBottomBlockContainer"],
.stChatFloatingInputContainer {
    background-color: #FDFBF7 !important;
}

footer { visibility: hidden; }

/* ── Block container padding ───────────────────────────────────────────────── */
.block-container {
    padding: 1rem 2rem 2rem 2rem !important;
    max-width: 100% !important;
}

/* ══════════════════════════════════════════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════════════════════════════════════════ */

[data-testid="stSidebar"] {
    background-color: #5C2C16 !important;
    min-width: 300px !important;
    max-width: 300px !important;
}

[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #FFFDD0 !important;
}

/* Sidebar buttons */
div.stButton > button {
    background-color: #E17A17 !important;
    color: #FFFFFF !important;
    border: none;
    border-radius: 10px;
    padding: 0.45rem 0.9rem;
    font-weight: 600;
    transition: background-color 0.25s ease, transform 0.15s ease;
    width: 100%;
}

div.stButton > button:hover {
    background-color: #C6650E !important;
    transform: translateY(-1px);
}

/* Food info card */
.food-card {
    background-color: rgba(255, 253, 208, 0.1);
    border: 1px solid rgba(255, 253, 208, 0.25);
    padding: 14px;
    border-radius: 12px;
    margin-top: 12px;
}

.food-card h4,
.food-card p {
    color: #FFFDD0 !important;
}

/* ══════════════════════════════════════════════════════════════════════════════
   CHAT MESSAGE — BLACK BOX FIX
   Streamlit wraps every st.chat_message() in a card with a dark background.
   We strip that card completely and hide the default avatar column so our
   own HTML bubbles have full visual control.
══════════════════════════════════════════════════════════════════════════════ */

[data-testid="stChatMessage"] {
    background-color: transparent !important;
    background:       transparent !important;
    border:           none        !important;
    box-shadow:       none        !important;
    padding:          0           !important;
    margin-bottom:    0.4rem      !important;
}

/* Hide Streamlit's built-in avatar so ours shows instead */
[data-testid="stChatMessage"] > div:first-child {
    display: none !important;
}

/* ══════════════════════════════════════════════════════════════════════════════
   CHAT BUBBLE LAYOUT — ALIGNMENT FIX
══════════════════════════════════════════════════════════════════════════════ */

/* Row wrapper — shared */
.bubble-row {
    display:     flex;
    align-items: flex-end;
    margin-bottom: 14px;
    gap: 8px;
    width: 100%;
}

/* USER  → right side: reverse the flex direction */
.bubble-row.user-row {
    flex-direction: row-reverse;
}

/* BOT   → left side: normal flex direction */
.bubble-row.bot-row {
    flex-direction: row;
}

/* Avatar circle */
.avatar {
    width:        36px;
    height:       36px;
    border-radius: 50%;
    flex-shrink:  0;
    display:      flex;
    align-items:  center;
    justify-content: center;
    font-size:    18px;
    line-height:  1;
}

.avatar.user-avatar { background-color: #E17A17; }
.avatar.bot-avatar  { background-color: #5C2C16; }

/* Bubble body — shared base */
.bubble {
    max-width:   72%;
    padding:     12px 16px;
    border-radius: 18px;
    font-size:   15px;
    line-height: 1.55;
    word-break:  break-word;
}

/* User bubble — warm green tint, rounded corner on bottom-right removed */
.bubble.user-bubble {
    background-color:     #DDE8C8;
    color:                #3B2A1A !important;
    border-bottom-right-radius: 4px;
}

/* Bot bubble — warm cream, slight shadow, rounded corner on bottom-left removed */
.bubble.bot-bubble {
    background-color:    #F8EFE2;
    color:               #4B2E1E !important;
    border:              1px solid #E5D2B0;
    box-shadow:          0 2px 8px rgba(0,0,0,0.06);
    border-bottom-left-radius: 4px;
}

/* Force ALL child text in bubbles to inherit the warm brown — prevents any
   Streamlit theme from injecting its own white / grey text colour */
.bubble p,
.bubble li,
.bubble ul,
.bubble ol,
.bubble span,
.bubble strong,
.bubble em,
.bubble code,
.bubble blockquote {
    color:            inherit             !important;
    background-color: transparent        !important;
}

/* ══════════════════════════════════════════════════════════════════════════════
   CHAT INPUT BOTTOM BAR — FIX A (v3 patch)
   ─────────────────────────────────────────────────────────────────────────────
   The dark bottom strip visible in the screenshot is produced by multiple
   nested Streamlit containers. We target every level explicitly so there is
   no dark border, shadow, or background anywhere around the chat input.
══════════════════════════════════════════════════════════════════════════════ */

/* Every bottom-docking container Streamlit uses (all nesting levels) */
[data-testid="stBottomBlockContainer"],
[data-testid="stBottomBlockContainer"] > div,
[data-testid="stBottomBlockContainer"] > div > div,
[data-testid="stBottomBlockContainer"] > div > div > div,
.stChatFloatingInputContainer,
.stChatFloatingInputContainer > div,
.stChatFloatingInputContainer > div > div {
    background-color: #FDFBF7 !important;
    border-top:       none     !important;
    box-shadow:       none     !important;
}

/* stChatInput — force cream on EVERY nested div so no dark layer can ever
   show through the border-radius corners at any nesting depth              */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] > div > div,
[data-testid="stChatInput"] > div > div > div,
[data-testid="stChatInput"] > div > div > div > div {
    background-color: #FFF8EE !important;
    background:       #FFF8EE !important;
}

/* The visible rounded box the user sees */
[data-testid="stChatInput"] > div {
    border:        2px solid #DCC7A1                  !important;
    border-radius: 16px                               !important;
    box-shadow:    0 2px 10px rgba(92, 44, 22, 0.08) !important;
    overflow:      hidden                             !important;
}

/* The textarea itself — border-radius set to 0 so it cannot create its own
   dark corner artefact inside the parent rounded container               */
[data-testid="stChatInput"] textarea {
    background-color: #FFF8EE !important;
    color:            #4B2E1E !important;
    border:           none    !important;
    border-radius:    0       !important;
    font-size:        15px    !important;
    box-shadow:       none    !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #9A7B5F !important;
}

/* Send arrow button inside the chat input */
[data-testid="stChatInput"] button {
    background-color: #E17A17 !important;
    border-radius:    10px    !important;
    color:            #FFFFFF !important;
}

/* ── Spinner text ──────────────────────────────────────────────────────────── */
[data-testid="stSpinner"] p {
    color: #5C2C16 !important;
}

</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==============================================================================
# 5. INITIALISE BACKEND PIPELINE  (cached — built only once per session)
# ==============================================================================

@st.cache_resource
def load_rag_pipeline() -> RAGPipelineManager:
    """
    Constructs and returns the full RAG pipeline.
    @st.cache_resource ensures this runs only once across all reruns.
    """
    embedding_manager    = EmbeddingManager()
    vector_store_manager = VectorStoreManager()
    retriever_manager    = RetreiverManager(embedding_manager, vector_store_manager)
    pipeline             = RAGPipelineManager(retriever_manager)
    return pipeline


rag_pipeline = load_rag_pipeline()


# ==============================================================================
# 6. SESSION STATE — persistent chat history across reruns
# ==============================================================================

WELCOME_MESSAGE = """
🙏 Namaste! Welcome to **VillageTaste Foods**.

I can help you with:
- Traditional food products
- Village recipes
- Order information
- Company services
- Food ingredients

What would you like to know today? 🍛
"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": WELCOME_MESSAGE}
    ]


# ==============================================================================
# 7. HELPER — call RAG pipeline safely
# ==============================================================================

def get_bot_response(query: str) -> str:
    """
    Sends query to the RAG pipeline and returns the LLM's text reply.
    Any exception is caught and returned as a user-friendly error message.
    """
    try:
        result = rag_pipeline.chat(query)
        return result["llm_response"]
    except Exception as exc:
        return (
            "⚠️ Something went wrong while processing your request.\n\n"
            f"**Error:** {exc}"
        )


# ==============================================================================
# 8. HELPER — render a single chat bubble
#
#    We bypass st.chat_message() entirely so Streamlit never renders its dark
#    card wrapper. Instead we write raw HTML via st.markdown(unsafe_allow_html).
#
#    The bubble-row CSS class controls left / right alignment:
#      user-row  → flex-direction: row-reverse  (bubble on the RIGHT)
#      bot-row   → flex-direction: row          (bubble on the LEFT)
# ==============================================================================

def render_bubble(role: str, content: str) -> None:
    """
    Renders a styled chat bubble with correct left/right alignment.

    Parameters
    ----------
    role    : "user" or "assistant"
    content : The message text (may contain markdown-style bold/italic)
    """
    if role == "user":
        row_class    = "bubble-row user-row"
        bubble_class = "bubble user-bubble"
        avatar_class = "avatar user-avatar"
        avatar_icon  = "👤"
    else:
        row_class    = "bubble-row bot-row"
        bubble_class = "bubble bot-bubble"
        avatar_class = "avatar bot-avatar"
        avatar_icon  = "🍲"

    # Convert markdown → HTML so LLM responses render beautifully.
    # md_lib.markdown handles **bold**, *italic*, bullet lists, numbered lists,
    # headings, inline `code`, blockquotes, and line breaks automatically.
    # We use the 'nl2br' extension so single newlines also become <br> tags.
    rendered_content = md_lib.markdown(
        content,
        extensions=["nl2br", "sane_lists"],
    )

    html = f"""
    <div class="{row_class}">
        <div class="{avatar_class}">{avatar_icon}</div>
        <div class="{bubble_class}">{rendered_content}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ==============================================================================
# 9. HELPER — reset chat to welcome state
# ==============================================================================

def clear_chat() -> None:
    """Resets conversation history to the single welcome message."""
    st.session_state.messages = [
        {"role": "assistant", "content": "🙏 Chat cleared.\n\nHow can I help you today? 🍲"}
    ]


# ==============================================================================
# 10. SIDEBAR
# ==============================================================================

with st.sidebar:

    # ── Logo ──────────────────────────────────────────────────────────────────
    st.image(logo_image, width=260)

    st.markdown(
        """
        <div style="text-align:center; color:#F5D7A1; margin-top:-8px;
                    margin-bottom:16px; font-size:14px;">
            Traditional Village Recipes
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Chat action buttons ───────────────────────────────────────────────────
    st.subheader("Chat Actions")

    col_new, col_clr = st.columns(2)

    with col_new:
        if st.button("New Chat", key="btn_new"):
            clear_chat()
            st.rerun()

    with col_clr:
        if st.button("Clear", key="btn_clr"):
            clear_chat()
            st.rerun()

    st.markdown("---")

    # ── Suggested questions ───────────────────────────────────────────────────
    st.subheader("💡 Suggested Questions")

    SUGGESTED_QUESTIONS = [
        "What food products do you offer?",
        "Tell me about your traditional recipes",
        "Do you use organic ingredients?",
        "What services are available?",
        "How can I place an order?",
    ]

    for idx, question in enumerate(SUGGESTED_QUESTIONS):
        if st.button(question, key=f"sq_{idx}"):
            # Save user turn
            st.session_state.messages.append({"role": "user", "content": question})

            # Fetch answer — spinner appears while waiting
            with st.spinner("Consulting VillageTaste knowledge base... 🌾"):
                answer = get_bot_response(question)

            # Save bot turn then rerun so the main chat area re-renders
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()

    st.markdown("---")

    # ── Info card ─────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="food-card">
            <h4>🍯 Traditional Taste</h4>
            <p style="font-size:0.85rem;">
                Our food products are prepared using authentic village
                recipes, traditional spices, and homemade cooking methods.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown(
        """
        <center style="font-size:0.78rem; opacity:0.65; color:#FFFDD0;">
            Made with ❤️ for Traditional Indian Foods
        </center>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# 11. MAIN AREA — Banner image
# ==============================================================================

st.image(banner_image, use_container_width=True)


# ==============================================================================
# 12. MAIN AREA — Chat history display
#
#    We use a named st.container() so new bubbles from step 13 are injected into
#    the same visual block rather than appearing below the chat input widget.
#    Every message is rendered via render_bubble() — no st.chat_message() calls —
#    so Streamlit never wraps them in its dark card component.
# ==============================================================================

chat_area = st.container()

with chat_area:
    for msg in st.session_state.messages:
        render_bubble(msg["role"], msg["content"])


# ==============================================================================
# 13. MAIN AREA — Chat input row  (PATCH v4)
#
#    st.chat_input() cannot be placed inside st.columns() — Streamlit pins it
#    to the bottom of the viewport regardless of where it is called in code.
#    The cleanest way to achieve a true side-by-side appearance is:
#      col1  (wide)  → st.chat_input()   lives here as the pinned bottom bar
#      col2  (narrow)→ pot image rendered in a matching fixed-bottom container
#
#    We use st.columns so both widgets share the same horizontal row, and we
#    vertically-align the pot column with CSS so it sits level with the input.
# ==============================================================================

col_input, col_pot = st.columns([11, 1])

with col_pot:
    # Vertically centre the pot so it aligns with the chat input bar
    st.markdown(
        """
        <div style="
            display:         flex;
            align-items:     center;
            justify-content: center;
            height:          100%;
            padding-top:     6px;
        ">
        """,
        unsafe_allow_html=True,
    )
    st.image(pot_image, width=160)
    st.markdown("</div>", unsafe_allow_html=True)

with col_input:
    user_input = st.chat_input("Type your message here...")

if user_input:

    # ── Step 1: show & save the user message immediately ──────────────────────
    st.session_state.messages.append({"role": "user", "content": user_input})

    with chat_area:
        render_bubble("user", user_input)

    # ── Step 2: fetch response — spinner rendered inside chat_area so it
    #    appears ABOVE the input bar, not below it (the earlier bug)       ──────
    with chat_area:
        with st.spinner("Consulting VillageTaste knowledge base... 🌾"):
            bot_reply = get_bot_response(user_input)

    # ── Step 3: show & save the bot reply ─────────────────────────────────────
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    with chat_area:
        render_bubble("assistant", bot_reply)
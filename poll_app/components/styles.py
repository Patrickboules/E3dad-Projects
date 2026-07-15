"""
Centralized styling for the E3dad Projects app.

Exposes:
  - inject_styles():        call once from the entry point to load the
                            orange / light-mode / RTL stylesheet.
  - option_click_js():      JavaScript injected in the topic step that maps a
                            card click to the matching Streamlit button and
                            pins light mode every 500ms.
"""

import streamlit as st


THEME = """
<style>
    :root {
        --primary-color: #FF5722;
        --hover-color: #FFF3E0;
        --selected-color: #FFE0B2;
        --border-color: #E64A19;
        --disabled-color: #F5F5F5;
        --text-color: #333333;
        --count-color: #666666;
        --success-bg: #E8F5E9;
        --success-border: #2E7D32;
        --error-bg: #FFEBEE;
        --error-border: #F44336;
        --header-color: #FF9800;
        --custom-topic-bg: #E3F2FD;
        --custom-topic-selected: #BBDEFB;
    }

    /* Force light mode */
    html, body, [class*="css"] {
        color: var(--text-color) !important;
        background-color: white !important;
    }
    * { color: var(--text-color) !important; }
    .stApp { background-color: white !important; }

    /* Arabic RTL direction on the whole document */
    body, .stApp, [data-testid="stAppViewContainer"] {
        direction: rtl;
    }

    /* Topic option cards (visual containers; buttons do the work) */
    .option-container {
        display: flex;
        flex-direction: column;
        margin: 8px 0;
        padding: 12px 15px;
        border-radius: 10px;
        transition: all 0.3s ease;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #E0E0E0;
        width: 100%;
    }
    .option-container:hover {
        background-color: var(--hover-color);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(255, 152, 0, 0.1);
    }
    .option-container.selected {
        background-color: var(--selected-color);
        border-right: 5px solid var(--border-color);
        box-shadow: 0 4px 8px rgba(255, 87, 34, 0.2);
    }
    .option-container.disabled {
        opacity: 0.7;
        pointer-events: none;
        background-color: var(--disabled-color);
    }
    .option-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        margin-bottom: 8px;
    }
    .option-text {
        text-align: right;
        font-size: 16px;
        color: var(--text-color);
        width: 100%;
        padding: 5px 0;
    }
    .progress-container {
        width: 100%;
        height: 20px;
        background-color: #F5F5F5;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
    }
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, var(--primary-color), #FF8A65);
        width: 0%;
        transition: width 0.5s ease;
    }
    .complete {
        background: linear-gradient(90deg, var(--border-color), var(--primary-color));
    }
    .option-number {
        font-weight: bold;
        font-size: 16px;
        color: var(--text-color);
    }
    .count-display {
        font-size: 13px;
        color: var(--count-color);
        font-weight: 500;
    }

    .required-field::after {
        content: " *";
        color: red;
        position: absolute;
        margin-right: 2px;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        padding: 8px 16px;
        transition: all 0.3s;
        background-color: var(--primary-color);
        color: white !important;
        border: none;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(255, 87, 34, 0.3);
    }
    .stButton>button:disabled {
        background-color: #cccccc !important;
        cursor: not-allowed;
    }

    .header {
        color: var(--header-color);
        margin-bottom: 20px;
    }

    /* Messages */
    .success-message {
        background-color: var(--success-bg);
        border-right: 5px solid var(--success-border);
        font-size: 18px;
        padding: 15px;
        border-radius: 8px;
        color: #333333;
        margin: 20px 0;
    }
    .error-message {
        background-color: var(--error-bg);
        border-right: 5px solid var(--error-border);
        font-size: 16px;
        padding: 10px;
        border-radius: 6px;
        color: #333333;
        margin: 10px 0;
    }

    /* Custom topic card */
    .custom-topic-container {
        background-color: var(--custom-topic-bg);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #BBDEFB;
        transition: all 0.3s ease;
    }
    .custom-topic-selected {
        background-color: var(--custom-topic-selected);
        border-right: 5px solid var(--border-color);
    }

    /* Phone verification container */
    .phone-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        background-color: white;
    }
    .phone-verification-container {
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        background-color: #ffffff;
    }
    .phone-header {
        text-align: center;
        color: #2c3e50;
        margin-bottom: 25px;
    }
    .phone-instructions {
        text-align: center;
        color: #7f8c8d;
        margin-bottom: 30px;
        font-size: 16px;
        line-height: 1.5;
    }
    .existing-data-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin: 20px 0;
        border-right: 4px solid #3498db;
    }
    .data-item { margin-bottom: 8px; display: flex; }
    .data-label { font-weight: bold; min-width: 120px; color: #2c3e50; }
    .data-value { flex-grow: 1; color: #34495e; }

    /* Inputs */
    .stTextInput>div>div>input {
        color: #333333 !important;
        background-color: white !important;
        border: 1px solid #E0E0E0 !important;
    }
    .stTextInput input {
        text-align: right;
        direction: rtl;
        padding: 12px;
        font-size: 16px;
        width: 100%;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .option-text { font-size: 14px; }
        .option-number, .count-display { font-size: 14px; }
        .progress-container { height: 15px; }
        .stButton>button { padding: 10px; font-size: 14px; }
        .stTextInput>div>div>input { font-size: 14px; }
        .phone-container, .phone-verification-container { padding: 20px; }
    }

    /* Dark mode suppression */
    [data-testid="stAppViewContainer"] { background-color: white !important; }
    [data-testid="stHeader"] { background-color: white !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
</style>
"""


def inject_styles() -> None:
    """Inject the application stylesheet. Call once from the entry point."""
    st.markdown(THEME, unsafe_allow_html=True)


def option_click_js() -> str:
    """
    JavaScript injected in the topic step:
      - handleClick(num): when an option card is clicked, clicks the
        matching "اختر" Streamlit button.
      - enforceLightMode(): pins light mode on load and every 500ms.
    """
    return """
<script>
function handleClick(optionNum) {
    const buttons = parent.document.querySelectorAll('button[title="اختر"]');
    buttons.forEach(button => {
        if (button.getAttribute("data-testid") &&
            button.getAttribute("data-testid").includes(optionNum)) {
            button.click();
        }
    });
}

function enforceLightMode() {
    document.documentElement.style.backgroundColor = '#ffffff';
    document.documentElement.style.colorScheme = 'light';
    document.body.style.backgroundColor = '#ffffff';
    document.body.classList.remove('dark');
    const darkModeToggle = document.querySelector('[data-testid="stToolbar"]');
    if (darkModeToggle) darkModeToggle.style.display = 'none';
}

window.addEventListener('load', enforceLightMode);
setInterval(enforceLightMode, 500);
</script>
"""

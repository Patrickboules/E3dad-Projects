import streamlit as st
from streamlit.components.v1 import html
import json
from github import Github

# Configure page - disable dark mode
st.set_page_config(
    layout="wide",
    page_title="مشاريع اعداد 2025",
    page_icon="📊",
    initial_sidebar_state="collapsed"
)

# Force light mode
st.markdown("""
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
    
    html, body, [class*="css"] {
        color: var(--text-color) !important;
        background-color: white !important;
    }
    
    * {
        color: var(--text-color) !important;
    }
    
    .stApp {
        background-color: white !important;
    }
    
    .option-container {
        display: flex;
        flex-direction: column;
        margin: 8px 0;
        padding: 12px 15px;
        border-radius: 10px;
        transition: all 0.3s ease;
        cursor: pointer;
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
        border-left: 5px solid var(--border-color);
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
        margin-left: 2px;
    }
    
    .stButton>button {
        border-radius: 8px;
        padding: 8px 16px;
        transition: all 0.3s;
        width: 100%;
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
    
    .success-message {
        background-color: var(--success-bg);
        border-left: 5px solid var(--success-border);
        font-size: 18px;
        padding: 15px;
        border-radius: 8px;
        color: #333333;
        margin: 20px 0;
    }
    
    .error-message {
        background-color: var(--error-bg);
        border-left: 5px solid var(--error-border);
        font-size: 16px;
        padding: 10px;
        border-radius: 6px;
        color: #333333;
        margin: 10px 0;
    }
    
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
        border-left: 5px solid var(--border-color);
    }
    
    .custom-topic-input {
        display: flex;
        gap: 10px;
        align-items: center;
    }
    
    .custom-topic-input input {
        flex-grow: 1;
    }
    
    .custom-topic-input button {
        flex-shrink: 0;
        width: 100px !important;
        height: 38px;
        margin-top: 10px;
    }
    
    /* Input fields */
    .stTextInput>div>div>input {
        color: #333333 !important;
        background-color: white !important;
        border: 1px solid #E0E0E0 !important;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .option-text {
            font-size: 14px;
        }
        
        .option-number, .count-display {
            font-size: 14px;
        }
        
        .progress-container {
            height: 15px;
        }
        
        .stButton>button {
            padding: 10px;
            font-size: 14px;
        }
        
        .stTextInput>div>div>input {
            font-size: 14px;
        }
        
        .custom-topic-input {
            flex-direction: column;
        }
        
        .custom-topic-input button {
            width: 100% !important;
        }
    }
    
    /* Disable dark mode */
    [data-testid="stAppViewContainer"] {
        background-color: white !important;
    }
    
    [data-testid="stHeader"] {
        background-color: white !important;
    }
    
    [data-testid="stToolbar"] {
        display: none !important;
    }
    
    [data-testid="stDecoration"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 مشاريع اعداد 2025")

# Initialize session state with clearer structure
def initialize_session_state():
    if 'form' not in st.session_state:
        st.session_state.form = {
            'selected_option': None,
            'custom_topic': '',
            'is_custom_selected': False,
            'first_name': '',
            'last_name': '',
            'submitted': False,
            'temp_counts': {}
        }

initialize_session_state()

# GitHub configuration
REPO_NAME = "Patrickboules/E3dad-Projects"
FILE_PATH = "responses.json"

# Define all 22 options
options = {
    1: "البدع والهرطقات",
    2: "الآباء الرسل",
    3: "أبطال الإيمان",
    4: "السيدات في الكتاب المقدس",
    5: "الصلاة",
    6: "القداس",
    7: "حياة القديسين في الكتاب المقدس",
    8: "الملائكة",
    9: "الذبائح",
    10: "الرهبنة",
    11: "الكهنوت",
    12: "نعمة",
    13: "إسلاميات",
    14: "قبول ومحبة الآخر",
    15: "البناء النفسي للخادم",
    16: "الإتيكيت",
    17: "علامات النضج",
    18: "الطاعة والالتزام والتلمذة",
    19: "الفتور الروحي والتغلب عليه",
    20: "آداب معاملة الآخرين (أصغر/أكبر/نفس السن)",
    21: "النضج وأهميته",
    22: "الارتباط ضرورة ولكن بشروط"
}

# Load existing responses from GitHub
@st.cache_data(ttl=5)
def load_topic_counts():
    topic_counts = {num: 0 for num in options.keys()}
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(REPO_NAME)
        file = repo.get_contents(FILE_PATH)
        existing_data = json.loads(file.decoded_content.decode())
        
        for response in existing_data:
            for num, text in options.items():
                if text == response.get("Topic"):
                    topic_counts[num] += 1
                    break
    except Exception as e:
        st.error(f"حدث خطأ في تحميل البيانات من GitHub: {str(e)}")
    return topic_counts

# Combine saved counts with temporary selections
def get_combined_counts():
    saved_counts = load_topic_counts()
    combined = saved_counts.copy()
    for num, count in st.session_state.form['temp_counts'].items():
        combined[num] += count
    return combined

# Save response to GitHub
def save_response():
    topic = options[st.session_state.form['selected_option']] if st.session_state.form['selected_option'] else st.session_state.form['custom_topic']
    response = {
        "First Name": st.session_state.form['first_name'],
        "Last Name": st.session_state.form['last_name'],
        "Topic": topic
    }
    
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(REPO_NAME)
        file = repo.get_contents(FILE_PATH)
        
        existing_data = json.loads(file.decoded_content.decode())
        existing_data.append(response)
        
        repo.update_file(
            path=FILE_PATH,
            message=f"إضافة اختيار جديد من {st.session_state.form['first_name']}",
            content=json.dumps(existing_data, indent=4, ensure_ascii=False),
            sha=file.sha
        )
        
        st.session_state.form['temp_counts'] = {}
        return True
    except Exception as e:
        st.error(f"حدث خطأ في حفظ البيانات على GitHub: {str(e)}")
        return False

def handle_option_selection(option_num):
    """Handle selection of a predefined option"""
    # Clear any custom selection
    st.session_state.form['custom_topic'] = ''
    st.session_state.form['is_custom_selected'] = False
    
    # Update counts for previous selection if exists
    if st.session_state.form['selected_option'] is not None:
        prev_option = st.session_state.form['selected_option']
        st.session_state.form['temp_counts'][prev_option] = st.session_state.form['temp_counts'].get(prev_option, 0) - 1
    
    # Set new selection
    st.session_state.form['selected_option'] = option_num
    st.session_state.form['temp_counts'][option_num] = st.session_state.form['temp_counts'].get(option_num, 0) + 1
    st.rerun()

def handle_custom_topic():
    """Handle custom topic input and selection"""
    # Clear any predefined selection
    if st.session_state.form['selected_option'] is not None:
        prev_option = st.session_state.form['selected_option']
        st.session_state.form['temp_counts'][prev_option] = st.session_state.form['temp_counts'].get(prev_option, 0) - 1
        st.session_state.form['selected_option'] = None
    
    # Update custom topic state
    custom_text = st.session_state.custom_topic_input.strip()
    st.session_state.form['custom_topic'] = custom_text
    st.session_state.form['is_custom_selected'] = bool(custom_text)
    st.rerun()

def create_option(num, text):
    combined_counts = get_combined_counts()
    count = combined_counts.get(num, 0)
    max_limit = 3
    progress = (count / max_limit) * 100
    disabled = count >= max_limit
    
    # Determine if this option is selected
    selected = (st.session_state.form['selected_option'] == num and 
               not st.session_state.form['is_custom_selected'])
    
    container = st.container()
    container.markdown(
        f"""
        <div class="option-container {'selected' if selected else ''} {'disabled' if disabled and not selected else ''}" 
             id="option_{num}"
             onclick="handleClick({num})">
            <div class="option-header">
                <div class="option-number">{num}.</div>
                <div class="count-display">({count}/{max_limit})</div>
            </div>
            <div class="option-text">{text}</div>
            <div class="progress-container">
                <div class="progress-bar {'complete' if count >= max_limit else ''}" style="width:{progress}%"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if not disabled and container.button("اختر", key=f"select_{num}"):
        handle_option_selection(num)

def create_custom_topic_input():
    selected = (st.session_state.form['is_custom_selected'] and 
               st.session_state.form['custom_topic'].strip())
    
    container_class = "custom-topic-container"
    if selected:
        container_class += " custom-topic-selected"
    
    st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)
    st.markdown("**أو اكتب موضوعًا مخصصًا:**")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.text_input(
            "موضوع مخصص",
            value=st.session_state.form['custom_topic'],
            key="custom_topic_input",
            label_visibility="collapsed",
            placeholder="اكتب موضوعًا مخصصًا إذا لم تجد ما تبحث عنه",
            on_change=handle_custom_topic
        )
    with col2:
        if st.button("اختر", key="select_custom", use_container_width=True):
            handle_custom_topic()
    
    st.markdown('</div>', unsafe_allow_html=True)

def option_click_js():
    return """
    <script>
    function handleClick(optionNum) {
        const buttons = parent.document.querySelectorAll('button[title="اختر"]');
        buttons.forEach(button => {
            if (button.textContent.includes("اختر") && 
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

    // Initial call and interval check
    window.addEventListener('load', enforceLightMode);
    setInterval(enforceLightMode, 500);
    </script>
    """

def main():
    if not st.session_state.form['submitted']:
        with st.container():
            st.subheader("المجموعة")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<span class="required-field">اسم المخدوم رقم 1</span>', unsafe_allow_html=True)
                st.session_state.form['first_name'] = st.text_input(
                    "اسم المخدوم رقم 1", 
                    value=st.session_state.form['first_name'],
                    key="first_name_input",
                    label_visibility="collapsed",
                    placeholder="أدخل الاسم الأول"
                )
            with col2:
                st.markdown("اسم المخدوم رقم 2")
                st.session_state.form['last_name'] = st.text_input(
                    "اسم المخدوم رقم 2", 
                    value=st.session_state.form['last_name'],
                    key="last_name_input",
                    label_visibility="collapsed",
                    placeholder="أدخل الاسم الثاني"
                )
            
            create_custom_topic_input()
            st.markdown("---")
    
    if st.session_state.form['submitted']:
        topic = (options[st.session_state.form['selected_option']] 
                if st.session_state.form['selected_option'] 
                else st.session_state.form['custom_topic'])
        st.markdown(
            f"""
            <div class="success-message">
                <h3>شكرًا لك {st.session_state.form['first_name']}!</h3>
                <p>لقد اخترت: <strong>{topic}</strong></p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return
    
    st.markdown('<h2 class="header">الرجاء اختيار موضوع واحد من المواضيع التالية:</h2>', unsafe_allow_html=True)
    
    for num, text in options.items():
        create_option(num, text)
    
    html(option_click_js(), height=0)
    st.markdown("---")
    
    # Check for valid selection
    has_valid_selection = (
        st.session_state.form['selected_option'] is not None or
        (st.session_state.form['is_custom_selected'] and 
         st.session_state.form['custom_topic'].strip())
    )
    
    if has_valid_selection:
        if not st.session_state.form['first_name'].strip():
            st.markdown(
                '<div class="error-message">'
                'الرجاء إدخال اسم المخدوم رقم 1'
                '</div>',
                unsafe_allow_html=True
            )
        
        if st.button("✅ إرسال الاختيار",
                    type="primary",
                    key="submit_btn",
                    use_container_width=True,
                    disabled=not st.session_state.form['first_name'].strip()):
            if save_response():
                st.session_state.form['submitted'] = True
                st.rerun()
    else:
        st.markdown(
            '<div class="error-message">'
            'الرجاء اختيار موضوع واحد أو كتابة موضوع مخصص'
            '</div>',
            unsafe_allow_html=True
        )
        st.button("✅ إرسال الاختيار",
                 type="primary",
                 key="submit_btn",
                 use_container_width=True,
                 disabled=True)

if __name__ == "__main__":
    main()
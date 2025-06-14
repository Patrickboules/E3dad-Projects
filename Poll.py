import streamlit as st
from streamlit.components.v1 import html
import json
from github import Github

# Configure page
st.set_page_config(
    layout="wide",
    page_title="مشاريع اعداد 2025",
    page_icon="📊"
)
st.title("📊 مشاريع اعداد 2025")

# Initialize session state
if 'selected' not in st.session_state:
    st.session_state.selected = None
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'first_name' not in st.session_state:
    st.session_state.first_name = ""
if 'last_name' not in st.session_state:
    st.session_state.last_name = ""
if 'temp_counts' not in st.session_state:
    st.session_state.temp_counts = {}

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
@st.cache_data(ttl=300)  # Cache for 5 minutes
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
    for num, count in st.session_state.temp_counts.items():
        combined[num] += count
    return combined

# Save response to GitHub
def save_response():
    response = {
        "First Name": st.session_state.first_name,
        "Last Name": st.session_state.last_name,
        "Topic": options[st.session_state.selected]
    }
    
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(REPO_NAME)
        file = repo.get_contents(FILE_PATH)
        
        # Get existing data
        existing_data = json.loads(file.decoded_content.decode())
        existing_data.append(response)
        
        # Update file on GitHub
        repo.update_file(
            path=FILE_PATH,
            message=f"إضافة اختيار جديد من {st.session_state.first_name}",
            content=json.dumps(existing_data, indent=4, ensure_ascii=False),
            sha=file.sha
        )
        
        st.session_state.temp_counts = {}
        return True
    except Exception as e:
        st.error(f"حدث خطأ في حفظ البيانات على GitHub: {str(e)}")
        return False

# Custom CSS for the options
st.markdown("""
<style>
    :root {
        --primary-color: #4CAF50;
        --hover-color: #f5f5f5;
        --selected-color: #E8F5E9;
        --border-color: #2E7D32;
        --disabled-color: #f9f9f9;
        --text-color: #333;
        --count-color: #666;
    }
    
    body {
        font-family: 'Arial', sans-serif;
    }
    
    .option-container {
        display: flex;
        align-items: center;
        margin: 8px 0;
        padding: 12px 15px;
        border-radius: 10px;
        transition: all 0.3s ease;
        cursor: pointer;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e1e1e1;
    }
    
    .option-container:hover {
        background-color: var(--hover-color);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .option-container.selected {
        background-color: var(--selected-color);
        border-left: 5px solid var(--border-color);
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.2);
    }
    
    .option-container.disabled {
        opacity: 0.7;
        pointer-events: none;
        background-color: var(--disabled-color);
    }
    
    .option-text {
        flex-grow: 1;
        padding: 0 15px;
        text-align: right;
        font-size: 16px;
        color: var(--text-color);
    }
    
    .progress-container {
        width: 120px;
        height: 20px;
        background-color: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        margin-right: 15px;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, var(--primary-color), #81C784);
        width: 0%;
        transition: width 0.5s ease;
    }
    
    .complete {
        background: linear-gradient(90deg, var(--border-color), #4CAF50);
    }
    
    .option-number {
        font-weight: bold;
        min-width: 30px;
        font-size: 16px;
        color: var(--text-color);
    }
    
    .count-display {
        font-size: 13px;
        color: var(--count-color);
        margin-left: 10px;
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
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
    }
    
    .header {
        color: #2E7D32;
        margin-bottom: 20px;
    }
    
    .success-message {
        font-size: 18px;
        padding: 15px;
        border-radius: 8px;
    }
    
    .error-message {
        font-size: 16px;
        padding: 10px;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

def create_option(num, text):
    combined_counts = get_combined_counts()
    count = combined_counts.get(num, 0)
    max_limit = 3
    progress = (count / max_limit) * 100
    disabled = count >= max_limit
    selected = st.session_state.selected == num
    
    container = st.container()
    container.markdown(
        f"""
        <div class="option-container {'selected' if selected else ''} {'disabled' if disabled and not selected else ''}" 
             id="option_{num}"
             onclick="handleClick({num})">
            <div class="option-number">{num}.</div>
            <div class="progress-container">
                <div class="progress-bar {'complete' if count >= max_limit else ''}" style="width:{progress}%"></div>
            </div>
            <div class="option-text">{text}</div>
            <div class="count-display">({count}/{max_limit})</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if not disabled and container.button("اختر", key=f"select_{num}"):
        if st.session_state.selected is not None:
            st.session_state.temp_counts[st.session_state.selected] = st.session_state.temp_counts.get(st.session_state.selected, 0) - 1
        st.session_state.selected = num
        st.session_state.temp_counts[num] = st.session_state.temp_counts.get(num, 0) + 1
        st.rerun()

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
    </script>
    """

def main():
    if not st.session_state.submitted:
        # Name input section
        with st.container():
            st.subheader("المجموعة")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<span class="required-field">اسم المخدوم رقم 1</span>', unsafe_allow_html=True)
                st.session_state.first_name = st.text_input(
                    "اسم المخدوم رقم 1", 
                    value=st.session_state.first_name,
                    key="first_name_input",
                    label_visibility="collapsed",
                    placeholder="أدخل الاسم الأول"
                )
            with col2:
                st.markdown("اسم المخدوم رقم 2")
                st.session_state.last_name = st.text_input(
                    "اسم المخدوم رقم 2", 
                    value=st.session_state.last_name,
                    key="last_name_input",
                    label_visibility="collapsed",
                    placeholder="أدخل الاسم الثاني"
                )
            st.markdown("---")

    if st.session_state.submitted:
        st.markdown(
            f"""
            <div class="success-message" style="background-color:#E8F5E9;border-left:5px solid #2E7D32">
                <h3>شكرًا لك {st.session_state.first_name}!</h3>
                <p>لقد اخترت: <strong>{options[st.session_state.selected]}</strong></p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return
    
    st.markdown('<h2 class="header">الرجاء اختيار موضوع واحد من المواضيع التالية:</h2>', unsafe_allow_html=True)
    
    # Create 3 columns for responsive layout
    cols = st.columns(3)
    
    for i, (num, text) in enumerate(options.items()):
        with cols[i % 3]:
            create_option(num, text)
    
    html(option_click_js(), height=0)
    
    st.markdown("---")
    if st.session_state.selected:
        if not st.session_state.first_name.strip():
            st.markdown(
                '<div class="error-message" style="background-color:#FFEBEE;border-left:5px solid #F44336">'
                'الرجاء إدخال اسم المخدوم رقم 1'
                '</div>',
                unsafe_allow_html=True
            )
        elif st.button("✅ إرسال الاختيار", type="primary", key="submit_btn", use_container_width=True):
            if save_response():
                st.session_state.submitted = True
                st.rerun()
    else:
        st.markdown(
            '<div class="error-message" style="background-color:#FFEBEE;border-left:5px solid #F44336">'
            'الرجاء اختيار موضوع واحد'
            '</div>',
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()
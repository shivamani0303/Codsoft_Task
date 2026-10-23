import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

from database import initialize_database
from auth import register_user, authenticate_user


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Spam Detection AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# DARK FUTURISTIC THEME
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- MAIN BACKGROUND ---------- */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(75, 45, 160, 0.20),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 20%,
                rgba(0, 130, 255, 0.16),
                transparent 30%
            ),
            radial-gradient(
                circle at 50% 100%,
                rgba(90, 40, 150, 0.15),
                transparent 35%
            ),
            #070914;
        color: #F5F7FF;
    }


    /* ---------- GENERAL TEXT ---------- */

    h1, h2, h3, h4 {
        color: #F5F7FF !important;
    }

    p, label, span {
        color: #C8CEE0;
    }


    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #090C19 0%,
                #0D1020 100%
            );
        border-right: 1px solid rgba(130, 140, 255, 0.15);
    }

    section[data-testid="stSidebar"] * {
        color: #DDE2F2 !important;
    }


    /* ---------- INPUTS ---------- */

    div[data-baseweb="input"],
    div[data-baseweb="textarea"] {
        background-color: rgba(15, 19, 38, 0.9) !important;
        border: 1px solid rgba(130, 140, 255, 0.22) !important;
        border-radius: 12px !important;
    }

    input,
    textarea {
        color: #F5F7FF !important;
        background-color: transparent !important;
    }

    textarea {
        min-height: 160px !important;
    }

    input::placeholder,
    textarea::placeholder {
        color: #737B96 !important;
    }


    /* ---------- BUTTONS ---------- */

    .stButton > button {
        width: 100%;
        border-radius: 12px;
        border: 1px solid rgba(125, 110, 255, 0.40);
        background:
            linear-gradient(
                135deg,
                rgba(88, 67, 190, 0.95),
                rgba(40, 95, 190, 0.95)
            );
        color: white;
        font-weight: 600;
        min-height: 44px;
        transition: 0.2s ease;
    }

    .stButton > button:hover {
        border-color: rgba(150, 140, 255, 0.8);
        transform: translateY(-1px);
        box-shadow: 0 8px 25px rgba(75, 65, 190, 0.25);
    }


    /* ---------- FORM SUBMIT BUTTON ---------- */

    .stFormSubmitButton > button {
        width: 100%;
        border-radius: 12px;
        border: 1px solid rgba(125, 110, 255, 0.40);
        background:
            linear-gradient(
                135deg,
                rgba(88, 67, 190, 0.95),
                rgba(40, 95, 190, 0.95)
            );
        color: white;
        font-weight: 600;
        min-height: 44px;
    }

    .stFormSubmitButton > button:hover {
        border-color: rgba(150, 140, 255, 0.8);
        box-shadow: 0 8px 25px rgba(75, 65, 190, 0.25);
    }


    /* ---------- BORDERED CONTAINERS ---------- */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(13, 17, 35, 0.72);
        border: 1px solid rgba(130, 140, 255, 0.18);
        border-radius: 20px;
        backdrop-filter: blur(18px);
    }


    /* ---------- METRICS ---------- */

    div[data-testid="stMetric"] {
        background: rgba(15, 19, 40, 0.78);
        border: 1px solid rgba(120, 130, 255, 0.18);
        border-radius: 16px;
        padding: 18px;
    }

    div[data-testid="stMetricLabel"] {
        color: #858DA8 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #F5F7FF !important;
    }


    /* ---------- TABS ---------- */

    button[data-baseweb="tab"] {
        color: #929AB5 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FFFFFF !important;
    }


    /* ---------- ALERTS ---------- */

    div[data-testid="stAlert"] {
        border-radius: 14px;
    }


    /* ---------- DIVIDER ---------- */

    hr {
        border-color: rgba(130, 140, 255, 0.12);
    }


    /* ---------- DATAFRAME ---------- */

    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
    }


    /* ---------- CODE ---------- */

    code {
        color: #BFC8FF !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

initialize_database()


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None

if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"

if "message_input" not in st.session_state:
    st.session_state.message_input = ""


# ============================================================
# LOAD MODEL
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "spam_model.pkl"
VECTORIZER_PATH = BASE_DIR / "models" / "tfidf_vectorizer.pkl"


@st.cache_resource
def load_model():

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model file not found:\n{MODEL_PATH}"
        )

    if not VECTORIZER_PATH.exists():
        raise FileNotFoundError(
            f"Vectorizer file not found:\n{VECTORIZER_PATH}"
        )

    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)

    return model, vectorizer


# ============================================================
# AUTHENTICATION - LOGIN PAGE
# ============================================================

def show_login_page():

    st.empty()

    left, right = st.columns(
        [1.15, 0.85],
        gap="large"
    )

    # --------------------------------------------------------
    # LEFT SIDE
    # --------------------------------------------------------

    with left:

        st.write("")
        st.write("")
        st.write("")

        st.title("Spam Detection AI")

        st.caption(
            "Intelligent SMS security and classification"
        )

        st.write("")

        st.header("Intelligent message")
        st.header("protection.")

        st.write(
            "Analyze SMS messages using machine learning "
            "and identify potentially harmful or unwanted "
            "messages."
        )

        st.write("")

        st.markdown("✦ Machine learning powered detection")
        st.markdown("✦ TF-IDF text analysis")
        st.markdown("✦ Secure user authentication")
        st.markdown("✦ Real-time message classification")

    # --------------------------------------------------------
    # RIGHT SIDE
    # --------------------------------------------------------

    with right:

        st.write("")
        st.write("")

        with st.container(border=True):

            st.subheader("Welcome back")

            st.caption(
                "Sign in to continue to your dashboard"
            )

            st.write("")

            with st.form("login_form"):

                username = st.text_input(
                    "Username",
                    placeholder="Enter your username"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password"
                )

                st.write("")

                login_clicked = st.form_submit_button(
                    "Sign in"
                )

            if login_clicked:

                if not username or not password:

                    st.error(
                        "Please enter both username and password."
                    )

                else:

                    success, user = authenticate_user(
                        username,
                        password
                    )

                    if success:

                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.session_state.auth_page = "login"

                        st.success(
                            "Login successful."
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Invalid username or password."
                        )

            st.write("")

            st.caption(
                "Don't have an account?"
            )

            if st.button(
                "Create an account",
                key="go_register"
            ):

                st.session_state.auth_page = "register"
                st.rerun()


# ============================================================
# AUTHENTICATION - REGISTRATION PAGE
# ============================================================

def show_registration_page():

    left, right = st.columns(
        [1.15, 0.85],
        gap="large"
    )

    # --------------------------------------------------------
    # LEFT SIDE
    # --------------------------------------------------------

    with left:

        st.write("")
        st.write("")
        st.write("")

        st.title("Create your account")

        st.caption(
            "Secure access to the SMS classification system"
        )

        st.write("")

        st.header("Start detecting")
        st.header("spam intelligently.")

        st.write(
            "Create an account to access the machine learning "
            "based SMS spam detection dashboard."
        )

        st.write("")

        st.markdown("✦ Secure password hashing")
        st.markdown("✦ Protected user authentication")
        st.markdown("✦ Machine learning classification")
        st.markdown("✦ Simple and fast analysis")

    # --------------------------------------------------------
    # RIGHT SIDE
    # --------------------------------------------------------

    with right:

        st.write("")
        st.write("")

        with st.container(border=True):

            st.subheader("Create account")

            st.caption(
                "Enter your details to get started"
            )

            st.write("")

            with st.form("registration_form"):

                username = st.text_input(
                    "Username",
                    placeholder="Choose a username"
                )

                email = st.text_input(
                    "Email",
                    placeholder="example@email.com"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Create a strong password"
                )

                confirm_password = st.text_input(
                    "Confirm password",
                    type="password",
                    placeholder="Re-enter your password"
                )

                st.caption(
                    "Password must contain at least 8 characters, "
                    "including uppercase, lowercase and a number."
                )

                st.write("")

                register_clicked = st.form_submit_button(
                    "Create account"
                )

            if register_clicked:

                if not username:
                    st.error("Please enter a username.")

                elif not email:
                    st.error("Please enter your email address.")

                elif not password:
                    st.error("Please enter a password.")

                elif not confirm_password:
                    st.error(
                        "Please confirm your password."
                    )

                else:

                    success, message = register_user(
                        username,
                        email,
                        password,
                        confirm_password
                    )

                    if success:

                        st.success(message)

                        st.info(
                            "Your account has been created. "
                            "You can now sign in."
                        )

                        if st.button(
                            "Go to login",
                            key="registration_login"
                        ):

                            st.session_state.auth_page = "login"
                            st.rerun()

                    else:

                        st.error(message)

            st.write("")

            if st.button(
                "Already have an account? Sign in",
                key="go_login"
            ):

                st.session_state.auth_page = "login"
                st.rerun()


# ============================================================
# AUTHENTICATION ROUTER
# ============================================================

if not st.session_state.authenticated:

    if st.session_state.auth_page == "register":

        show_registration_page()

    else:

        show_login_page()

    st.stop()


# ============================================================
# LOAD MODEL AFTER LOGIN
# ============================================================

try:

    model, vectorizer = load_model()

except Exception as error:

    st.error("Unable to load the spam detection model.")

    st.code(str(error))

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🛡️ Spam Detection AI")

    st.caption("AI-powered SMS classification")

    st.divider()

    user = st.session_state.user

    if user:

        st.write("### Account")

        st.write(
            f"👤 {user['username']}"
        )

        st.write(
            f"📧 {user['email']}"
        )

    st.divider()

    st.write("### Navigation")

    page = st.radio(
        "Choose a section",
        [
            "🔍 Analyzer",
            "📊 Model Performance",
            "🤖 How It Works"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    if st.button(
        "Logout",
        key="logout_button"
    ):

        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.auth_page = "login"
        st.session_state.message_input = ""

        st.rerun()


# ============================================================
# MAIN HEADER
# ============================================================

st.title("Spam Detection AI")

st.caption(
    "Machine learning powered SMS classification system"
)


# ============================================================
# ANALYZER PAGE
# ============================================================

if page == "🔍 Analyzer":

    st.write("")

    # --------------------------------------------------------
    # MESSAGE INPUT
    # --------------------------------------------------------

    st.subheader("Analyze an SMS message")

    message = st.text_area(
        "SMS message",
        key="message_input",
        placeholder="Enter or paste an SMS message here...",
        height=180
    )

    st.write("")

    analyze_clicked = st.button(
        "🔍 Analyze Message",
        key="analyze_button",
        use_container_width=True
    )

    st.write("")

    # ========================================================
    # TRY A SAMPLE - REAL MESSAGES FROM DATASET
    # ========================================================

    @st.cache_data
    def load_sample_messages():

        dataset_path = (
            Path(__file__).resolve().parent
            / "dataset"
            / "spam.csv"
        )

        data = pd.read_csv(
            dataset_path,
            encoding="latin-1"
        )

        data = data[["v1", "v2"]]
        data.columns = ["label", "message"]

        data = data.dropna(
            subset=["label", "message"]
        )

        data = data.drop_duplicates(
            subset=["label", "message"]
        )

        spam_messages = data[
            data["label"] == "spam"
        ]["message"].tolist()

        ham_messages = data[
            data["label"] == "ham"
        ]["message"].tolist()

        return spam_messages, ham_messages


    spam_messages, ham_messages = load_sample_messages()


    def set_spam_sample_1():
        st.session_state.message_input = spam_messages[0]


    def set_spam_sample_2():
        st.session_state.message_input = spam_messages[1]


    def set_spam_sample_3():
        st.session_state.message_input = spam_messages[2]


    def set_ham_sample_1():
        st.session_state.message_input = ham_messages[0]


    def set_ham_sample_2():
        st.session_state.message_input = ham_messages[1]


    def set_ham_sample_3():
        st.session_state.message_input = ham_messages[2]


    st.subheader("Try a sample")
    st.caption("Choose a real SMS message from the dataset")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### 🚨 Spam messages")

        st.button(
            "Spam message 1",
            key="spam_sample_1",
            on_click=set_spam_sample_1,
            use_container_width=True
        )

        st.button(
            "Spam message 2",
            key="spam_sample_2",
            on_click=set_spam_sample_2,
            use_container_width=True
        )

        st.button(
            "Spam message 3",
            key="spam_sample_3",
            on_click=set_spam_sample_3,
            use_container_width=True
        )


    with col2:

        st.markdown("### 💬 Normal messages")

        st.button(
            "Normal message 1",
            key="ham_sample_1",
            on_click=set_ham_sample_1,
            use_container_width=True
        )

        st.button(
            "Normal message 2",
            key="ham_sample_2",
            on_click=set_ham_sample_2,
            use_container_width=True
        )

        st.button(
            "Normal message 3",
            key="ham_sample_3",
            on_click=set_ham_sample_3,
            use_container_width=True
        )


    # --------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------

    if analyze_clicked:

        if not message.strip():

            st.warning(
                "Please enter a message before analyzing."
            )

        else:

            try:

                transformed_message = vectorizer.transform(
                    [message]
                )

                prediction = model.predict(
                    transformed_message
                )[0]

                # Confidence
                confidence = None

                if hasattr(model, "predict_proba"):

                    probabilities = model.predict_proba(
                        transformed_message
                    )[0]

                    confidence = max(probabilities) * 100

                # Result
                if prediction == 1:

                    st.error(
                        "🚨 SPAM MESSAGE DETECTED"
                    )

                    st.write(
                        "This message has characteristics "
                        "associated with spam."
                    )

                else:

                    st.success(
                        "✅ NORMAL MESSAGE"
                    )

                    st.write(
                        "This message appears to be a normal "
                        "or legitimate SMS."
                    )

                # Confidence
                if confidence is not None:

                    st.metric(
                        "Prediction Confidence",
                        f"{confidence:.2f}%"
                    )

            except Exception as error:

                st.error(
                    "An error occurred while analyzing "
                    "the message."
                )

                st.code(str(error))

# ============================================================
# MODEL PERFORMANCE PAGE
# ============================================================

elif page == "📊 Model Performance":

    st.header("Model Performance")

    st.write(
        "Performance of the trained spam detection model "
        "on the test dataset."
    )

    st.write("")

    # --------------------------------------------------------
    # NAIVE BAYES METRICS
    # --------------------------------------------------------

    st.subheader("Multinomial Naive Bayes")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Accuracy",
            "96.61%"
        )

    with col2:

        st.metric(
            "Precision",
            "99.00%"
        )

    with col3:

        st.metric(
            "Recall",
            "74.05%"
        )

    with col4:

        st.metric(
            "F1 Score",
            "84.50%"
        )

    st.write("")

    # --------------------------------------------------------
    # MODEL COMPARISON
    # --------------------------------------------------------

    st.subheader("Model Comparison")

    comparison_data = pd.DataFrame(
        {
            "Model": [
                "Multinomial Naive Bayes",
                "Logistic Regression"
            ],
            "Accuracy": [
                96.61,
                95.84
            ],
            "Precision": [
                99.00,
                98.89
            ],
            "Recall": [
                74.05,
                67.94
            ],
            "F1 Score": [
                84.50,
                80.54
            ]
        }
    )

    st.dataframe(
        comparison_data,
        use_container_width=True,
        hide_index=True
    )

    st.write("")

    st.subheader("Metric Visualization")

    chart_data = comparison_data.set_index(
        "Model"
    )

    st.bar_chart(
        chart_data
    )


# ============================================================
# HOW IT WORKS PAGE
# ============================================================

elif page == "🤖 How It Works":

    st.header("How the system works")

    st.write(
        "The system uses natural language processing and "
        "machine learning to classify SMS messages."
    )

    st.write("")

    # --------------------------------------------------------
    # STEP 1
    # --------------------------------------------------------

    with st.container(border=True):

        st.subheader("1️⃣ Message Input")

        st.write(
            "The user enters an SMS message that needs to "
            "be classified."
        )

    st.write("")

    # --------------------------------------------------------
    # STEP 2
    # --------------------------------------------------------

    with st.container(border=True):

        st.subheader("2️⃣ TF-IDF Transformation")

        st.write(
            "The text is converted into numerical features "
            "using TF-IDF vectorization."
        )

    st.write("")

    # --------------------------------------------------------
    # STEP 3
    # --------------------------------------------------------

    with st.container(border=True):

        st.subheader("3️⃣ Machine Learning Model")

        st.write(
            "The TF-IDF features are passed to the trained "
            "Multinomial Naive Bayes classifier."
        )

    st.write("")

    # --------------------------------------------------------
    # STEP 4
    # --------------------------------------------------------

    with st.container(border=True):

        st.subheader("4️⃣ Classification")

        st.write(
            "The model predicts whether the message is "
            "Spam or Ham."
        )

    st.write("")

    # --------------------------------------------------------
    # STEP 5
    # --------------------------------------------------------

    with st.container(border=True):

        st.subheader("5️⃣ Result")

        st.write(
            "The prediction and confidence score are "
            "displayed to the user."
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Spam Detection AI • Machine Learning SMS Classification"
)
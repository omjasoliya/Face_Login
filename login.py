import os
import time
import pickle

import psutil
import cv2
import numpy as np
import streamlit as st
from insightface.app import FaceAnalysis
from numpy.linalg import norm
from pymongo import MongoClient
from bson.binary import Binary

# 🔥 MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="FaceAuth App",
    page_icon="🔐",
    layout="wide",
)

# ─── SESSION STATE DEFAULTS ───────────────────────────────────────────────────
for key, default in {
    "signup_started": False,
    "signup_username": "",
    "signup_image": None,
    "auth_started": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .card { background: #fff; border-radius:12px; padding:24px; box-shadow:0 4px 12px rgba(0,0,0,0.05); margin-bottom:24px; }
  .card-header { font-size:22px; font-weight:600; color:#FFFFFF; margin-bottom:16px; }
  .stButton > button { background:#4CAF50; color:#fff; width:100%; padding:12px 0; font-size:16px; border-radius:6px; }
  .stButton > button:hover { background:#45a049; }
</style>
""", unsafe_allow_html=True)

# ─── MONGO SETUP ───────────────────────────────────────────────────────────────
MONGO_URI = "mongodb+srv://<your-credentials>@cluster0.hhcuv7x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client    = MongoClient(MONGO_URI)
db        = client["faceauth_db"]
col       = db["embeddings"]

# ─── FACE MODEL SETUP ─────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    app = FaceAnalysis(providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=0, det_size=(640, 640))
    return app

app = load_model()

# ─── UTILS ────────────────────────────────────────────────────────────────────
def compute_similarity(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

def save_embedding(username: str, emb: np.ndarray):
    pickled = pickle.dumps(emb, protocol=pickle.HIGHEST_PROTOCOL)
    col.replace_one(
        {"username": username},
        {"username": username, "emb": Binary(pickled)},
        upsert=True
    )

def load_embeddings() -> dict[str, np.ndarray]:
    embs: dict[str, np.ndarray] = {}
    for doc in col.find({}):
        embs[doc["username"]] = pickle.loads(doc["emb"])
    return embs

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔐 FaceAuth App")
    with st.expander("💻 System Resource Usage", expanded=True):
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        st.metric("CPU Usage", f"{cpu}%")
        st.metric("Memory Used", f"{mem.percent}% of {mem.total//(1024**3)} GB")
    st.markdown("---")
    st.markdown("""
    **How it works**  
    1. **Signup**: click ▶️, enter username & capture face  
    2. **Login**: click ▶️, live face matching  
    3. Password-less, secure auth  
    """)

# ─── MAIN LAYOUT ──────────────────────────────────────────────────────────────
st.markdown("<h1 style='text-align:center;color:#2E3A59;'>🔐 FaceAuth Login & Signup</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#6c757d;'>Fast, secure, and seamless face authentication.</p>", unsafe_allow_html=True)

tabs = st.tabs(["🆕 Signup", "🔓 Login"])

# ─── SIGNUP TAB ────────────────────────────────────────────────────────────────
with tabs[0]:
    st.markdown('<div class="card-header">👤 New User Registration</div>', unsafe_allow_html=True)

    col1, _ = st.columns([3, 1])
    with col1:
        if not st.session_state.signup_started:
            if st.button("▶️ Start Registration"):
                st.session_state.signup_started = True
        else:
            if st.button("🔒 Stop Registration"):
                # reset signup state
                st.session_state.signup_started = False
                st.session_state.signup_username = ""
                st.session_state.signup_image = None
                st.rerun()
    if st.session_state.signup_started:
        st.session_state.signup_username = st.text_input(
            "Username",
            value=st.session_state.signup_username,
            placeholder="Enter a unique username"
        )
        img_file = st.camera_input("Capture your face", key="signup_cam")
        if img_file:
            arr = np.frombuffer(img_file.getvalue(), np.uint8)
            st.session_state.signup_image = cv2.imdecode(arr, cv2.IMREAD_COLOR)

        if st.session_state.signup_username and st.session_state.signup_image is not None:
            if st.button("Register"):
                faces = app.get(st.session_state.signup_image)
                if not faces:
                    st.error("⚠️ No face detected. Adjust camera or lighting.")
                else:
                    emb = faces[0].embedding
                    embs = load_embeddings()
                    # check duplicate face
                    for name, known in embs.items():
                        if compute_similarity(emb, known) > 0.6:
                            st.warning(f"⚠️ Face already registered as **{name}**.")
                            break
                    else:
                        if st.session_state.signup_username in embs:
                            st.warning(f"⚠️ Username **{st.session_state.signup_username}** taken.")
                        else:
                            save_embedding(st.session_state.signup_username, emb)
                            st.success(f"✅ **{st.session_state.signup_username}** registered!")
                            st.balloons()
                            # reset
                            st.session_state.signup_started = False
                            st.session_state.signup_username = ""
                            st.session_state.signup_image = None
    else:
        st.info("Click ▶️ Start Registration to begin.")

    st.markdown('</div>', unsafe_allow_html=True)

# ─── LOGIN TAB ─────────────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown('<div class="card-header">🔍 Face Authentication (Live)</div>', unsafe_allow_html=True)

    embeddings = load_embeddings()
    if not embeddings:
        st.warning("⚠️ No users found. Please sign up first.")
    else:
        col1, _ = st.columns([3, 1])
        with col1:
            if not st.session_state.auth_started:
                if st.button("▶️ Start Authentication"):
                    st.session_state.auth_started = True
            else:
                if st.button("🔒 Stop Authentication"):
                    st.session_state.auth_started = False

        if st.session_state.auth_started:
            placeholder = st.empty()
            status = st.empty()
            cap = cv2.VideoCapture(0)
            start = time.time()
            TIMEOUT = 20

            while cap.isOpened() and st.session_state.auth_started:
                ret, frame = cap.read()
                if not ret:
                    status.error("❌ Cannot access camera.")
                    break

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                placeholder.image(rgb, channels="RGB", caption="Scanning...")

                faces = app.get(frame)
                if faces:
                    emb = faces[0].embedding
                    best_name, best_sim = max(
                        ((n, compute_similarity(emb, k)) for n, k in embeddings.items()),
                        key=lambda x: x[1]
                    )
                    if best_sim > 0.6:
                        status.success(f"✅ Welcome **{best_name}** (score {best_sim:.2f})")
                        st.balloons()
                        break

                if time.time() - start > TIMEOUT:
                    status.warning("⌛ Timeout. No match found.")
                    break

            cap.release()
            st.session_state.auth_started = False  # auto-stop
        else:
            st.info("Click ▶️ Start Authentication to begin face scan.")

    st.markdown('</div>', unsafe_allow_html=True)


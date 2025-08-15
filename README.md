# 🔐 FaceAuth App (Streamlit + InsightFace + MongoDB)

Password-less face authentication with a clean Streamlit UI.  
Users **sign up** by capturing a face image; **log in** via live webcam matching against stored face embeddings in MongoDB.

---

## ✨ Features

- **Signup**: capture a face + username, store embedding in MongoDB.
- **Login**: live webcam scan, cosine similarity match with threshold.
- **Streamlit UI** with simple start/stop controls and resource stats.
- **CPU-only** by default (InsightFace with `CPUExecutionProvider`).
- **Idempotent storage**: upsert by username; duplicate-face check.

---

## 🧱 Tech Stack

- **Frontend/App**: [Streamlit](https://streamlit.io/)
- **Face recognition**: [InsightFace](https://github.com/deepinsight/insightface) (`FaceAnalysis`)
- **Data**: MongoDB (Atlas or local)
- **Python libs**: `opencv-python`, `numpy`, `psutil`, `pymongo`

---

## 📦 Requirements

- Python 3.9–3.11
- A webcam
- MongoDB (Atlas **or** local `mongod`)
- OS: Windows, macOS, Linux

---

## 🚀 Quickstart

### 1️⃣ Clone & create a virtual environment


git clone https://github.com/<your-username>/faceauth-app.git
cd faceauth-app

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
2️⃣ Install dependencies
bash
Copy
Edit
pip install -U pip
pip install streamlit insightface opencv-python numpy psutil pymongo "pymongo[srv]" dnspython
pymongo[srv] + dnspython are required if you use an Atlas SRV URI (mongodb+srv://).

3️⃣ Configure MongoDB
Create a .env file (or set environment variables in your shell). You can choose Atlas or Local.

Option A — MongoDB Atlas (recommended)
In Atlas: Build a Database (M0 Free is fine), create a DB user, and add your IP to Network Access.

From Connect → Drivers, copy the SRV URI. It looks like:

ruby
Copy
Edit
mongodb+srv://app_user:<PASSWORD>@cluster0.ab12cde.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
URL-encode special characters in <PASSWORD> (e.g., @ → %40).

Example .env:

bash
Copy
Edit
MONGO_URI="mongodb+srv://app_user:ENCODED_PASSWORD@cluster0.ab12cde.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
Option B — Local MongoDB
Ensure mongod is running, then:

Example .env:

bash
Copy
Edit
MONGO_URI="mongodb://127.0.0.1:27017/?directConnection=true"
4️⃣ Run the app
bash
Copy
Edit
# If you created .env, load it first or set MONGO_URI in your shell
streamlit run login.py
Open the URL Streamlit prints (usually http://localhost:8501).

🧩 How it works
Model: FaceAnalysis detects faces and outputs a 512-d embedding.

Storage: Embeddings are serialized with pickle and stored in faceauth_db.embeddings.

Match: Cosine similarity between live embedding and stored ones.

Threshold: 0.60 by default (adjust to your needs).

⚙️ Configuration
Setting	Where	Default
Mongo URI	.env → MONGO_URI	(required)
DB name / collection	in code	faceauth_db, embeddings
Similarity threshold	in code	0.60
Capture timeout (login)	in code	20s
Device	CPUExecutionProvider	CPU
Detector input size	det_size=(640, 640)	640×640

🗂️ Project structure
bash
Copy
Edit
.
├─ login.py            # main Streamlit app
├─ README.md           # this file
└─ .env                # contains MONGO_URI (not committed)
🧪 Usage
Signup
Go to 🆕 Signup tab.

Click Start Registration → enter username → capture face.

Click Register.

Blocks duplicate faces and usernames.

Login
Go to 🔓 Login tab.

Click Start Authentication.

Look at the camera — if match > threshold, you’re in.

🛠️ Troubleshooting
MongoDB SRV / DNS errors (Atlas)
bash
Copy
Edit
pymongo.errors.ConfigurationError: The DNS query name does not exist: _mongodb._tcp.cluster0.<id>.mongodb.net.
Use the exact URI from Atlas → Connect → Drivers.

Install SRV support: pip install "pymongo[srv]" dnspython

Whitelist your IP in Atlas.

Connection timeout / auth failure
Verify username & password (URL-encode password).

For local Mongo: use mongodb://127.0.0.1:27017/?directConnection=true

Streamlit file-watcher + PyTorch errors (Windows)
Disable watcher:

bash
Copy
Edit
setx STREAMLIT_SERVER_FILE_WATCHER_TYPE none
Or run:

streamlit run login.py --server.fileWatcherType=none
🔒 Security notes
Never commit .env with credentials.

Use per-app DB users (avoid root).

Consider encryption for embeddings in production.

📜 License
MIT — feel free to use and adapt.
If you build something cool, a ⭐️ would be appreciated!

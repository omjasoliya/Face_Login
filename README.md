🔐 FaceAuth App (Streamlit + InsightFace + MongoDB)

Password-less face authentication with a clean Streamlit UI.
Users sign up by capturing a face image; log in via live webcam matching against stored face embeddings in MongoDB.

✨ Features

Signup: capture a face + username, store embedding in MongoDB.

Login: live webcam scan, cosine similarity match with threshold.

Streamlit UI with simple start/stop controls and resource stats.

CPU-only by default (InsightFace with CPUExecutionProvider).

Idempotent storage: upsert by username; duplicate-face check.

🧱 Tech Stack

Frontend/App: Streamlit

Face recognition: InsightFace (FaceAnalysis)

Data: MongoDB (Atlas or local)

Python libs: opencv-python, numpy, psutil, pymongo

📦 Requirements

Python 3.9–3.11

A webcam

MongoDB (Atlas or local mongod)

OS: Windows, macOS, Linux

🚀 Quickstart
1) Clone & create a virtual environment
git clone https://github.com/<your-username>/faceauth-app.git
cd faceauth-app

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

2) Install dependencies
pip install -U pip
pip install streamlit insightface opencv-python numpy psutil pymongo "pymongo[srv]" dnspython


pymongo[srv] + dnspython are required if you use an Atlas SRV URI (mongodb+srv://).

3) Configure MongoDB

Create a .env (or set environment variables in your shell). You can choose Atlas or Local.

Option A — MongoDB Atlas (recommended for quick start)

In Atlas: Build a Database (M0 Free is fine), create a DB user, and add your IP to Network Access.

From Connect → Drivers, copy the SRV URI. It looks like:

mongodb+srv://app_user:<PASSWORD>@cluster0.ab12cde.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0


URL-encode special characters in <PASSWORD> (e.g., @ → %40).

.env:

MONGO_URI="mongodb+srv://app_user:ENCODED_PASSWORD@cluster0.ab12cde.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

Option B — Local MongoDB

Make sure mongod is running, then:

.env:

MONGO_URI="mongodb://127.0.0.1:27017/?directConnection=true"

4) Run the app
# If you created .env, load it (optional helper)
# Windows PowerShell:  $env:MONGO_URI = "your-uri"
# macOS/Linux:         export MONGO_URI="your-uri"

streamlit run login.py


Open the URL Streamlit prints (usually http://localhost:8501).

🧩 How it works

Model: FaceAnalysis detects faces and outputs a 512-d embedding.

Storage: Embeddings are serialized with pickle and stored in faceauth_db.embeddings as { username, emb }.

Match: Cosine similarity between live embedding and stored ones.

Threshold: 0.60 by default (adjust to your data/lighting).

MongoDB collections are created automatically on first insert—no manual schema is required.

⚙️ Configuration
Setting	Where	Default
Mongo URI	.env → MONGO_URI	(required)
DB name / collection	in code (faceauth_db.embeddings)	faceauth_db, embeddings
Similarity threshold	in code (> 0.6)	0.60
Capture timeout (login)	in code (TIMEOUT = 20)	20s
Device	CPUExecutionProvider	CPU
Detector input size	det_size=(640, 640)	640×640
🗂️ Project structure (minimal)
.
├─ login.py            # main Streamlit app
├─ README.md           # this file
└─ .env                # contains MONGO_URI (not committed)

🧪 Usage
Signup

Go to 🆕 Signup tab.

Start Registration → enter username → Capture your face.

Click Register.

App blocks duplicates (same face) and duplicate usernames.

Login

Go to 🔓 Login tab.

Start Authentication.

Look at the camera. If the top match exceeds the threshold, you’re in.

🛠️ Troubleshooting
MongoDB SRV / DNS errors (Atlas)
pymongo.errors.ConfigurationError: The DNS query name does not exist: _mongodb._tcp.cluster0.<id>.mongodb.net.


You used a placeholder hostname. Copy the exact URI from Atlas → Connect → Drivers.

Ensure SRV support: pip install "pymongo[srv]" dnspython

Whitelist your IP in Atlas.

Check DNS:

nslookup -type=SRV _mongodb._tcp.cluster0.<your-id>.mongodb.net

Connection timeout / authentication

Verify user & password (URL-encode password).

For local Mongo: use mongodb://127.0.0.1:27017/?directConnection=true

Add serverSelectionTimeoutMS=5000 to MongoClient if needed.

Streamlit file-watcher + PyTorch noise on Windows

If you see errors about torch.classes during hot-reload, disable the watcher:

# One time:
# Windows PowerShell
setx STREAMLIT_SERVER_FILE_WATCHER_TYPE none

# Or at runtime:
streamlit run login.py --server.fileWatcherType=none


Or upgrade:

pip install -U streamlit torch

Webcam issues

Ensure only one app is using the camera.

On macOS, grant Terminal/IDE camera permissions.

Try cv2.VideoCapture(0) → check if ret is True.

Model download / performance

InsightFace will download model weights on first run (cache under ~/.insightface).

For faster detection on CPU, reduce det_size or run on a GPU (requires proper CUDA setup and changing providers).

🔒 Security notes

Don’t commit .env with credentials.

Use per-app DB users; avoid root.

Consider encryption at rest for stored embeddings (they’re pickled).

For multi-user/public deployment, add authentication/authorization to the app itself.

🧰 Helpful code snippets

Safer Mongo client with early ping:

from pymongo import MongoClient
from pymongo.errors import ConfigurationError, ServerSelectionTimeoutError
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/?directConnection=true")
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, tls=MONGO_URI.startswith("mongodb+srv://"))
client.admin.command("ping")
db = client["faceauth_db"]
col = db["embeddings"]


Adjust similarity threshold:

THRESHOLD = 0.60
if best_sim > THRESHOLD:
    # success

📜 License

MIT — feel free to use and adapt.
If you build something cool with this, a star ⭐️ on the repo would be awesome!

🙋 FAQ

Q: Do I need to create the MongoDB collection manually?
A: No. MongoDB creates DB/collection on first insert.

Q: Can I run on GPU?
A: Yes, if your environment has CUDA/cuDNN and you install the GPU-enabled dependencies, then initialize InsightFace with the appropriate provider.

Q: Can I use a different DB (e.g., Postgres)?
A: This sample uses MongoDB for simplicity. You can swap out the persistence layer—just store/retrieve embeddings the same way.

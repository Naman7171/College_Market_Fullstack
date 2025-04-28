
# UniSphere 🎓 — College Marketplace & Community Platform

UniSphere is a **full-stack platform** designed exclusively for college students to **buy/sell items**, **post lost and found notices**, **join community discussions**, and **manage events** — fostering trust within the campus network.

---

## 📂 Project Structure

```
College_Market_Fullstack/
│
├── frontend/    # React (Vite + TypeScript + Zustand + TailwindCSS)
│
├── backend/     # Flask (Python REST API)
│
└── README.md
```

---

## 🌟 Key Features

- **Marketplace**:  
  Students can list and purchase items securely (e.g., a 4th-year selling a laptop to a 1st-year with trust inside campus).
  
- **Lost and Found**:  
  Report and recover lost items easily through community help.

- **Community Forum**:  
  Students can post discussions, ask questions, and build connections.

- **Event Management**:  
  Host and manage college events and activities on one platform.

- **Authentication**:  
  Secure login, registration, JWT token-based authentication.

- **Role Management**:  
  User roles like Student, Faculty, and Admin.

- **Real-Time Messaging** *(Planned)*:  
  Chat functionality between users.

---

## 🛠 Tech Stack

**Frontend (React)**
- React 18
- Vite
- TypeScript
- TailwindCSS
- Zustand (for global state management)
- Axios (for API calls)
- React Router

**Backend (Flask)**
- Flask + Flask-RESTful
- JWT Authentication
- SQLAlchemy (ORM)
- CORS (Cross-Origin Resource Sharing)
- Flask-Migrate (for database migrations)

**Database**
- SQLite (for development)

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Naman7171/College_Market_Fullstack.git
cd College_Market_Fullstack
```

---

### 2. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

**Start the backend server:**
```bash
python app.py
```
(Backend will run at `http://localhost:5000`)

---

### 3. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```
(Frontend will run at `http://localhost:5173`)

---

## 🧠 Project Motivation

- Students often hesitate to trust strangers on platforms like OLX.
- UniSphere solves this by enabling **peer-to-peer trust** based on **college identity** (knowing batch, branch, etc.).
- Also provides **community bonding** through forums and event participation.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you would like to change.

---

## 📄 License

This project is licensed under the MIT License.

---

## 📬 Contact

- **Developer**: Naman joshi
---

# 🚀 Let's build a trusted student community together!

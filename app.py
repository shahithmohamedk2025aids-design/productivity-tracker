import streamlit as st
import json
import os
import hashlib
import pandas as pd
from datetime import date

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Productivity Pro", layout="wide")

# ---------------- BACKGROUND STYLE (OPTION 2) ----------------
st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1492724441997-5dc865305da7");
    background-size: cover;
    background-position: center;
}

/* Dark overlay */
.stApp::before {
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0,0,0,0.7);
    z-index: -1;
}

/* Glass UI */
.card {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    color: white;
}

/* Buttons */
.stButton>button {
    border-radius: 10px;
    background: linear-gradient(45deg, #00c6ff, #0072ff);
    color: white;
    font-weight: bold;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(0,0,0,0.6);
}
</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------
DATA_FILE = "data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# ---------------- HASH ----------------
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN ----------------
def login():
    st.markdown("<h1 style='text-align:center;color:white;'>🚀 Productivity Pro</h1>", unsafe_allow_html=True)

    data = load_data()

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if u in data and data[u]["password"] == hash_password(p):
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        u = st.text_input("New Username")
        p = st.text_input("New Password", type="password")

        if st.button("Create Account"):
            if u in data:
                st.warning("User already exists")
            else:
                data[u] = {
                    "password": hash_password(p),
                    "tasks": [],
                    "streak": 0,
                    "last_date": str(date.today())
                }
                save_data(data)
                st.success("Account created")

# ---------------- MAIN ----------------
def app():
    data = load_data()
    user = st.session_state.user

    st.sidebar.title("⚡ Menu")
    menu = st.sidebar.radio("Navigate", ["Dashboard", "Tasks", "Stats", "Logout"])

    st.markdown(f"<h2 style='color:white;'>Welcome, {user} 👋</h2>", unsafe_allow_html=True)

    # -------- DASHBOARD --------
    if menu == "Dashboard":
        today = str(date.today())

        if data[user]["last_date"] != today:
            data[user]["streak"] += 1
            data[user]["last_date"] = today
            save_data(data)

        total = len(data[user]["tasks"])
        done = sum(1 for t in data[user]["tasks"] if t["done"])
        progress = int((done / total) * 100) if total > 0 else 0

        col1, col2, col3 = st.columns(3)

        col1.metric("Tasks", total)
        col2.metric("Completed", done)
        col3.metric("🔥 Streak", data[user]["streak"])

        st.progress(progress)

    # -------- TASKS --------
    elif menu == "Tasks":
        st.subheader("Your Tasks")

        new_task = st.text_input("Add Task")

        if st.button("Add Task"):
            if new_task:
                data[user]["tasks"].append({"task": new_task, "done": False})
                save_data(data)
                st.rerun()

        st.markdown("### Task List")

        for i, t in enumerate(data[user]["tasks"]):
            col1, col2 = st.columns([8,1])

            checked = col1.checkbox(t["task"], value=t["done"], key=f"chk_{i}")
            data[user]["tasks"][i]["done"] = checked

            if col2.button("Delete", key=f"del_{i}"):
                data[user]["tasks"].pop(i)
                save_data(data)
                st.rerun()

        save_data(data)

    # -------- STATS --------
    elif menu == "Stats":
        st.subheader("Your Stats")

        total = len(data[user]["tasks"])
        done = sum(1 for t in data[user]["tasks"] if t["done"])

        df = pd.DataFrame({
            "Type": ["Total", "Completed"],
            "Count": [total, done]
        })

        st.bar_chart(df.set_index("Type"))

    # -------- LOGOUT --------
    elif menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

# ---------------- RUN ----------------
if st.session_state.logged_in:
    app()
else:
    login()

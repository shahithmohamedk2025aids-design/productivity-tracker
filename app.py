import streamlit as st
import json
import os
import hashlib
import pandas as pd
from datetime import date

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Productivity Ultra", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #1f1c2c, #928dab);
    color: white;
}
.card {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
}
</style>
""", unsafe_allow_html=True)

# ---------------- FILE ----------------
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
    st.title("🚀 Productivity Ultra")

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
                st.error("Wrong credentials")

    with tab2:
        u = st.text_input("New Username")
        p = st.text_input("New Password", type="password")

        if st.button("Create"):
            if u in data:
                st.warning("User exists")
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
    menu = st.sidebar.radio("Go", ["Dashboard", "Tasks", "Stats", "Logout"])

    st.title(f"Welcome {user}")

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
        st.subheader("Tasks")

        new_task = st.text_input("Add Task")

        if st.button("Add"):
            if new_task:
                data[user]["tasks"].append({"task": new_task, "done": False})
                save_data(data)
                st.rerun()

        for i, t in enumerate(data[user]["tasks"]):
            col1, col2 = st.columns([8,1])

            checked = col1.checkbox(t["task"], value=t["done"], key=f"chk{i}")
            data[user]["tasks"][i]["done"] = checked

            if col2.button("X", key=f"del{i}"):
                data[user]["tasks"].pop(i)
                save_data(data)
                st.rerun()

        save_data(data)

    # -------- STATS --------
    elif menu == "Stats":
        st.subheader("Stats")

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

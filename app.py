import streamlit as st
import json
import os
import hashlib
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Productivity Tracker", page_icon="🚀", layout="wide")

# ---------------- BACKGROUND STYLE ----------------
st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1519389950473-47ba0277781c");
    background-size: cover;
}
.glass {
    background: rgba(0,0,0,0.65);
    padding: 25px;
    border-radius: 15px;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE FILE ----------------
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

# ---------------- PASSWORD HASH ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN PAGE ----------------
def login_page():
    st.markdown("<h1 style='text-align:center;color:white;'>🚀 Productivity Tracker</h1>", unsafe_allow_html=True)
    st.markdown('<div class="glass">', unsafe_allow_html=True)

    data = load_data()

    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Signup"])

    # LOGIN
    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in data and data[username]["password"] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.user = username
                st.success("Login successful 🎉")
                st.rerun()
            else:
                st.error("Invalid credentials ❌")

    # SIGNUP
    with tab2:
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Create Account"):
            if new_user in data:
                st.warning("User already exists ⚠️")
            else:
                data[new_user] = {
                    "password": hash_password(new_pass),
                    "tasks": []
                }
                save_data(data)
                st.success("Account created ✅")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- MAIN APP ----------------
def main_app():
    data = load_data()
    user = st.session_state.user

    st.sidebar.title("🚀 Menu")
    menu = st.sidebar.radio("Navigate", ["🏠 Dashboard", "📝 Tasks", "📊 Stats", "🚪 Logout"])

    st.title(f"Welcome, {user} 👋")

    # DASHBOARD
    if menu == "🏠 Dashboard":
        st.subheader("📊 Daily Productivity")
        progress = st.slider("Your productivity", 0, 100, 50)
        st.progress(progress)

    # TASKS
    elif menu == "📝 Tasks":
        st.subheader("Your Tasks")

        new_task = st.text_input("Add new task")

        if st.button("Add Task"):
            if new_task:
                data[user]["tasks"].append(new_task)
                save_data(data)
                st.rerun()

        st.markdown("### ✅ Task List")
          tasks = ["Study", "Workout", "Read"]

for task in tasks:
    col1, col2 = st.columns([8,1])
    col1.write(f"- {task}")
            if col2.button("❌", key=i):
                data[user]["tasks"].pop(i)
                save_data(data)
                st.rerun()

    # STATS
    elif menu == "📊 Stats":
        st.subheader("📈 Your Stats")

        total_tasks = len(data[user]["tasks"])

        df = pd.DataFrame({
            "Category": ["Tasks"],
            "Count": [total_tasks]
        })

        st.bar_chart(df.set_index("Category"))

    # LOGOUT
    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

# ---------------- ROUTER ----------------
if st.session_state.logged_in:
    main_app()
else:
    login_page()

       

import streamlit as st
import json
import os
from datetime import date
import pandas as pd

st.set_page_config(page_title="Pro Productivity Tracker", page_icon="🚀")

USERS_FILE = "users.json"

# ------------------ FILE FUNCTIONS ------------------
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

# ------------------ LOGIN SYSTEM ------------------
if "user" not in st.session_state:
    st.session_state.user = None

users = load_users()

st.title("🔐 Login / Signup")

if st.session_state.user is None:
    choice = st.radio("Choose", ["Login", "Signup"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Signup":
        if st.button("Create Account"):
            if username in users:
                st.error("User already exists")
            else:
                users[username] = {
                    "password": password,
                    "tasks": []
                }
                save_users(users)
                st.success("Account created! Now login.")

    else:
        if st.button("Login"):
            if username in users and users[username]["password"] == password:
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid credentials")

# ------------------ MAIN APP ------------------
else:
    st.sidebar.write(f"👋 Welcome {st.session_state.user}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    user_data = users[st.session_state.user]
    tasks = user_data["tasks"]

    st.title("🚀 Your Productivity Dashboard")

    # ➕ Add Task
    st.subheader("➕ Add Task")

    task = st.text_input("Task")
    due = st.date_input("Due date", value=date.today())
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])

    if st.button("Add Task"):
        if task.strip():
            tasks.append({
                "task": task,
                "done": False,
                "due": str(due),
                "priority": priority
            })
            save_users(users)
            st.rerun()

    # 📝 Show Tasks
    st.subheader("📝 Tasks")

    for i, t in enumerate(tasks):
        col1, col2, col3, col4 = st.columns([0.1, 0.4, 0.3, 0.2])

        with col1:
            new_status = st.checkbox("", value=t["done"], key=f"check_{i}")
            if new_status != t["done"]:
                t["done"] = new_status
                save_users(users)
                st.rerun()

        with col2:
            if t["done"]:
                st.markdown(f"~~{t['task']}~~")
            else:
                st.write(t["task"])

        with col3:
            st.write(f"📅 {t['due']}")
            st.write(f"🔥 {t['priority']}")

        with col4:
            if st.button("❌", key=f"del_{i}"):
                tasks.pop(i)
                save_users(users)
                st.rerun()

    # 📊 Progress
    st.subheader("📊 Progress")

    total = len(tasks)
    completed = sum(1 for t in tasks if t["done"])

    if total > 0:
        st.progress(completed / total)
        st.write(f"✅ {completed}/{total} done")

        df = pd.DataFrame(tasks)
        st.bar_chart(df["done"].value_counts())
    else:
        st.info("No tasks yet")

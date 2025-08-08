import streamlit as st
import requests

# FastAPI base URL
API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="User Portal", layout="centered")

# Session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# ---------- SIDEBAR NAVIGATION ----------
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Go to", ["Home", "Register", "Login", "Upload CSV"]
)

# ---------- HOME ----------
if menu == "Home":
    st.title("Welcome to the User Portal")
    st.write("Use the sidebar to Register, Login, or Upload CSV files.")

# ---------- REGISTER ----------
elif menu == "Register":
    st.title("Register")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    preferences = st.multiselect(
        "Select Preferences",
        ["plastic", "metal", "glass", "paper", "organic", "e-waste"]
    )

    if st.button("Register"):
        if not username or not password:
            st.warning("Username and password are required.")
        else:
            payload = {
                "username": username,
                "password": password,
                "preferences": preferences
            }
            try:
                res = requests.post(f"{API_BASE}/Register", json=payload)
                if res.status_code == 200:
                    st.success("Registered successfully!")
                else:
                    st.error(f"Error: {res.json()['detail']}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI.")

# ---------- LOGIN ----------
elif menu == "Login":
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not username or not password:
            st.warning("Both fields required.")
        else:
            payload = {"username": username, "password": password}
            try:
                res = requests.post(f"{API_BASE}/Login", json=payload)
                if res.status_code == 200:
                    st.success("Login successful!")
                    st.session_state.logged_in = True
                    st.session_state.username = username
                else:
                    st.error(f"Error: {res.json()['detail']}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI.")

# ---------- CSV UPLOAD ----------
elif menu == "Upload CSV":
    st.title("Upload CSV")

    if not st.session_state.logged_in:
        st.warning("Please login first to upload CSV files.")
        st.stop()

    st.success(f"Logged in as: {st.session_state.username}")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file and st.button("Upload"):
        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")
        }
        try:
            res = requests.post(f"{API_BASE}/upload_csv", files=files)
            if res.status_code == 200:
                result = res.json()
                st.success(result["message"])
                st.write(f"Total Rows: {result['rows']}")
            else:
                st.error(f"Error: {res.json()['detail']}")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to FastAPI.")

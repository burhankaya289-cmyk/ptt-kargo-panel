import streamlit as st


def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "username" not in st.session_state:
        st.session_state.username = ""

    if "role" not in st.session_state:
        st.session_state.role = ""

    if not st.session_state.logged_in:
        st.warning("Bu sayfayı görmek için giriş yapmalısınız.")
        st.stop()


def current_user():
    return st.session_state.get("username", "")


def current_role():
    return st.session_state.get("role", "")


def is_admin():
    return st.session_state.get("role", "") == "Admin"

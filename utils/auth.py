import streamlit as st


def require_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

        st.markdown("""
        <style>
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.error("Bu sayfayı görmek için giriş yapmalısınız.")
        st.stop()


def current_user():
    return st.session_state.get("username", "admin")


def current_role():
    return st.session_state.get("role", "Operatör")


def is_admin():
    return current_role() == "Admin"

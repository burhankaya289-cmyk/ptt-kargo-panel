import streamlit as st


def require_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "username" not in st.session_state:
        st.session_state.username = ""

    if "role" not in st.session_state:
        st.session_state.role = ""

    query_user = st.query_params.get("user", "")
    query_role = st.query_params.get("role", "")

    if query_user and query_role and not st.session_state.logged_in:
        st.session_state.logged_in = True
        st.session_state.username = query_user
        st.session_state.role = query_role

    if not st.session_state.logged_in:
        st.markdown("""
        <style>
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.error("Bu sayfayı görmek için giriş yapmalısınız.")

        if st.button("Giriş ekranına dön"):
            st.switch_page("app.py")

        st.stop()


def current_user():
    return st.session_state.get("username", "admin")


def current_role():
    return st.session_state.get("role", "Operatör")


def is_admin():
    return str(current_role()).strip().lower() == "admin"

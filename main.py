import streamlit as st
from service import bootstrap

st.set_page_config(page_title="客户人脉管理系统", layout="wide")

bootstrap()

for key, default in [
    ('view', 'dashboard'),
    ('customer_id', None),
    ('form_mode', 'add'),
    ('list_reset', 0),
]:
    if key not in st.session_state:
        st.session_state[key] = default

with st.sidebar:
    st.title("客户人脉管理系统")
    st.divider()
    if st.button("仪表盘", use_container_width=True):
        st.session_state.view = 'dashboard'
        st.rerun()
    if st.button("客户列表", use_container_width=True):
        st.session_state.view = 'list'
        st.rerun()

from ui_dashboard import render_dashboard
from ui_list import render_list
from ui_detail import render_detail
from ui_form import render_form

if st.session_state.view == 'dashboard':
    render_dashboard()
elif st.session_state.view == 'list':
    render_list()
elif st.session_state.view == 'detail':
    render_detail()
elif st.session_state.view == 'form':
    render_form()

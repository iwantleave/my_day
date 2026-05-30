import streamlit as st
import pandas as pd
from datetime import date
from service import get_dashboard_stats, search_customers


def render_dashboard():
    stats = get_dashboard_stats()

    st.header("仪表盘")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总客户数", stats['total'])
    with col2:
        st.metric("今日需跟进", stats['today_followup'])
    with col3:
        st.metric("逾期未跟进", stats['overdue_followup'])

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("客户状态分布")
        dist = stats['status_distribution']
        if dist:
            df_status = pd.DataFrame([
                {'状态': k, '数量': v} for k, v in dist.items()
            ])
            st.bar_chart(df_status.set_index('状态'), y='数量')
        else:
            st.info("暂无客户数据")

    with col_b:
        st.subheader("今日需跟进")
        today_rows = search_customers(
            search='', status='', level='', source='',
            sort_by='next_follow', sort_desc=False,
        )
        today = date.today().isoformat()
        today_list = [r for r in today_rows if r.get('next_follow') == today]
        if today_list:
            for r in today_list:
                with st.container(border=True):
                    cols = st.columns([3, 2, 1])
                    with cols[0]:
                        st.write(f"**{r['name']}**")
                    with cols[1]:
                        st.write(r.get('company', ''))
                    with cols[2]:
                        if st.button("查看", key=f"dash_{r['id']}", use_container_width=True):
                            st.session_state.customer_id = r['id']
                            st.session_state.view = 'detail'
                            st.rerun()
        else:
            st.info("今日无待跟进客户")

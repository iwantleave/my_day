import streamlit as st
import pandas as pd
from service import search_customers, export_csv

STATUS_OPTIONS = ['全部', '潜在客户', '意向客户', '谈判中', '已成交', '流失']
LEVEL_OPTIONS = ['全部', 'A', 'B', 'C']
SOURCE_OPTIONS = ['全部', '展会', '朋友介绍', '线上广告', '陌拜', '线上咨询', '其他']
SORT_OPTIONS = {
    'name': '姓名',
    'company': '公司',
    'position': '职位',
    'level': '等级',
    'status': '状态',
    'next_follow': '下次跟进',
    'amount': '预计金额',
    'updated_at': '更新时间',
    'created_at': '创建时间',
}
SORT_DESC_DEFAULT = {
    'updated_at': True, 'created_at': True, 'amount': True,
    'name': False, 'company': False, 'position': False,
    'level': False, 'status': False, 'next_follow': False,
}


def render_list():
    st.header("客户列表")

    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1.5])
    with col1:
        search = st.text_input("搜索姓名、公司、手机、微信", key="list_search")
    with col2:
        status_filter = st.selectbox("状态", STATUS_OPTIONS, key="list_status")
    with col3:
        level_filter = st.selectbox("等级", LEVEL_OPTIONS, key="list_level")
    with col4:
        source_filter = st.selectbox("来源", SOURCE_OPTIONS, key="list_source")
    with col5:
        sort_by = st.selectbox(
            "排序",
            options=list(SORT_OPTIONS.keys()),
            format_func=lambda x: SORT_OPTIONS[x],
            key="list_sort",
        )

    col_a, col_b, _ = st.columns([1, 1, 10])
    with col_a:
        if st.button("添加客户", type="primary", use_container_width=True):
            st.session_state.form_mode = 'add'
            st.session_state.customer_id = None
            st.session_state.view = 'form'
            st.rerun()
    with col_b:
        csv_data = export_csv()
        st.download_button(
            label="导出CSV",
            data=csv_data,
            file_name="客户列表.csv",
            mime="text/csv",
            use_container_width=True,
        )

    status_param = status_filter if status_filter != '全部' else ''
    level_param = level_filter if level_filter != '全部' else ''
    source_param = source_filter if source_filter != '全部' else ''
    sort_desc = SORT_DESC_DEFAULT.get(sort_by, True)

    rows = search_customers(
        search=search,
        status=status_param,
        level=level_param,
        source=source_param,
        sort_by=sort_by,
        sort_desc=sort_desc,
    )

    if not rows:
        st.info("暂无客户数据")
        return

    df = pd.DataFrame(rows)
    table_key = f"customer_list_{st.session_state.get('list_reset', 0)}"

    display_cols = ['name', 'company', 'position', 'level', 'status', 'last_contact', 'next_follow', 'amount']
    col_labels = ['姓名', '公司', '职位', '等级', '状态', '最后联系', '下次跟进', '预计金额']

    display_df = pd.DataFrame()
    for col, label in zip(display_cols, col_labels):
        if col in df.columns:
            display_df[label] = df[col]
    display_df['预计金额'] = display_df['预计金额'].apply(
        lambda x: f"{x:,.0f}" if pd.notna(x) and x else '-'
    )
    display_df['最后联系'] = display_df['最后联系'].fillna('-')
    display_df['下次跟进'] = display_df['下次跟进'].fillna('-')

    selection = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        key=table_key,
        on_select="rerun",
        selection_mode="single-row",
    )

    if selection and selection.selection and selection.selection.rows:
        idx = selection.selection.rows[0]
        if idx < len(rows):
            cust = rows[idx]
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([2, 2, 2, 6])
                with c1:
                    st.markdown(f"**{cust['name']}**")
                with c2:
                    st.write(cust.get('company', ''))
                with c3:
                    st.write(cust.get('status', ''))
                with c4:
                    ca, cb, cc = st.columns([1, 1, 1])
                    with ca:
                        if st.button("查看详情", type="primary", key="detail_btn"):
                            st.session_state.customer_id = cust['id']
                            st.session_state.view = 'detail'
                            st.rerun()
                    with cb:
                        if st.button("编辑", key="edit_btn"):
                            st.session_state.form_mode = 'edit'
                            st.session_state.customer_id = cust['id']
                            st.session_state.view = 'form'
                            st.rerun()

    st.caption(f"共 {len(rows)} 位客户（点击行选中后可查看详情或编辑）")

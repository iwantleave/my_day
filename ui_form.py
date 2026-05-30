import streamlit as st
from service import add_customer, edit_customer, get_customer, calculate_age

STATUS_OPTIONS = ['潜在客户', '意向客户', '谈判中', '已成交', '流失']
LEVEL_OPTIONS = ['A', 'B', 'C']
GENDER_OPTIONS = ['', '男', '女', '其他']
SOURCE_OPTIONS = ['', '展会', '朋友介绍', '线上广告', '陌拜', '线上咨询', '其他']


def render_form():
    is_edit = st.session_state.form_mode == 'edit'
    customer_id = st.session_state.get('customer_id')
    customer = get_customer(customer_id) if is_edit and customer_id else None

    st.header("编辑客户" if is_edit else "添加客户")

    if st.button("← 返回"):
        if is_edit and customer_id:
            st.session_state.view = 'detail'
        else:
            st.session_state.list_reset += 1
            st.session_state.view = 'list'
        st.rerun()

    with st.form("customer_form", clear_on_submit=False):
        st.subheader("基本信息")
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("姓名*", value=customer.name if customer else '')
        with c2:
            gender = st.selectbox("性别", GENDER_OPTIONS, index=GENDER_OPTIONS.index(customer.gender) if customer and customer.gender in GENDER_OPTIONS else 0)

        c1, c2, c3 = st.columns(3)
        with c1:
            birthday = st.date_input("生日", value=None)
            if customer and customer.birthday:
                from datetime import datetime
                try:
                    birthday = datetime.strptime(customer.birthday, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    pass
        with c2:
            age = None
            if birthday:
                age = calculate_age(birthday.isoformat())
            elif customer and customer.age is not None:
                age = customer.age
            st.number_input("年龄", value=age, disabled=True)
        with c3:
            death_date = st.date_input("去世日期", value=None)
            if customer and customer.death_date:
                from datetime import datetime
                try:
                    death_date = datetime.strptime(customer.death_date, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    pass

        st.subheader("公司信息")
        c1, c2 = st.columns(2)
        with c1:
            company = st.text_input("公司", value=customer.company if customer else '')
        with c2:
            department = st.text_input("部门", value=customer.department if customer else '')
        position = st.text_input("职位", value=customer.position if customer else '')

        st.subheader("联系方式")
        c1, c2 = st.columns(2)
        with c1:
            phone = st.text_input("手机", value=customer.phone if customer else '')
        with c2:
            wechat = st.text_input("微信", value=customer.wechat if customer else '')
        c1, c2 = st.columns(2)
        with c1:
            qq = st.text_input("QQ", value=customer.qq if customer else '')
        with c2:
            email = st.text_input("邮箱", value=customer.email if customer else '')
        address = st.text_input("地址", value=customer.address if customer else '')

        st.subheader("销售信息")
        c1, c2 = st.columns(2)
        with c1:
            source = st.selectbox("来源", SOURCE_OPTIONS, index=SOURCE_OPTIONS.index(customer.source) if customer and customer.source in SOURCE_OPTIONS else 0)
        with c2:
            status_val = customer.status if customer else '潜在客户'
            status_idx = STATUS_OPTIONS.index(status_val) if status_val in STATUS_OPTIONS else 0
            status = st.selectbox("客户状态", STATUS_OPTIONS, index=status_idx)

        c1, c2 = st.columns(2)
        with c1:
            level_val = customer.level if customer else 'C'
            level_idx = LEVEL_OPTIONS.index(level_val) if level_val in LEVEL_OPTIONS else 0
            level = st.selectbox("客户等级", LEVEL_OPTIONS, index=level_idx)
        with c2:
            sales = st.text_input("负责销售", value=customer.sales if customer else '')

        product = st.text_input("意向产品", value=customer.product if customer else '')

        c1, c2 = st.columns(2)
        with c1:
            amount = st.number_input("预计金额（元）", value=float(customer.amount) if customer and customer.amount else 0.0, min_value=0.0, step=1000.0, format="%.0f")
        with c2:
            deal_date = st.date_input("预计成交日期", value=None)
            if customer and customer.deal_date:
                from datetime import datetime
                try:
                    deal_date = datetime.strptime(customer.deal_date, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    pass

        next_follow = st.date_input("下次跟进", value=None)
        if customer and customer.next_follow:
            from datetime import datetime
            try:
                next_follow = datetime.strptime(customer.next_follow, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                pass

        st.subheader("其他信息")
        tags = st.text_input("标签（逗号分隔）", value=customer.tags if customer else '')
        remark = st.text_area("备注", value=customer.remark if customer else '')

        saved = st.form_submit_button("保存", type="primary", use_container_width=True)

        if saved:
            if not name.strip():
                st.error("请输入客户姓名")
            else:
                _fmt = lambda d: d.isoformat() if d else ''
                data = {
                    'name': name.strip(),
                    'gender': gender,
                    'birthday': _fmt(birthday),
                    'death_date': _fmt(death_date),
                    'company': company,
                    'department': department,
                    'position': position,
                    'phone': phone,
                    'wechat': wechat,
                    'qq': qq,
                    'email': email,
                    'address': address,
                    'source': source,
                    'status': status,
                    'level': level,
                    'sales': sales,
                    'product': product,
                    'amount': amount,
                    'deal_date': _fmt(deal_date),
                    'next_follow': _fmt(next_follow),
                    'tags': tags,
                    'remark': remark,
                }
                try:
                    if is_edit and customer_id:
                        data['id'] = customer_id
                        edit_customer(data)
                        st.success("客户已更新")
                        st.session_state.view = 'detail'
                    else:
                        add_customer(data)
                        st.success("客户已添加")
                        st.session_state.list_reset += 1
                        st.session_state.view = 'list'
                    st.rerun()
                except Exception as ex:
                    st.error(f"保存失败: {ex}")

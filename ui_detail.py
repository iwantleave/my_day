import streamlit as st
from service import get_customer, get_contacts, remove_customer, add_contact


def render_detail():
    customer_id = st.session_state.get('customer_id')
    if not customer_id:
        st.session_state.view = 'list'
        st.rerun()
        return

    customer = get_customer(customer_id)
    if not customer:
        st.error("客户不存在")
        if st.button("返回列表"):
            st.session_state.view = 'list'
            st.rerun()
        return

    if st.button("← 返回列表"):
        st.session_state.list_reset += 1
        st.session_state.view = 'list'
        st.rerun()

    st.header(customer.name)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("编辑", type="primary"):
            st.session_state.form_mode = 'edit'
            st.session_state.view = 'form'
            st.rerun()
    with col2:
        if st.button("删除客户", type="secondary"):
            st.session_state.confirm_delete = True
            st.rerun()

    if st.session_state.get('confirm_delete'):
        st.warning(f"确认删除客户「{customer.name}」？此操作不可撤销，该客户的所有联系记录也将被删除。")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("确认删除"):
                remove_customer(customer_id)
                st.session_state.confirm_delete = False
                st.session_state.list_reset += 1
                st.session_state.view = 'list'
                st.success(f"已删除客户「{customer.name}」")
                st.rerun()
        with c2:
            if st.button("取消"):
                st.session_state.confirm_delete = False
                st.rerun()

    st.divider()

    info_items = []
    if customer.gender:
        info_items.append(("性别", customer.gender))
    if customer.age is not None:
        info_items.append(("年龄", f"{customer.age}岁"))
    if customer.birthday:
        info_items.append(("生日", customer.birthday))
    if customer.death_date:
        info_items.append(("去世", customer.death_date))
    if customer.company:
        info_items.append(("公司", customer.company))
    if customer.department:
        info_items.append(("部门", customer.department))
    if customer.position:
        info_items.append(("职位", customer.position))
    if customer.phone:
        info_items.append(("手机", customer.phone))
    if customer.wechat:
        info_items.append(("微信", customer.wechat))
    if customer.qq:
        info_items.append(("QQ", customer.qq))
    if customer.email:
        info_items.append(("邮箱", customer.email))
    if customer.address:
        info_items.append(("地址", customer.address))
    if customer.source:
        info_items.append(("来源", customer.source))
    if customer.status:
        info_items.append(("客户状态", customer.status))
    if customer.level:
        info_items.append(("客户等级", customer.level))
    if customer.sales:
        info_items.append(("负责销售", customer.sales))
    if customer.product:
        info_items.append(("意向产品", customer.product))
    if customer.amount:
        info_items.append(("预计金额", f"{customer.amount:,.0f}元"))
    if customer.deal_date:
        info_items.append(("预计成交", customer.deal_date))
    if customer.next_follow:
        info_items.append(("下次跟进", customer.next_follow))

    for i in range(0, len(info_items), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(info_items):
                k, v = info_items[i + j]
                with cols[j]:
                    st.markdown(f"**{k}**: {v}")

    if customer.tags:
        st.markdown(f"**标签**: {customer.tags}")
    if customer.remark:
        st.markdown(f"**备注**: {customer.remark}")

    st.divider()
    st.subheader("联系记录")

    with st.expander("添加联系记录"):
        with st.form("add_contact_form", clear_on_submit=True):
            ct_time = st.date_input("联系时间")
            ct_method = st.selectbox(
                "联系方式", ['', '电话', '微信', '邮件', '面谈', '短信', '其他']
            )
            ct_summary = st.text_area("沟通摘要*")
            ct_result = st.selectbox(
                "联系结果", ['', '有意向', '暂不需要', '约见成功', '已拒绝', '其他']
            )
            ct_next = st.date_input("下次跟进时间", value=None)

            if st.form_submit_button("保存记录", type="primary"):
                if not ct_summary.strip():
                    st.error("请输入沟通摘要")
                else:
                    add_contact({
                        'customer_id': customer_id,
                        'time': ct_time.isoformat(),
                        'method': ct_method,
                        'summary': ct_summary,
                        'result': ct_result,
                        'next_follow': ct_next.isoformat() if ct_next else '',
                    })
                    st.success("联系记录已添加")
                    st.rerun()

    contacts = get_contacts(customer_id)
    if contacts:
        for ct in contacts:
            with st.container(border=True):
                cols = st.columns([1, 1, 2, 4])
                with cols[0]:
                    st.markdown(f"**{ct['time']}**")
                with cols[1]:
                    method = ct.get('method', '')
                    st.markdown(f"`{method}`" if method else "")
                with cols[2]:
                    result = ct.get('result', '')
                    if result:
                        st.markdown(f"→ {result}")
                with cols[3]:
                    st.markdown(ct['summary'])
                if ct.get('next_follow'):
                    st.caption(f"下次跟进: {ct['next_follow']}")
    else:
        st.info("暂无联系记录")

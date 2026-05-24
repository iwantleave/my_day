from nicegui import ui
from service import get_customer, get_contacts, remove_customer, add_contact
from ui_form import show_form, METHOD_OPTIONS, RESULT_OPTIONS


def show_detail(customer_id, on_done=None):
    customer = get_customer(customer_id)
    if not customer:
        ui.notify('客户不存在', type='warning')
        return

    def refresh():
        nonlocal customer
        customer = get_customer(customer_id)
        _rebuild()

    with ui.dialog() as dialog, ui.card().classes('w-[900px] max-h-[90vh] overflow-y-auto p-6'):
        def _confirm_delete():
            with ui.dialog() as confirm, ui.card().classes('p-6'):
                ui.label(f'确认删除客户"{customer.name}"？').classes('text-lg')
                ui.label('此操作不可撤销，该客户的所有联系记录也将被删除。').classes('text-sm text-gray-500 mt-2')
                with ui.row().classes('w-full justify-end gap-2 mt-4'):
                    ui.button('取消', on_click=confirm.close).props('flat')
                    ui.button('确认删除', on_click=lambda: _do_delete(confirm)).props('unelevated').classes('bg-red-600 text-white')
            confirm.open()

        def _do_delete(confirm):
            confirm.close()
            dialog.close()
            remove_customer(customer_id)
            ui.notify(f'已删除客户"{customer.name}"', type='success')
            if on_done:
                on_done()

        def _rebuild():
            content.clear()

            with content:
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label(customer.name).classes('text-2xl font-bold')
                    with ui.row().classes('gap-2'):
                        ui.button('编辑', icon='edit', on_click=lambda: show_form(customer_id, on_done=refresh)).props('flat')
                        ui.button('删除', icon='delete', on_click=_confirm_delete).props('flat').classes('text-red-600')
                        ui.button('✕', on_click=dialog.close).props('flat').classes('text-gray-400')

                with ui.row().classes('w-full gap-4 mt-2'):
                    if customer.gender:
                        ui.label(f"性别: {customer.gender}").classes('text-sm')
                    if customer.age is not None:
                        ui.label(f"年龄: {customer.age}岁").classes('text-sm')
                    if customer.birthday:
                        ui.label(f"生日: {customer.birthday}").classes('text-sm')
                    if customer.death_date:
                        ui.label(f"去世: {customer.death_date}").classes('text-sm text-red-500')

                ui.separator().classes('my-3')

                with ui.grid(columns=3).classes('w-full gap-x-8 gap-y-2'):
                    _info_row('公司', customer.company)
                    _info_row('部门', customer.department)
                    _info_row('职位', customer.position)
                    _info_row('手机', customer.phone)
                    _info_row('微信', customer.wechat)
                    _info_row('QQ', customer.qq)
                    _info_row('邮箱', customer.email)
                    _info_row('地址', customer.address)
                    _info_row('来源', customer.source)
                    _info_row('客户状态', customer.status)
                    _info_row('客户等级', customer.level)
                    _info_row('负责销售', customer.sales)
                    _info_row('意向产品', customer.product)
                    _info_row('预计金额', f"{customer.amount:,.0f}元" if customer.amount else '')
                    _info_row('预计成交', customer.deal_date)
                    _info_row('下次跟进', customer.next_follow)

                with ui.row().classes('w-full gap-2 mt-2'):
                    if customer.tags:
                        for tag in customer.tags.split(','):
                            tag = tag.strip()
                            if tag:
                                ui.chip(tag).props('small')
                    if customer.remark:
                        ui.label(f"备注: {customer.remark}").classes('text-sm text-gray-600 mt-1')

                ui.separator().classes('my-3')

                with ui.row().classes('w-full items-center justify-between'):
                    ui.label('联系记录').classes('text-lg font-bold')
                    ui.button('添加记录', icon='add', on_click=lambda: _show_add_contact()).props('unelevated').classes('bg-green-600 text-white')

                contacts = get_contacts(customer_id)
                if contacts:
                    for ct in contacts:
                        with ui.card().classes('w-full p-3'):
                            with ui.row().classes('w-full items-center gap-3'):
                                ui.icon('chat').classes('text-blue-500')
                                ui.label(ct['time']).classes('text-sm font-bold')
                                ui.label(f"[{ct.get('method', '')}]").classes('text-sm text-gray-500')
                                if ct.get('result'):
                                    ui.label(f"→ {ct['result']}").classes('text-sm')
                            ui.label(ct['summary']).classes('text-sm mt-1 ml-7')
                            if ct.get('next_follow'):
                                ui.label(f"下次跟进: {ct['next_follow']}").classes('text-xs text-gray-400 ml-7')
                else:
                    ui.label('暂无联系记录').classes('text-gray-400')

        def _show_add_contact():
            with ui.dialog() as add_dialog, ui.card().classes('w-[500px] p-6'):
                ui.label('添加联系记录').classes('text-xl font-bold mb-4')
                ct_time = ui.date_input('联系时间')
                ct_method = ui.select(METHOD_OPTIONS, label='联系方式').classes('w-full').props('outlined dense')
                ct_summary = ui.textarea('沟通摘要*').classes('w-full').props('outlined dense rows-3')
                ct_result = ui.select(RESULT_OPTIONS, label='联系结果').classes('w-full').props('outlined dense')
                ct_next = ui.date_input('下次跟进时间')

                def save_contact():
                    if not ct_summary.value:
                        ui.notify('请输入沟通摘要', type='warning')
                        return
                    add_contact({
                        'customer_id': customer_id,
                        'time': ct_time.value,
                        'method': ct_method.value,
                        'summary': ct_summary.value,
                        'result': ct_result.value,
                        'next_follow': ct_next.value,
                    })
                    ui.notify('联系记录已添加', type='success')
                    add_dialog.close()
                    refresh()
                    if on_done:
                        on_done()

                with ui.row().classes('w-full justify-end gap-2 mt-4'):
                    ui.button('取消', on_click=add_dialog.close).props('flat')
                    ui.button('保存', on_click=save_contact, icon='save').props('unelevated').classes('bg-blue-600 text-white')

                add_dialog.open()

        content = ui.column().classes('w-full')
        _rebuild()
        dialog.open()


def _info_row(label, value):
    if value:
        ui.label(f"{label}: {value}").classes('text-sm')

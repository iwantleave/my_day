from nicegui import ui
from service import add_customer, edit_customer, get_customer


STATUS_OPTIONS = ['潜在客户', '意向客户', '谈判中', '已成交', '流失']
LEVEL_OPTIONS = ['A', 'B', 'C']
GENDER_OPTIONS = ['男', '女', '其他']
SOURCE_OPTIONS = ['展会', '朋友介绍', '线上广告', '陌拜', '线上咨询', '其他']
METHOD_OPTIONS = ['电话', '微信', '邮件', '面谈', '短信', '其他']
RESULT_OPTIONS = ['有意向', '暂不需要', '约见成功', '已拒绝', '其他']


def show_form(customer_id=None, on_done=None):
    is_edit = customer_id is not None
    customer = get_customer(customer_id) if is_edit else None

    with ui.dialog() as dialog, ui.card().classes('w-[600px] max-h-[90vh] overflow-y-auto p-6'):
        ui.label('编辑客户' if is_edit else '添加客户').classes('text-xl font-bold mb-4')

        data = {}

        ui.label('基本信息').classes('text-lg font-bold text-blue-600 mt-2 mb-2')
        with ui.row().classes('w-full gap-4'):
            inp_name = ui.input('姓名*').classes('flex-1').props('outlined dense')
            inp_gender = ui.select(GENDER_OPTIONS, label='性别').classes('flex-1').props('outlined dense')
        with ui.row().classes('w-full gap-4'):
            inp_birthday = ui.date_input('生日', on_change=lambda e: _update_age(e.value)).classes('flex-1')
            inp_age = ui.number('年龄', precision=0).classes('w-24').props('outlined dense readonly')
            inp_death = ui.date_input('去世日期').classes('flex-1')

        ui.label('公司信息').classes('text-lg font-bold text-blue-600 mt-2 mb-2')
        with ui.row().classes('w-full gap-4'):
            inp_company = ui.input('公司').classes('flex-1').props('outlined dense')
            inp_department = ui.input('部门').classes('flex-1').props('outlined dense')
        inp_position = ui.input('职位').classes('w-full').props('outlined dense')

        ui.label('联系方式').classes('text-lg font-bold text-blue-600 mt-2 mb-2')
        with ui.row().classes('w-full gap-4'):
            inp_phone = ui.input('手机').classes('flex-1').props('outlined dense')
            inp_wechat = ui.input('微信').classes('flex-1').props('outlined dense')
        with ui.row().classes('w-full gap-4'):
            inp_qq = ui.input('QQ').classes('flex-1').props('outlined dense')
            inp_email = ui.input('邮箱').classes('flex-1').props('outlined dense')
        inp_address = ui.input('地址').classes('w-full').props('outlined dense')

        ui.label('销售信息').classes('text-lg font-bold text-blue-600 mt-2 mb-2')
        with ui.row().classes('w-full gap-4'):
            inp_source = ui.select(SOURCE_OPTIONS, label='来源', with_input=True).classes('flex-1').props('outlined dense')
            inp_status = ui.select(STATUS_OPTIONS, label='客户状态', value='潜在客户').classes('flex-1').props('outlined dense')
        with ui.row().classes('w-full gap-4'):
            inp_level = ui.select(LEVEL_OPTIONS, label='客户等级', value='C').classes('flex-1').props('outlined dense')
            inp_sales = ui.input('负责销售').classes('flex-1').props('outlined dense')
        inp_product = ui.input('意向产品').classes('w-full').props('outlined dense')
        with ui.row().classes('w-full gap-4'):
            inp_amount = ui.number('预计金额', precision=0, suffix='元').classes('flex-1').props('outlined dense')
            inp_deal_date = ui.date_input('预计成交日期').classes('flex-1')
        inp_next_follow = ui.date_input('下次跟进').classes('w-full')

        ui.label('其他信息').classes('text-lg font-bold text-blue-600 mt-2 mb-2')
        inp_tags = ui.input('标签（逗号分隔）').classes('w-full').props('outlined dense')
        inp_remark = ui.textarea('备注').classes('w-full').props('outlined dense rows-3')

        def _update_age(birthday):
            if birthday:
                from service import calculate_age
                age = calculate_age(birthday)
                inp_age.value = age
            else:
                inp_age.value = None

        if is_edit and customer:
            inp_name.value = customer.name
            inp_gender.value = customer.gender
            inp_birthday.value = customer.birthday
            inp_age.value = customer.age
            inp_death.value = customer.death_date
            inp_company.value = customer.company
            inp_department.value = customer.department
            inp_position.value = customer.position
            inp_phone.value = customer.phone
            inp_wechat.value = customer.wechat
            inp_qq.value = customer.qq
            inp_email.value = customer.email
            inp_address.value = customer.address
            inp_source.value = customer.source
            inp_status.value = customer.status
            inp_level.value = customer.level
            inp_sales.value = customer.sales
            inp_product.value = customer.product
            inp_amount.value = customer.amount
            inp_deal_date.value = customer.deal_date
            inp_next_follow.value = customer.next_follow
            inp_tags.value = customer.tags
            inp_remark.value = customer.remark

        def _collect():
            d = {
                'name': inp_name.value,
                'gender': inp_gender.value,
                'birthday': inp_birthday.value,
                'death_date': inp_death.value,
                'company': inp_company.value,
                'department': inp_department.value,
                'position': inp_position.value,
                'phone': inp_phone.value,
                'wechat': inp_wechat.value,
                'qq': inp_qq.value,
                'email': inp_email.value,
                'address': inp_address.value,
                'source': inp_source.value,
                'status': inp_status.value,
                'level': inp_level.value,
                'sales': inp_sales.value,
                'product': inp_product.value,
                'amount': inp_amount.value,
                'deal_date': inp_deal_date.value,
                'next_follow': inp_next_follow.value,
                'tags': inp_tags.value,
                'remark': inp_remark.value,
            }
            if is_edit:
                d['id'] = customer_id
            return d

        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('取消', on_click=lambda: _close()).props('flat')
            ui.button('保存', on_click=lambda: _save(), icon='save').props('unelevated').classes('bg-blue-600 text-white')

        def _save():
            d = _collect()
            if not d['name']:
                ui.notify('请输入客户姓名', type='warning')
                return
            try:
                if is_edit:
                    edit_customer(d)
                    ui.notify('客户已更新', type='success')
                else:
                    add_customer(d)
                    ui.notify('客户已添加', type='success')
                _close()
                if on_done:
                    on_done()
            except Exception as ex:
                ui.notify(f'保存失败: {ex}', type='negative')

        def _close():
            dialog.close()

        dialog.open()

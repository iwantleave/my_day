from nicegui import ui
from service import bootstrap
from ui_list import list_content


@ui.page('/')
def index():
    with ui.header(elevated=True).classes('items-center justify-between px-4'):
        ui.label('客户人脉管理系统').classes('text-lg font-bold text-white')

    list_content()


bootstrap()
ui.run(title='客户人脉管理系统')

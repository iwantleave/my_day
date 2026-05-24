from nicegui import ui
from service import search_customers, export_csv
from ui_detail import show_detail
from ui_form import show_form
import io

STATUS_OPTIONS = ['', '潜在客户', '意向客户', '谈判中', '已成交', '流失']
LEVEL_OPTIONS = ['', 'A', 'B', 'C']
SOURCE_OPTIONS = ['', '展会', '朋友介绍', '线上广告', '陌拜', '线上咨询', '其他']
SORT_OPTIONS = {
    'updated_at': '更新时间',
    'created_at': '创建时间',
    'name': '姓名',
    'company': '公司',
    'status': '状态',
    'level': '等级',
    'next_follow': '下次跟进',
    'amount': '预计金额',
}
SORT_DIRECTION = {
    'updated_at': True,
    'created_at': True,
    'name': False,
    'company': False,
    'status': False,
    'level': False,
    'next_follow': False,
    'amount': True,
}

_search = ''
_filter_status = ''
_filter_level = ''
_filter_source = ''
_sort_by = 'updated_at'
_sort_desc = True
_table = None


def list_content():
    global _search, _filter_status, _filter_level, _filter_source, _sort_by, _sort_desc, _table

    def refresh_table():
        rows = search_customers(
            search=_search,
            status=_filter_status,
            level=_filter_level,
            source=_filter_source,
            sort_by=_sort_by,
            sort_desc=_sort_desc,
        )
        for r in rows:
            r['last_contact'] = r.get('last_contact') or '-'
            r['next_follow'] = r.get('next_follow') or '-'
            r['amount_display'] = f"{r['amount']:,.0f}" if r.get('amount') else '-'
        if _table:
            _table.rows = rows

    def refresh_all():
        refresh_table()

    def on_search_change(value):
        global _search
        _search = value
        refresh_table()

    def on_filter_change(name):
        def handler(e):
            globals()[f'_filter_{name}'] = e.value
            refresh_table()
        return handler

    def on_sort_change(e):
        global _sort_by, _sort_desc
        _sort_by = e.value
        _sort_desc = SORT_DIRECTION.get(e.value, True)
        refresh_table()

    def do_export():
        csv_data = export_csv()
        ui.download(csv_data, '客户列表.csv')

    with ui.column().classes('w-full gap-4 p-4'):
        ui.label('客户列表').classes('text-2xl font-bold')

        with ui.row().classes('w-full items-center gap-2 flex-wrap'):
            ui.input('搜索姓名、公司、手机、微信…') \
                .props('outlined dense') \
                .classes('w-64') \
                .bind_value_to(globals(), '_search') \
                .on('keydown.enter', lambda: on_search_change(_search))
            ui.select(STATUS_OPTIONS, label='状态', on_change=on_filter_change('status')) \
                .props('outlined dense').classes('w-32')
            ui.select(LEVEL_OPTIONS, label='等级', on_change=on_filter_change('level')) \
                .props('outlined dense').classes('w-28')
            ui.select(SOURCE_OPTIONS, label='来源', on_change=on_filter_change('source')) \
                .props('outlined dense').classes('w-32')
            ui.select(SORT_OPTIONS, label='排序', value='updated_at', on_change=on_sort_change) \
                .props('outlined dense').classes('w-40')
            ui.button('添加', icon='add', on_click=lambda: show_form(None, on_done=refresh_all)) \
                .props('unelevated').classes('bg-blue-600 text-white')
            ui.button('导出CSV', icon='download', on_click=do_export).props('flat')
            ui.button('刷新', icon='refresh', on_click=refresh_table).props('flat')

        columns = [
            {'name': 'name', 'label': '姓名', 'field': 'name', 'sortable': True, 'align': 'left'},
            {'name': 'company', 'label': '公司', 'field': 'company', 'sortable': True, 'align': 'left'},
            {'name': 'position', 'label': '职位', 'field': 'position', 'sortable': True, 'align': 'left'},
            {'name': 'level', 'label': '等级', 'field': 'level', 'sortable': True, 'align': 'center'},
            {'name': 'status', 'label': '状态', 'field': 'status', 'sortable': True, 'align': 'center'},
            {'name': 'last_contact', 'label': '最后联系', 'field': 'last_contact', 'sortable': True, 'align': 'center'},
            {'name': 'next_follow', 'label': '下次跟进', 'field': 'next_follow', 'sortable': True, 'align': 'center'},
            {'name': 'amount_display', 'label': '预计金额', 'field': 'amount_display', 'sortable': False, 'align': 'right'},
            {'name': 'actions', 'label': '操作', 'field': 'actions', 'sortable': False, 'align': 'center'},
        ]

        _table = ui.table(columns=columns, rows=[]).classes('w-full')
        _table.props('''
            flat bordered dense
            :pagination="{rowsPerPage: 20, rowsNumber: 0}"
        ''')
        _table.add_slot('body-cell-actions', r'''
            <q-td :props="props">
                <a href="javascript:void(0)"
                    class="text-blue-600 hover:text-blue-800 text-sm no-underline cursor-pointer detail-link">详情</a>
            </q-td>
        ''')
        _table.on('row-click',
            lambda e: show_detail(e.args['id'], on_done=refresh_all),
            args=[['id']],
            js_handler='(evt, row, index) => { if (evt.target.closest("a.detail-link")) { emit(row); } }',
        )

        refresh_table()

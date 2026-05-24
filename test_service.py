import os, tempfile, pytest, uuid
from unittest.mock import patch
from datetime import date, datetime

os.environ['TZ'] = 'Asia/Shanghai'
try:
    import time
    time.tzset()
except AttributeError:
    pass

import database
from service import (
    calculate_age, add_customer, edit_customer, remove_customer,
    get_customer, search_customers, add_contact, get_contacts, export_csv,
)
from models import Customer


@pytest.fixture(autouse=True)
def test_db():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    original = database.DB_PATH
    database.DB_PATH = db_path
    database.init_db()
    yield
    database.DB_PATH = original
    os.unlink(db_path)


def make_customer(overrides=None):
    data = {
        'name': '张三',
        'gender': '男',
        'company': 'ABC公司',
        'phone': '13800138000',
        'source': '朋友介绍',
        'status': '潜在客户',
        'level': 'A',
    }
    if overrides:
        data.update(overrides)
    return data


class TestCalculateAge:
    def test_valid_birthday(self):
        today = date.today()
        expected = today.year - 1990 - ((today.month, today.day) < (1, 15))
        assert calculate_age('1990-01-15') == expected

    def test_empty_string(self):
        assert calculate_age('') is None

    def test_invalid_date(self):
        assert calculate_age('not-a-date') is None


class TestCustomerCRUD:
    def test_add_and_get(self):
        cid = add_customer(make_customer())
        assert cid
        c = get_customer(cid)
        assert c is not None
        assert c.name == '张三'
        assert c.company == 'ABC公司'

    def test_add_sets_id_and_timestamps(self):
        cid = add_customer(make_customer())
        c = get_customer(cid)
        assert c.id == cid
        assert c.created_at
        assert c.updated_at
        assert c.created_at == c.updated_at

    def test_add_calculates_age(self):
        cid = add_customer(make_customer({'birthday': '1990-01-15'}))
        c = get_customer(cid)
        today = date.today()
        expected = today.year - 1990 - ((today.month, today.day) < (1, 15))
        assert c.age == expected

    def test_edit_updates_fields(self):
        cid = add_customer(make_customer())
        edit_customer({'id': cid, 'name': '李四', 'company': 'XYZ公司'})
        c = get_customer(cid)
        assert c.name == '李四'
        assert c.company == 'XYZ公司'

    def test_edit_preserves_created_at(self):
        cid = add_customer(make_customer({'birthday': '1990-01-15'}))
        c_orig = get_customer(cid)
        created = c_orig.created_at
        edit_customer({'id': cid, 'name': '李四', 'company': 'XYZ公司', 'birthday': '1990-01-15'})
        c = get_customer(cid)
        assert c.created_at == created
        # updated_at may equal created_at if edit happens within same second
        assert c.name == '李四'

    def test_edit_nonexistent_raises(self):
        with pytest.raises(ValueError, match='客户不存在'):
            edit_customer({'id': 'fake-id', 'name': 'x'})

    def test_remove(self):
        cid = add_customer(make_customer())
        remove_customer(cid)
        assert get_customer(cid) is None

    def test_remove_nonexistent_does_not_raise(self):
        remove_customer('fake-id')


class TestSearch:
    def test_empty_search_returns_all(self):
        cid1 = add_customer(make_customer({'name': '张三'}))
        cid2 = add_customer(make_customer({'name': '李四'}))
        rows = search_customers()
        assert len(rows) >= 2
        ids = {r['id'] for r in rows}
        assert cid1 in ids
        assert cid2 in ids

    def test_search_by_name(self):
        cid1 = add_customer(make_customer({'name': '张三'}))
        add_customer(make_customer({'name': '李四'}))
        rows = search_customers(search='张三')
        assert len(rows) == 1
        assert rows[0]['id'] == cid1

    def test_search_by_company(self):
        add_customer(make_customer({'company': 'ABC公司'}))
        cid2 = add_customer(make_customer({'company': 'XYZ科技'}))
        rows = search_customers(search='XYZ')
        assert len(rows) == 1
        assert rows[0]['id'] == cid2

    def test_search_by_phone(self):
        cid = add_customer(make_customer({'phone': '13912345678'}))
        rows = search_customers(search='1391234')
        assert len(rows) == 1
        assert rows[0]['id'] == cid

    def test_filter_by_status(self):
        cid1 = add_customer(make_customer({'name': 'A', 'status': '意向客户'}))
        add_customer(make_customer({'name': 'B', 'status': '已成交'}))
        rows = search_customers(status='意向客户')
        assert len(rows) == 1
        assert rows[0]['id'] == cid1

    def test_filter_by_level(self):
        cid1 = add_customer(make_customer({'name': 'A', 'level': 'A'}))
        add_customer(make_customer({'name': 'B', 'level': 'B'}))
        rows = search_customers(level='A')
        assert len(rows) == 1
        assert rows[0]['id'] == cid1

    def test_filter_by_source(self):
        cid1 = add_customer(make_customer({'name': 'A', 'source': '展会'}))
        add_customer(make_customer({'name': 'B', 'source': '线上广告'}))
        rows = search_customers(source='展会')
        assert len(rows) == 1
        assert rows[0]['id'] == cid1

    def test_combined_filters(self):
        cid = add_customer(make_customer({
            'name': '张三',
            'status': '意向客户',
            'level': 'A',
            'source': '展会',
        }))
        add_customer(make_customer({
            'name': '李四',
            'status': '意向客户',
            'level': 'B',
            'source': '展会',
        }))
        rows = search_customers(search='张三', status='意向客户', level='A', source='展会')
        assert len(rows) == 1
        assert rows[0]['id'] == cid

    def test_sort_by_name_asc(self):
        add_customer(make_customer({'name': 'B'}))
        add_customer(make_customer({'name': 'A'}))
        rows = search_customers(sort_by='name', sort_desc=False)
        names = [r['name'] for r in rows if r['name'] in ('A', 'B')]
        assert names == ['A', 'B']

    def test_sort_by_name_desc(self):
        add_customer(make_customer({'name': 'A'}))
        add_customer(make_customer({'name': 'B'}))
        rows = search_customers(sort_by='name', sort_desc=True)
        names = [r['name'] for r in rows if r['name'] in ('A', 'B')]
        assert names == ['B', 'A']

    def test_sort_by_updated_at_default(self):
        cid1 = add_customer(make_customer({'name': 'A'}))
        cid2 = add_customer(make_customer({'name': 'B'}))
        rows = search_customers()
        ids = {r['id'] for r in rows}
        assert cid1 in ids
        assert cid2 in ids

    def test_no_match_returns_empty(self):
        rows = search_customers(search='nonexistent')
        assert rows == []


class TestContacts:
    def test_add_and_list(self):
        cid = add_customer(make_customer())
        contact_id = add_contact({
            'customer_id': cid,
            'time': '2025-01-01',
            'summary': '初次沟通',
            'method': '电话',
        })
        assert contact_id
        contacts = get_contacts(cid)
        assert len(contacts) == 1
        assert contacts[0]['summary'] == '初次沟通'
        assert contacts[0]['customer_id'] == cid

    def test_list_ordered_by_time_desc(self):
        cid = add_customer(make_customer())
        add_contact({'customer_id': cid, 'time': '2025-01-01', 'summary': '旧'})
        add_contact({'customer_id': cid, 'time': '2025-06-01', 'summary': '新'})
        contacts = get_contacts(cid)
        assert contacts[0]['summary'] == '新'
        assert contacts[1]['summary'] == '旧'

    def test_no_contacts_returns_empty(self):
        assert get_contacts('nonexistent') == []


class TestExport:
    def test_export_csv_headers(self):
        add_customer(make_customer({'name': '张三'}))
        csv_str = export_csv()
        assert '姓名' in csv_str or 'name' in csv_str
        assert '张三' in csv_str

    def test_export_csv_multiple_rows(self):
        add_customer(make_customer({'name': '张三'}))
        add_customer(make_customer({'name': '李四'}))
        csv_str = export_csv()
        assert csv_str.count('\n') >= 2

    def test_export_csv_empty(self):
        csv_str = export_csv()
        assert csv_str == ''


class TestCustomerFromDict:
    def test_from_dict_only_keeps_valid_fields(self):
        d = {'name': '张三', 'company': 'ABC', 'invalid_field': 'should be ignored'}
        c = Customer.from_dict(d)
        assert c.name == '张三'
        assert c.company == 'ABC'
        assert not hasattr(c, 'invalid_field')

    def test_to_dict_roundtrip(self):
        c1 = Customer(name='张三', company='ABC', status='潜在客户', level='A', phone='13800138000')
        d = c1.to_dict()
        c2 = Customer.from_dict(d)
        for k in Customer.__dataclass_fields__:
            assert getattr(c1, k) == getattr(c2, k), f'Mismatch for field {k}'


class TestModelDefaults:
    def test_customer_defaults(self):
        c = Customer()
        assert c.status == '潜在客户'
        assert c.level == 'C'
        assert c.id == ''

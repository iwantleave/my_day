import uuid
from datetime import datetime, date
from models import Customer, ContactRecord
from database import (
    init_db, insert_customer, update_customer, delete_customer,
    get_customer as db_get_customer,
    list_customers as db_list_customers,
    insert_contact, list_contacts as db_list_contacts,
    export_all_customers, get_dashboard_stats as db_get_dashboard_stats,
)


def bootstrap():
    init_db()


def calculate_age(birthday_str: str) -> int | None:
    if not birthday_str:
        return None
    try:
        bd = datetime.strptime(birthday_str, '%Y-%m-%d').date()
        today = date.today()
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    except (ValueError, TypeError):
        return None


def _now() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def _today_str() -> str:
    return date.today().isoformat()


def add_customer(data: dict) -> str:
    c = Customer.from_dict(data)
    c.id = str(uuid.uuid4())
    c.age = calculate_age(c.birthday)
    now = _now()
    c.created_at = now
    c.updated_at = now
    insert_customer(c.to_dict())
    return c.id


def edit_customer(data: dict) -> None:
    existing = db_get_customer(data['id'])
    if not existing:
        raise ValueError('客户不存在')
    c = Customer.from_dict(data)
    c.age = calculate_age(c.birthday)
    c.created_at = existing['created_at']
    c.updated_at = _now()
    update_customer(c.to_dict())


def remove_customer(customer_id: str) -> None:
    delete_customer(customer_id)


def get_customer(customer_id: str) -> Customer | None:
    row = db_get_customer(customer_id)
    return Customer.from_dict(row) if row else None


def search_customers(
    search: str = '',
    status: str = '',
    level: str = '',
    source: str = '',
    sort_by: str = 'updated_at',
    sort_desc: bool = True,
) -> list[dict]:
    rows = db_list_customers(search, status, level, source, sort_by, sort_desc)
    return rows


def get_contacts(customer_id: str) -> list[dict]:
    return db_list_contacts(customer_id)


def add_contact(data: dict) -> str:
    r = ContactRecord.from_dict(data)
    r.id = str(uuid.uuid4())
    r.time = r.time or _now()[:10]
    insert_contact(r.to_dict())
    return r.id


def export_csv() -> str:
    import csv, io
    rows = export_all_customers()
    out = io.StringIO()
    if rows:
        writer = csv.DictWriter(out, fieldnames=rows[0].keys(), extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    return out.getvalue()


def get_dashboard_stats() -> dict:
    return db_get_dashboard_stats()

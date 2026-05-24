import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crm.db')

SORT_WHITELIST = {
    'name', 'company', 'level', 'status', 'amount',
    'next_follow', 'updated_at', 'created_at', 'position',
}


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            id           TEXT PRIMARY KEY,
            name         TEXT NOT NULL,
            gender       TEXT,
            birthday     TEXT,
            age          INTEGER,
            death_date   TEXT,
            company      TEXT,
            department   TEXT,
            position     TEXT,
            phone        TEXT,
            wechat       TEXT,
            qq           TEXT,
            email        TEXT,
            address      TEXT,
            source       TEXT,
            status       TEXT DEFAULT '潜在客户',
            level        TEXT DEFAULT 'C',
            product      TEXT,
            amount       REAL,
            deal_date    TEXT,
            sales        TEXT,
            next_follow  TEXT,
            tags         TEXT,
            remark       TEXT,
            created_at   TEXT,
            updated_at   TEXT
        );
        CREATE TABLE IF NOT EXISTS contacts (
            id           TEXT PRIMARY KEY,
            customer_id  TEXT NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
            time         TEXT NOT NULL,
            method       TEXT,
            summary      TEXT NOT NULL,
            result       TEXT,
            next_follow  TEXT
        );
    """)
    conn.commit()
    conn.close()


def insert_customer(data: dict) -> None:
    conn = get_conn()
    keys = ', '.join(data.keys())
    vals = ', '.join('?' for _ in data)
    conn.execute(f"INSERT INTO customers ({keys}) VALUES ({vals})", list(data.values()))
    conn.commit()
    conn.close()


def update_customer(data: dict) -> None:
    conn = get_conn()
    sets = ', '.join(f"{k} = ?" for k in data if k != 'id')
    vals = [v for k, v in data.items() if k != 'id']
    vals.append(data['id'])
    conn.execute(f"UPDATE customers SET {sets} WHERE id = ?", vals)
    conn.commit()
    conn.close()


def delete_customer(customer_id: str) -> None:
    conn = get_conn()
    conn.execute("DELETE FROM customers WHERE id = ?", [customer_id])
    conn.commit()
    conn.close()


def get_customer(customer_id: str) -> dict | None:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM customers WHERE id = ?", [customer_id]
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def list_customers(
    search: str = '',
    status: str = '',
    level: str = '',
    source: str = '',
    sort_by: str = 'updated_at',
    sort_desc: bool = True,
) -> list[dict]:
    conn = get_conn()
    conditions = []
    params = []

    if search:
        conditions.append(
            "(c.name LIKE ? OR c.company LIKE ? OR c.phone LIKE ? OR c.wechat LIKE ?)"
        )
        p = f'%{search}%'
        params.extend([p, p, p, p])
    if status:
        conditions.append("c.status = ?")
        params.append(status)
    if level:
        conditions.append("c.level = ?")
        params.append(level)
    if source:
        conditions.append("c.source = ?")
        params.append(source)

    where = ' AND '.join(conditions) if conditions else '1'
    sort_col = sort_by if sort_by in SORT_WHITELIST else 'updated_at'
    order = 'DESC' if sort_desc else 'ASC'
    sql = f"""
        SELECT c.*, (SELECT MAX(time) FROM contacts WHERE customer_id = c.id) as last_contact
        FROM customers c
        WHERE {where}
        ORDER BY c.{sort_col} {order}
    """
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def insert_contact(data: dict) -> None:
    conn = get_conn()
    keys = ', '.join(data.keys())
    vals = ', '.join('?' for _ in data)
    conn.execute(f"INSERT INTO contacts ({keys}) VALUES ({vals})", list(data.values()))
    conn.commit()
    conn.close()


def list_contacts(customer_id: str) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM contacts WHERE customer_id = ? ORDER BY time DESC",
        [customer_id],
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def export_all_customers() -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        """SELECT c.*, (SELECT MAX(time) FROM contacts WHERE customer_id = c.id) as last_contact
           FROM customers c ORDER BY c.name"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

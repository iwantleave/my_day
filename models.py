from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Customer:
    id: str = ''
    name: str = ''
    gender: str = ''
    birthday: str = ''
    age: Optional[int] = None
    death_date: str = ''
    company: str = ''
    department: str = ''
    position: str = ''
    phone: str = ''
    wechat: str = ''
    qq: str = ''
    email: str = ''
    address: str = ''
    source: str = ''
    status: str = '潜在客户'
    level: str = 'C'
    product: str = ''
    amount: Optional[float] = None
    deal_date: str = ''
    sales: str = ''
    next_follow: str = ''
    tags: str = ''
    remark: str = ''
    created_at: str = ''
    updated_at: str = ''

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class ContactRecord:
    id: str = ''
    customer_id: str = ''
    time: str = ''
    method: str = ''
    summary: str = ''
    result: str = ''
    next_follow: str = ''

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

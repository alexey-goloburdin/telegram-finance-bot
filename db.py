import os
from typing import Dict, List, Tuple

import sqlite3

conn = sqlite3.connect(os.path.join("db", "finance.db"))
cursor = conn.cursor()


def insert(table: str, column_values: Dict):
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join("?" * len(column_values.keys()))
    cursor.executemany(
        f"INSERT INTO {table} "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    conn.commit()


def fetchall(table: str, columns: List[str]) -> List[Tuple]:
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table}")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


def get_amount(date: str, base: bool):
    if date == "today":
        if base is False:
            cursor.execute("select sum(amount)"
                           "from expense where date(created)=date('now', 'localtime')")
            amount = cursor.fetchone()
            return amount
        else:
            cursor.execute("select sum(amount) "
                           "from expense where date(created)=date('now', 'localtime') "
                           "and category_codename in (select codename "
                           "from category where is_base_expense=true)")
            amount = cursor.fetchone()
            return amount
    else:
        if base is False:
            cursor.execute(f"select sum(amount) "
                           f"from expense where date(created) >= '{date}'")
            amount = cursor.fetchone()
            return amount
        else:
            cursor.execute(f"select sum(amount) "
                           f"from expense where date(created) >= '{date}' "
                           f"and category_codename in (select codename "
                           f"from category where is_base_expense=true)")
            amount = cursor.fetchone()
            return amount


def last():
    cursor.execute(
        "select e.id, e.amount, c.name "
        "from expense e left join category c "
        "on c.codename=e.category_codename "
        "order by created desc limit 10")
    rows = cursor.fetchall()
    return rows


def delete(table: str, row_id: int) -> None:
    row_id = int(row_id)
    cursor.execute(f"delete from {table} where id={row_id}")
    conn.commit()


def get_cursor():
    return cursor


def _init_db():
    """Инициализирует БД"""
    with open("createdb.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def check_db_exists():
    """Проверяет, инициализирована ли БД, если нет — инициализирует"""
    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE type='table' AND name='expense'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()


check_db_exists()

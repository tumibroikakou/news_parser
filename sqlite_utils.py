import sqlite3


def create_db() -> None:
    # TODO дб с таблицей чат_ид и номером новости, вместо словарика Юзерс
    #  иии таблица с последней новостью, распарсеной! без джсона!
    connect = sqlite3.connect("db.sqlite3")
    cursor = connect.cursor()
    cursor.execute("""
           CREATE TABLE IF NOT EXISTS scheduler (
           chat_id INTEGER PRIMARY KEY,
           hour INTEGER,
           minute INTEGER,
           is_group INTEGER
           )
       """)
    connect.commit()
    cursor.close()
    connect.close()


def write_job_to_db(chat_id: int, hour: int, minute: int, is_group: int) -> None:
    connect = sqlite3.connect("db.sqlite3")
    cursor = connect.cursor()
    cursor.execute('SELECT chat_id FROM scheduler WHERE chat_id=?', (chat_id,))
    if not cursor.fetchone():
        cursor.execute('INSERT INTO scheduler (chat_id, hour, minute, is_group) VALUES (?, ?, ?, ?)',
                       (chat_id, hour, minute, 1 if is_group else 0))
    else:
        cursor.execute('UPDATE scheduler SET hour=?, minute=?, is_group=? WHERE chat_id=?',
                       (hour, minute, is_group, chat_id))
    connect.commit()
    cursor.close()
    connect.close()


def get_all_jobs_from_db() -> list:
    connect = sqlite3.connect("db.sqlite3")
    cursor = connect.cursor()
    result = cursor.execute('SELECT chat_id, hour, minute, is_group FROM scheduler').fetchall()
    cursor.close()
    connect.close()
    return result


def remove_job_from_db(chat_id) -> None:
    connect = sqlite3.connect("db.sqlite3")
    cursor = connect.cursor()
    cursor.execute('DELETE FROM scheduler WHERE chat_id=?', (chat_id,))
    connect.commit()
    cursor.close()
    connect.close()

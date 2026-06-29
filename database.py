import sqlite3

DB = "toolbox.db"


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS toolbox(
        box_no TEXT,
        item TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_items(box_no, items):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "DELETE FROM toolbox WHERE box_no=?",
        (box_no,)
    )

    for item in items:
        c.execute(
            "INSERT INTO toolbox VALUES (?,?)",
            (box_no, item)
        )

    conn.commit()
    conn.close()


def get_items(box_no):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT item FROM toolbox WHERE box_no=?",
        (box_no,)
    )

    rows = c.fetchall()

    conn.close()

    return [r[0] for r in rows]


def update_missing(box_no, missing):

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "DELETE FROM toolbox WHERE box_no=?",
        (box_no,)
    )

    for item in missing:
        c.execute(
            "INSERT INTO toolbox VALUES (?,?)",
            (box_no, item)
        )

    conn.commit()
    conn.close()


def get_all_boxes():

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT box_no,item FROM toolbox"
    )

    rows = c.fetchall()

    conn.close()

    return rows


def get_box_count():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT COUNT(DISTINCT box_no) FROM toolbox"
    )
    count = c.fetchone()[0]

    conn.close()

    return count


def get_item_count():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "SELECT COUNT(*) FROM toolbox"
    )
    count = c.fetchone()[0]

    conn.close()

    return count


def delete_box(box_no):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "DELETE FROM toolbox WHERE box_no=?",
        (box_no,)
    )

    conn.commit()
    conn.close()
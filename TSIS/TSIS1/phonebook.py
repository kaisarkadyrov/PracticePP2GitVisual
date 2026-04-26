"""
phonebook.py  –  PhoneBook Extended (TSIS 1)
Builds on the CRUD / CSV / search / pagination foundations from
Practice 7 & 8.  Only NEW features are implemented here.
"""

import csv
import json
import os
from datetime import date, datetime

import psycopg2
import psycopg2.extras

from connect import get_connection


def _conn():
    return get_connection()


def _fmt_date(d):
    return d.isoformat() if d else ""


def _parse_date(s):
    s = (s or "").strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        print(f"  ⚠  Invalid date '{s}' – expected YYYY-MM-DD, skipping.")
        return None


def _print_contacts(rows):
    if not rows:
        print("  (no contacts found)")
        return
    sep = "-" * 80
    print(sep)
    for r in rows:
        phones = r.get("phones", [])
        phone_str = ", ".join(
            f"{p['phone']} [{p['type']}]" for p in phones
        ) if phones else "(no phones)"
        print(
            f"  [{r['id']:>4}]  {r['name']}\n"
            f"         Email:    {r.get('email') or '—'}\n"
            f"         Birthday: {_fmt_date(r.get('birthday')) or '—'}\n"
            f"         Group:    {r.get('group_name') or '—'}\n"
            f"         Phones:   {phone_str}"
        )
    print(sep)


def _fetch_contacts_with_phones(conn, contact_ids):
    if not contact_ids:
        return []
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            SELECT c.id, c.name, c.email, c.birthday,
                   g.name AS group_name
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            WHERE c.id = ANY(%s)
            ORDER BY c.name
            """,
            (list(contact_ids),),
        )
        contacts = {r["id"]: dict(r) for r in cur.fetchall()}

        cur.execute(
            "SELECT contact_id, phone, type FROM phones WHERE contact_id = ANY(%s)",
            (list(contact_ids),),
        )
        for row in cur.fetchall():
            contacts[row["contact_id"]].setdefault("phones", []).append(
                {"phone": row["phone"], "type": row["type"]}
            )

    for c in contacts.values():
        c.setdefault("phones", [])
    return list(contacts.values())


# ── 3.1 Schema ────────────────────────────────────────────────

def init_schema():
    base = os.path.dirname(os.path.abspath(__file__))
    with _conn() as conn:
        with conn.cursor() as cur:
            for fname in ("schema.sql", "procedures.sql"):
                fpath = os.path.join(base, fname)
                with open(fpath, encoding="utf-8") as f:
                    sql = f.read()
                cur.execute(sql)
        conn.commit()
    print("✅  Schema and procedures applied.")


# ── 3.2 Search & Filter ───────────────────────────────────────

def filter_by_group():
    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT id, name FROM groups ORDER BY name")
            groups = cur.fetchall()

    if not groups:
        print("No groups found.")
        return

    print("\nAvailable groups:")
    for g in groups:
        print(f"  {g['id']}. {g['name']}")
    choice = input("Enter group number (or name): ").strip()

    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if choice.isdigit():
                cur.execute(
                    "SELECT c.id FROM contacts c JOIN groups g ON g.id = c.group_id WHERE g.id = %s",
                    (int(choice),),
                )
            else:
                cur.execute(
                    "SELECT c.id FROM contacts c JOIN groups g ON g.id = c.group_id WHERE LOWER(g.name) = LOWER(%s)",
                    (choice,),
                )
            ids = [r["id"] for r in cur.fetchall()]
        results = _fetch_contacts_with_phones(conn, ids)
    _print_contacts(results)


def search_by_email():
    query = input("Email search term: ").strip()
    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id FROM contacts WHERE LOWER(email) LIKE %s",
                (f"%{query.lower()}%",),
            )
            ids = [r["id"] for r in cur.fetchall()]
        results = _fetch_contacts_with_phones(conn, ids)
    _print_contacts(results)


def sort_and_list():
    print("\nSort by:  1) Name   2) Birthday   3) Date added")
    choice = input("Choice [1]: ").strip() or "1"
    order_map = {
        "1": "c.name",
        "2": "c.birthday NULLS LAST",
        "3": "c.created_at",
    }
    order = order_map.get(choice, "c.name")

    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SELECT id FROM contacts c ORDER BY {order}")
            ids = [r["id"] for r in cur.fetchall()]
        results = _fetch_contacts_with_phones(conn, ids)
    _print_contacts(results)


def paginated_browse():
    page_size = 5
    page = 0

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM contacts")
            total = cur.fetchone()[0]

    total_pages = max(1, (total + page_size - 1) // page_size)
    print(f"\nTotal contacts: {total}  |  Page size: {page_size}")

    while True:
        offset = page * page_size
        with _conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM get_contacts_paginated(%s, %s)",
                    (page_size, offset),
                )
                rows = cur.fetchall()

        print(f"\n── Page {page + 1} / {total_pages} ──")
        if rows:
            ids = [r["id"] for r in rows]
            with _conn() as conn:
                results = _fetch_contacts_with_phones(conn, ids)
            _print_contacts(results)
        else:
            print("  (empty page)")

        cmd = input("[N]ext  [P]rev  [Q]uit: ").strip().lower()
        if cmd == "n":
            if page + 1 < total_pages:
                page += 1
            else:
                print("  Already on the last page.")
        elif cmd == "p":
            if page > 0:
                page -= 1
            else:
                print("  Already on the first page.")
        elif cmd == "q":
            break


# ── 3.3 Import / Export ───────────────────────────────────────

def export_to_json(filepath="contacts_export.json"):
    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT id FROM contacts c ORDER BY name")
            ids = [r["id"] for r in cur.fetchall()]
        contacts = _fetch_contacts_with_phones(conn, ids)

    for c in contacts:
        if isinstance(c.get("birthday"), date):
            c["birthday"] = c["birthday"].isoformat()

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)

    print(f"✅  Exported {len(contacts)} contacts to '{filepath}'.")


def _upsert_contact_from_dict(conn, data, on_duplicate="ask"):
    name = (data.get("name") or "").strip()
    if not name:
        print("  ⚠  Skipping record with no name.")
        return

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "SELECT id FROM contacts WHERE LOWER(name) = LOWER(%s)",
            (name,),
        )
        existing = cur.fetchone()

    if existing:
        action = on_duplicate
        if action == "ask":
            print(f"  ⚠  Duplicate: '{name}'.  [S]kip / [O]verwrite? ", end="")
            action = "skip" if input().strip().lower() != "o" else "overwrite"
        if action == "skip":
            print(f"     → Skipped.")
            return
        with conn.cursor() as cur:
            cur.execute("DELETE FROM contacts WHERE id = %s", (existing["id"],))

    group_id = None
    group_name = (data.get("group_name") or data.get("group") or "").strip()
    if group_name:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
                (group_name,),
            )
            cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
            row = cur.fetchone()
            if row:
                group_id = row[0]

    birthday = _parse_date(data.get("birthday"))
    email = (data.get("email") or "").strip() or None

    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s, %s, %s, %s) RETURNING id",
            (name, email, birthday, group_id),
        )
        contact_id = cur.fetchone()[0]

    phones = data.get("phones", [])
    if not phones and data.get("phone"):
        phones = [{"phone": data["phone"], "type": data.get("phone_type", "mobile")}]

    with conn.cursor() as cur:
        for p in phones:
            ph_type = (p.get("type") or "mobile").lower()
            if ph_type not in ("home", "work", "mobile"):
                ph_type = "mobile"
            cur.execute(
                "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                (contact_id, p["phone"], ph_type),
            )

    conn.commit()
    print(f"  ✅  Saved: {name}")


def import_from_json(filepath=None):
    if filepath is None:
        filepath = input("JSON file path [contacts_export.json]: ").strip() or "contacts_export.json"
    if not os.path.exists(filepath):
        print(f"  ✗  File not found: {filepath}")
        return

    with open(filepath, encoding="utf-8") as f:
        records = json.load(f)

    print(f"Found {len(records)} records in '{filepath}'.")
    mode = input("On duplicate — [A]sk each / [S]kip all / [O]verwrite all [A]: ").strip().lower()
    on_dup = {"s": "skip", "o": "overwrite"}.get(mode, "ask")

    with _conn() as conn:
        for rec in records:
            _upsert_contact_from_dict(conn, rec, on_duplicate=on_dup)
    print("✅  Import complete.")


def import_from_csv(filepath=None):
    """Expected CSV columns: name, email, birthday, group, phone, phone_type"""
    if filepath is None:
        filepath = input("CSV file path [contacts.csv]: ").strip() or "contacts.csv"
    if not os.path.exists(filepath):
        print(f"  ✗  File not found: {filepath}")
        return

    mode = input("On duplicate — [A]sk each / [S]kip all / [O]verwrite all [A]: ").strip().lower()
    on_dup = {"s": "skip", "o": "overwrite"}.get(mode, "ask")

    imported = 0
    with _conn() as conn, open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            _upsert_contact_from_dict(conn, row, on_duplicate=on_dup)
            imported += 1
    print(f"✅  CSV import complete: processed {imported} rows.")


# ── 3.4 Stored-procedure wrappers ────────────────────────────

def call_add_phone():
    name  = input("Contact name: ").strip()
    phone = input("Phone number: ").strip()
    ptype = input("Type (home/work/mobile) [mobile]: ").strip().lower() or "mobile"
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
        conn.commit()
    print("✅  Phone added.")


def call_move_to_group():
    name  = input("Contact name: ").strip()
    group = input("Target group name: ").strip()
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL move_to_group(%s, %s)", (name, group))
        conn.commit()
    print("✅  Contact moved.")


def call_search_contacts():
    query = input("Search query: ").strip()
    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            rows = cur.fetchall()
        ids = [r["id"] for r in rows]
        results = _fetch_contacts_with_phones(conn, ids)
    _print_contacts(results)


# ── Main menu ─────────────────────────────────────────────────

MENU = """
╔══════════════════════════════════════════════════╗
║         PhoneBook  –  TSIS 1 Extended Menu       ║
╠══════════════════════════════════════════════════╣
║  SCHEMA                                          ║
║  0.  Apply schema & procedures                   ║
╠══════════════════════════════════════════════════╣
║  SEARCH & FILTER                                 ║
║  1.  Filter contacts by group                    ║
║  2.  Search by email                             ║
║  3.  List all contacts (sorted)                  ║
║  4.  Browse contacts (paginated)                 ║
╠══════════════════════════════════════════════════╣
║  IMPORT / EXPORT                                 ║
║  5.  Export to JSON                              ║
║  6.  Import from JSON                            ║
║  7.  Import from CSV (extended)                  ║
╠══════════════════════════════════════════════════╣
║  STORED PROCEDURES                               ║
║  8.  Add phone number to contact                 ║
║  9.  Move contact to group                       ║
║  10. Search contacts (all fields + phones)       ║
╠══════════════════════════════════════════════════╣
║  Q.  Quit                                        ║
╚══════════════════════════════════════════════════╝
"""

HANDLERS = {
    "0":  init_schema,
    "1":  filter_by_group,
    "2":  search_by_email,
    "3":  sort_and_list,
    "4":  paginated_browse,
    "5":  export_to_json,
    "6":  import_from_json,
    "7":  import_from_csv,
    "8":  call_add_phone,
    "9":  call_move_to_group,
    "10": call_search_contacts,
}


def main():
    while True:
        print(MENU)
        choice = input("Select option: ").strip().lower()
        if choice == "q":
            print("Goodbye!")
            break
        handler = HANDLERS.get(choice)
        if handler:
            try:
                handler()
            except psycopg2.Error as e:
                print(f"  ✗  Database error: {e.pgerror or e}")
            except KeyboardInterrupt:
                print()
        else:
            print("  Invalid choice, please try again.")


if __name__ == "__main__":
    main()
import csv
from connect import connect
from config import load_config

def create_table():
    config = load_config()
    conn = connect(config)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        phone VARCHAR(20) UNIQUE NOT NULL
    )
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("Table created")


def insert_from_csv():
    config = load_config()
    conn = connect(config)
    cur = conn.cursor()

    with open("contacts.csv", newline='') as f:
        reader = csv.reader(f)
        next(reader)

        for row in reader:
            cur.execute(
                "INSERT INTO contacts (name, phone) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (row[0], row[1])
            )

    conn.commit()
    cur.close()
    conn.close()
    print("CSV data inserted")


def insert_from_console():
    name = input("Enter name: ")
    phone = input("Enter phone: ")

    config = load_config()
    conn = connect(config)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
        (name, phone)
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Contact added")


def search_contacts():
    keyword = input("Search: ")

    config = load_config()
    conn = connect(config)
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM contacts WHERE name ILIKE %s OR phone LIKE %s",
        ('%' + keyword + '%', '%' + keyword + '%')
    )

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def update_contact():
    name = input("Enter name to update: ")
    new_name = input("New name: ")
    new_phone = input("New phone: ")

    config = load_config()
    conn = connect(config)
    cur = conn.cursor()

    if new_name:
        cur.execute(
            "UPDATE contacts SET name=%s WHERE name=%s",
            (new_name, name)
        )

    if new_phone:
        cur.execute(
            "UPDATE contacts SET phone=%s WHERE name=%s",
            (new_phone, name)
        )

    conn.commit()
    cur.close()
    conn.close()
    print("Updated")


def delete_contact():
    value = input("Enter name or phone to delete: ")

    config = load_config()
    conn = connect(config)
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM contacts WHERE name=%s OR phone=%s",
        (value, value)
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Deleted")


def menu():
    while True:
        print("""
1. Create table
2. Insert from CSV
3. Insert from console
4. Search
5. Update
6. Delete
7. Exit
""")

        choice = input("Choose: ")

        if choice == "1":
            create_table()
        elif choice == "2":
            insert_from_csv()
        elif choice == "3":
            insert_from_console()
        elif choice == "4":
            search_contacts()
        elif choice == "5":
            update_contact()
        elif choice == "6":
            delete_contact()
        elif choice == "7":
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    menu()
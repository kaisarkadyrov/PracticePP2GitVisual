from connect import connect
from config import load_config

config = load_config()
conn = connect(config)
cur = conn.cursor()
cur.execute("SELECT current_database(), current_schema()")
print(cur.fetchall())  # покажет имя базы и схему, с которой соединение
cur.close()
conn.close()

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

def search_contacts():
    keyword = input("Search: ")

    config = load_config()        # Загружаем конфиг для подключения
    conn = connect(config)        # Подключаемся к базе
    cur = conn.cursor()

    # Выполняем поиск по имени или телефону
    cur.execute(
        "SELECT * FROM contacts WHERE name ILIKE %s OR phone ILIKE %s",
        ('%' + keyword + '%', '%' + keyword + '%')  # добавляем % для шаблона
    )

    rows = cur.fetchall()

    if rows:
        print("\nResults:")
        for row in rows:
            print(row)
    else:
        print("No contacts found.")

    cur.close()
    conn.close()

def insert_contact():
    name = input("Name: ")
    phone = input("Phone: ")
    config = load_config()
    conn = connect(config)
    cur = conn.cursor()
    cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
    conn.commit()
    cur.close()
    conn.close()
    print("Contact inserted/updated")

def bulk_insert():
    n = int(input("How many contacts to insert? "))
    contacts = []

    for _ in range(n):
        name = input("Name: ")
        phone = input("Phone: ")
        contacts.append((name, phone))

    config = load_config()
    conn = connect(config)
    cur = conn.cursor()

    for name, phone in contacts:
        cur.execute(
            "INSERT INTO contacts(name, phone) VALUES (%s, %s)",
            (name, phone)
        )

    conn.commit()
    cur.close()
    conn.close()
    print(f"{n} contacts added successfully.")

def delete_contact():
    value = input("Name or phone to delete: ")

    config = load_config()
    conn = connect(config)
    cur = conn.cursor()

    # удаляем по имени или телефону
    cur.execute(
        "DELETE FROM contacts WHERE name = %s OR phone = %s",
        (value, value)
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Contact deleted (if existed).")

def show_paginated():
    limit = int(input("Number of rows per page: "))
    offset = int(input("Offset: "))
    config = load_config()
    conn = connect(config)
    cur = conn.cursor()
    cur.execute("SELECT * FROM get_contacts_paginated(%s,%s)", (limit, offset))
    rows = cur.fetchall()
    if rows:
        for row in rows:
            print(row)
    else:
        print("No contacts found")
    cur.close()
    conn.close()

def menu():
    while True:
        print("""
1. Create table
2. Search contacts
3. Insert/Update contact
4. Bulk insert contacts
5. Delete contact
6. Show paginated contacts
7. Exit
""")
        choice = input("Choose: ")
        if choice == "1":
            create_table()
        elif choice == "2":
            search_contacts()
        elif choice == "3":
            insert_contact()
        elif choice == "4":
            bulk_insert()
        elif choice == "5":
            delete_contact()
        elif choice == "6":
            show_paginated()
        elif choice == "7":
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    menu()
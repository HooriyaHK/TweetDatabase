# main.py

import sqlite3
from auth import register_user, login_user  # import functions from auth.py

# function to connect to db
def connect_db():
    connection = sqlite3.connect("prj-sample.db")
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")  # enable foreign keys
    return connection, cursor

def login_screen():
    print("\n=== Welcome to Twitter ===")
    print("1. Login")
    print("2. Register")
    print("3. Exit")
    option = input("\nChoose an option: ")
    return option

# main
if __name__ == "__main__":
    connection, cursor = connect_db() # db connection

    while True:
        option = login_screen()
        if option == '1':
            user_id = login_user(cursor)  
            if user_id:
                print(f"User {user_id} is now logged in.")
        elif option == '2':
            register_user(cursor, connection)  
        elif option == '3':
            print("\nExiting program...")
            break
        else:
            print("\nInvalid option. Please try again.")

    connection.close()

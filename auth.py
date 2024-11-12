# auth.py -- authentication functions (ex. login, signup)

import sqlite3
from getpass import getpass  # hides password input for security

# user registration function
def register_user(cursor, connection):
    print("\n=== Register ===")
    name = input("Enter Name: ")
    email = input("Enter Email: ")
    phone = input("Enter Phone: ")
    pwd = getpass("Enter Password: ")

    try:
        # Insert the new user, letting SQLite automatically generate the user ID
        cursor.execute("INSERT INTO users (name, email, phone, pwd) VALUES (?, ?, ?, ?)", (name, email, phone, pwd))
        connection.commit()  # SAVE CHANGES ??
        
        # Retrieve the auto-generated user ID
        new_usr = cursor.lastrowid
        print("\nsign-up Completed! Your user ID is:", new_usr)
    except sqlite3.IntegrityError:
        print("\nError: email or phone already registered.")
    except Exception as e:
        print("\nerror occurred during registration:", e)

# user login
def login_user(cursor):
    print("=== Login ===")
    usr = input("Enter User ID: ")
    pwd = getpass("Enter Password: ")

    try:
        cursor.execute("SELECT * FROM users WHERE usr = ? AND pwd = ?", (usr, pwd))
        user = cursor.fetchone()
        if user:
            print(f"\nWelcome, {user[1]}!")  
            return usr  
        else:
            print("\nInvalid User ID or Password.")
            return None
    except Exception as e:
        print("\nAn error occurred during login:", e)
        return None

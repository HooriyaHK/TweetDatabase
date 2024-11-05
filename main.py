import sqlite3

def login_screen():
    print("=== Welcome to Twitter ===")

    print("1. Login")
    print("2. Register")
    print("3. Exit")
    option = input("\nChoose an option: ")
    return option

if __name__ == "__main__":
    while True:
        option = login_screen()
        
        if option == '1':
            # login function
            pass
        elif option == '2':
            # sign up function
            pass
        elif option == '3':
            print("\nExiting program...")
            break
        else:
            print("\nInvalid option. Please try again.")


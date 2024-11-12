import sqlite3


def login_screen():
    print("=== Welcome to Twitter ===")

    print("1. Login")
    print("2. Register")
    print("3. Exit")
    option = input("\nChoose an option: ")
    return option

# This is the function tp sign up
def sign_up():
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    phone = input("Enter your phone: ")
    pwd = input("Enter your password: ")
    if (1):
        print("Congratulation! You successfully sign in! \n")
        print("Here is your user id: " + "1")
    else:
        print("Your use id is already in the datebase")


# This is the function to login
def login():
    usr = input("Enter User ID: ")
    pwd = input("Enter Password: ")

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
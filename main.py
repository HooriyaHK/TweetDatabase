# main.py

import sqlite3
from getpass import getpass  # hides password input for security
import re  # for hashtag extraction

# Function to connect to database
def connect_db():
    connection = sqlite3.connect("prj-sample.db")
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
    return connection, cursor

# user registration function
def register_user(cursor, connection):
    print("\n=== Register ===")
    name = input("Enter Name: ")
    email = input("Enter Email: ")
    phone = input("Enter Phone: ")
    pwd = getpass("Enter Password: ")

    try:
        # manually generate next available user ID
        cursor.execute("SELECT MAX(usr) FROM users")
        max_usr = cursor.fetchone()[0]
        new_usr = max_usr + 1 if max_usr is not None else 1  # start with 1 if no users exist

        # Insert the new user with the manually assigned user ID
        cursor.execute("INSERT INTO users (usr, name, email, phone, pwd) VALUES (?, ?, ?, ?, ?)",
                       (new_usr, name, email, phone, pwd))
        connection.commit()  # Save changes
        
        print("\nSign-up Completed! Your user ID is:", new_usr) #success message
        print("You can now log in!")

    except sqlite3.IntegrityError:
        print("\nError: Email or phone already registered.")
    except Exception as e:
        print("\nAn error occurred during registration:", e)

# user login
def login_user(cursor):
    print("=== Login ===")
    usr = input("Enter User ID: ")
    pwd = getpass("Enter Password: ")

    try:
        #query 1 
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
    #show twitter feed of the 5 tweets from followers 

#compose tweet 
def compose_tweet(cursor, connection, user_id):
    print("\n=== Compose Tweet ===")
    tweet_text = input("Enter your tweet (use # to tag hashtags): ")

    hashtags = re.findall(r'#\w+', tweet_text)
    if hashtags:
        hashtags = [tag[1:].lower() for tag in hashtags]  # Remove '#' and lowercase

    reply_to_tid = input("If this tweet is a reply to another tweet, enter its tweet ID (or press Enter to skip): ")
    reply_to_tid = int(reply_to_tid) if reply_to_tid else None

    try:
        # Manually setting the tid if needed (alternatively, rely on auto-increment)
        tweet_tid = None  # Set to None if auto-generated, or manually set the tid
        if tweet_tid is None:
            cursor.execute("INSERT INTO tweets (writer_id, text, tdate, ttime, replyto_tid) VALUES (?, ?, DATE('now'), TIME('now'), ?)", 
                           (user_id, tweet_text, reply_to_tid))
        else:
            cursor.execute("INSERT INTO tweets (tid, writer_id, text, tdate, ttime, replyto_tid) VALUES (?, ?, ?, DATE('now'), TIME('now'), ?)", 
                           (tweet_tid, user_id, tweet_text, reply_to_tid))
        connection.commit()

        tweet_id = cursor.lastrowid if tweet_tid is None else tweet_tid
        print(f"Tweet posted with ID: {tweet_id}")

        # Insert hashtags into the hashtag_mentions table
        for tag in set(hashtags):  
            cursor.execute("INSERT INTO hashtag_mentions (tid, term) VALUES (?, ?)", (tweet_id, tag))
        connection.commit()
        print("Hashtags added to the database.")

    except sqlite3.Error as e:
        print(f"An error occurred while posting the tweet: {e}")


# List followers
#query 7 
def list_followers(cursor, user_id):
    print("\n=== Followers ===")
    page = 1
    while True:
        #tested query needed 
        offset = (page - 1) * 5
        cursor.execute("SELECT flwer, name FROM follows JOIN users ON follows.flwer = users.usr WHERE flwee = ? LIMIT 5 OFFSET ?", 
                       (user_id, offset))
        followers = cursor.fetchall()

        if not followers:
            print("No more followers.")
            break

        for follower in followers:
            print(f"Follower ID: {follower[0]}, Name: {follower[1]}")

        choice = input("Select a follower ID to view details, or type 'next' for more, 'back' for previous page, or 'exit': ")
        
        if choice.isdigit():
            follower_id = int(choice)
            show_follower_details(cursor, follower_id)
        elif choice.lower() == 'next':
            page += 1
        elif choice.lower() == 'back' and page > 1:
            page -= 1
        elif choice.lower() == 'exit':
            break

# Logout function
def logout():
    print("\nLogging out... Returning to login page.\n")

# Main login screen
def login_screen():
    print("\n=== Welcome to Twitter ===")
    print("1. Login")
    print("2. Register")
    print("3. Exit")
    option = input("\nChoose an option: ")
    return option

# Logged-in user menu
def user_menu(cursor, connection, user_id):
    while True:
        print("\n=== User Menu ===")
        print("1. Compose Tweet")
        print("2. List Followers")
        print("3. Logout")
        option = input("\nChoose an option: ")

        if option == '1':
            compose_tweet(cursor, connection, user_id)
        elif option == '2':
            list_followers(cursor, user_id)
        elif option == '3':
            logout()
            break  # Return to login screen
        else:
            print("\nInvalid option. Please try again.")

# Main program
if __name__ == "__main__":
    connection, cursor = connect_db()  # Establish database connection

    while True:
        option = login_screen()
        if option == '1':
            user_id = login_user(cursor)
            if user_id:
                print(f"User {user_id} is now logged in.")
                user_menu(cursor, connection, user_id)  # Go to user menu
        elif option == '2':
            register_user(cursor, connection)
        elif option == '3':
            print("\nExiting program...")
            break
        else:
            print("\nInvalid option. Please try again.")

    connection.close()  # Close database connection

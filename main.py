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

# User registration function
def register_user(cursor, connection):
    print("\n=== Register ===")
    name = input("Enter Name: ")
    email = input("Enter Email: ")
    phone = input("Enter Phone: ")
    pwd = getpass("Enter Password: ")

    try:
        #query 2 
        cursor.execute("INSERT INTO users (name, email, phone, pwd) VALUES (?, ?, ?, ?)", (name, email, phone, pwd))
        connection.commit()
        new_usr = cursor.lastrowid
        print("\nSign-up Completed! Your user ID is:", new_usr)
        
        #query 1 
        cursor.execute("SELECT * FROM users WHERE usr = ?", (new_usr,))
        user = cursor.fetchone()
        if user:
            print("\nNewly added user:", user)
        else:
            print("\nUser not found in database after insertion.")
    except sqlite3.IntegrityError:
        print("\nError: Email or phone already registered.")
    except Exception as e:
        print("\nAn error occurred during registration:", e)

# User login
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

# Compose a tweet
def compose_tweet(cursor, connection, user_id):
    print("\n=== Compose Tweet ===")
    tweet_text = input("Enter your tweet (use # to tag hashtags): ")

    hashtags = re.findall(r'#\w+', tweet_text)
    if hashtags:
        hashtags = [tag[1:].lower() for tag in hashtags]  # Remove '#' and lowercase

    try:
        #query 6
        cursor.execute("INSERT INTO tweets (writer_id, text, tdate, ttime) VALUES (?, ?, DATE('now'), TIME('now'))", 
                       (user_id, tweet_text))
        connection.commit()
        tweet_id = cursor.lastrowid
        print(f"Tweet posted with ID: {tweet_id}")

        for tag in set(hashtags):  
            cursor.execute("INSERT INTO hashtag_mentions (tid, term) VALUES (?, ?)", (tweet_id, tag))
        connection.commit()
        print("Hashtags added to the database.")
    except sqlite3.Error as e:
        print(f"An error occurred while posting the tweet: {e}")

# List followers
def list_followers(cursor, user_id):
    print("\n=== Followers ===")
    page = 1
    while True:
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

# Show follower details
def show_follower_details(cursor, follower_id):
    print(f"\n=== Details for Follower ID {follower_id} ===")
    cursor.execute("""
        SELECT 
            (SELECT COUNT(*) FROM tweets WHERE writer_id = ?) AS num_tweets,
            (SELECT COUNT(*) FROM follows WHERE flwer = ?) AS num_following,
            (SELECT COUNT(*) FROM follows WHERE flwee = ?) AS num_followers
    """, (follower_id, follower_id, follower_id))
    details = cursor.fetchone()
    
    if details:
        print(f"Tweets: {details[0]}, Following: {details[1]}, Followers: {details[2]}")
    else:
        print("Follower not found or has no tweets.")

    cursor.execute("SELECT tid, text, tdate, ttime FROM tweets WHERE writer_id = ? ORDER BY tdate DESC, ttime DESC LIMIT 3", 
                   (follower_id,))
    recent_tweets = cursor.fetchall()

    if recent_tweets:
        print("\nRecent Tweets:")
        for tweet in recent_tweets:
            print(f"Tweet ID: {tweet[0]}, Text: {tweet[1]}, Date: {tweet[2]}, Time: {tweet[3]}")
    else:
        print("No recent tweets.")

    follow_choice = input("Type 'follow' to follow this user, or 'more' to see more tweets, or press Enter to return: ")
    if follow_choice.lower() == 'follow':
        try:
            cursor.execute("INSERT INTO follows (flwer, flwee) VALUES (?, ?)", (follower_id, follower_id))
            print("You are now following this user.")
        except sqlite3.IntegrityError:
            print("You are already following this user.")
    elif follow_choice.lower() == 'more':
        cursor.execute("SELECT tid, text, tdate, ttime FROM tweets WHERE writer_id = ? ORDER BY tdate DESC, ttime DESC", 
                       (follower_id,))
        all_tweets = cursor.fetchall()
        for tweet in all_tweets[3:]:  # Skip the first 3 already shown
            print(f"Tweet ID: {tweet[0]}, Text: {tweet[1]}, Date: {tweet[2]}, Time: {tweet[3]}")
            if input("Press Enter to continue or type 'exit' to stop viewing tweets: ") == 'exit':
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

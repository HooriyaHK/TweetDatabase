import sqlite3
from getpass import getpass  # hides password input for security
import re  # for hashtag extraction

# Function to connect to database
def connect_db(db_name):
    #connection = sqlite3.connect("prj-sample.db")
    if not db_name.endswith(".db"):
        print("\nError: Please provide a valid .db file.")
        return None, None

    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
    return connection, cursor

# function to validate email & phone number 
def is_valid_input(input_value, input_type):
    if input_type == 'email':
        # Basic email validation pattern
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,3}$' #
    elif input_type == 'phone':
        # 10-digit phone number validation pattern
        pattern = r'^\d{10}$'
    else:
        raise ValueError("Invalid input type. Use 'email' or 'phone'.")
    
    return re.match(pattern, input_value) is not None


# User registration function
def register_user(cursor, connection):
    print("\n=== Register ===")
    name = input("Enter Name: ")

    # loop for email validation
    while True:
        email = input("Enter Email: ")
        if is_valid_input(email, 'email'):
            break
        else:
            print("Invalid email format. Please enter a valid email with '@' and a domain (e.g., example@domain.com).")

    # loop for phone num validation
    while True:
        phone = input("Enter Phone (10 digits): ")
        if is_valid_input(phone, 'phone'):
            break
        else:
            print("Invalid phone number. Please enter a 10-digit phone number.")

    # Password entry and confirmation loop
    while True:
        pwd = getpass("Enter Password: ")
        pwd_confirm = getpass("Retype Password: ")
        if pwd == pwd_confirm:
            break
        else:
            print("Passwords do not match. Please try again.")

    try:
        # Generate next available user ID
        cursor.execute("SELECT MAX(usr) FROM users")
        max_usr = cursor.fetchone()[0]
        new_usr = max_usr + 1 if max_usr is not None else 1  # Start with 1 if no users exist

        # Insert new user
        cursor.execute("INSERT INTO users (usr, name, email, phone, pwd) VALUES (?, ?, ?, ?, ?)",
                       (new_usr, name, email, phone, pwd))
        connection.commit()
        print("\nSign-up Completed! Your user ID is:", new_usr)

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

# Display tweets and retweets of followed users
def display_feed(cursor, user_id):
    try:
        # Fetch tweets
        cursor.execute("""
            SELECT T.tid, T.writer_id, T.text, T.tdate, T.ttime
            FROM tweets T
            JOIN follows F ON T.writer_id = F.flwee
            WHERE F.flwer = ?
            ORDER BY T.tdate DESC, T.ttime DESC
            LIMIT 5 OFFSET 0;
        """, (user_id,))
        tweets = cursor.fetchall()

        # Fetch retweets
        cursor.execute("""
            SELECT RT.tid, RT.retweeter_id, RT.writer_id, RT.spam, RT.rdate
            FROM retweets RT, follows F
            WHERE RT.retweeter_id = F.flwer AND F.flwee = ?
            LIMIT 5 OFFSET 0;
        """, (user_id,))
        retweets = cursor.fetchall()

        print("\n--- Feed ---")
        print("\nTweets:")
        for tweet in tweets:
            print(tweet)

        print("\nRetweets:")
        for retweet in retweets:
            print(retweet)

    except sqlite3.Error as e:
        print("An error occurred:", e)

# Compose tweet
def compose_tweet(cursor, connection, user_id):
    print("\n=== Compose Tweet ===")
    tweet_text = input("Enter your tweet (use # to tag hashtags): ")
    hashtags = re.findall(r'#\w+', tweet_text)

    reply_to_tid = input("If this is a reply, enter its tweet ID (or press Enter to skip): ")
    reply_to_tid = int(reply_to_tid) if reply_to_tid else None

    try:
        cursor.execute("""
            INSERT INTO tweets (writer_id, text, tdate, ttime, replyto_tid) 
            VALUES (?, ?, DATE('now'), TIME('now'), ?)
        """, (user_id, tweet_text, reply_to_tid))
        connection.commit()
        tweet_id = cursor.lastrowid
        print(f"Tweet posted with ID: {tweet_id}")

        # Normalize and insert hashtags
        for tag in set([tag[1:].lower() for tag in hashtags]):
            cursor.execute("INSERT INTO hashtag_mentions (tid, term) VALUES (?, ?)", (tweet_id, tag))
        connection.commit()

    except sqlite3.Error as e:
        print(f"An error occurred while posting the tweet: {e}")

# Search tweets by keyword
def search_tweets(cursor, keyword):
    try:
        cursor.execute("""
            SELECT tid, writer_id, text, tdate, ttime 
            FROM tweets 
            WHERE text LIKE '%' || ? || '%' 
               OR tid IN (SELECT tid FROM hashtag_mentions WHERE term = ?)
            ORDER BY tdate DESC
            LIMIT 5 OFFSET 0;
        """, (keyword, keyword))
        results = cursor.fetchall()
        
        print("\n--- Tweet Search Results ---")
        for tweet in results:
            print(tweet)

    except sqlite3.Error as e:
        print("An error occurred during tweet search:", e)

# Search users by keyword
def search_users(cursor, keyword):
    try:
        cursor.execute("""
            SELECT usr, name, email, phone
            FROM users
            WHERE name LIKE '%' || ? || '%' 
            ORDER BY LENGTH(name) ASC
            LIMIT 5 OFFSET 0;
        """, (keyword,))
        results = cursor.fetchall()
        
        # Display user ID and name
        print("\n--- User Search Results ---")
        if results:
            for user in results:
                print(f"User ID: {user[0]}, Name: {user[1]}")
        else:
            print("No users found matching the given keyword.")
    except sqlite3.Error as e:
        print("An error occurred during user search:", e)

# List followers
def list_followers(cursor, user_id):
    try:
        cursor.execute("""
            SELECT flwer, name 
            FROM follows 
            JOIN users ON follows.flwer = users.usr 
            WHERE flwee = ?
            LIMIT 5 OFFSET 0;
        """, (user_id,))
        followers = cursor.fetchall()
        
        print("\n--- Followers ---")
        for follower in followers:
            print(follower)

    except sqlite3.Error as e:
        print("An error occurred while listing followers:", e)

# Follow a user
def follow_user(cursor, connection, flwer, flwee):
    try:
        cursor.execute("""
            INSERT INTO follows(flwer, flwee, start_date)
            VALUES(?, ?, DATE('now'));
        """, (flwer, flwee))
        connection.commit()
        print(f"\nYou are now following User {flwee}.")

    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: follows.flwer, follows.flwee" in str(e):
            print("\nYou are already following this user.")
        else:
            print("\nAn error occurred while following the user:", e)
# Unfollow a user
def unfollow_user(cursor, connection, flwer, flwee):
    try:
        cursor.execute("""
            DELETE FROM follows 
            WHERE flwer = ? AND flwee = ?;
        """, (flwer, flwee))
        connection.commit()
        print(f"\nYou have unfollowed User {flwee}.")
    except sqlite3.Error as e:
        print("An error occurred while unfollowing the user:", e)

# main program flow
def main():
    db_name = input("Please enter the file name: ")
    connection, cursor = connect_db(db_name)

    # exit if connection is None bc of invalid file
    if connection is None:
        print("Exiting program due to invalid database file.\n")
        return
    
    while True:
        print("\n--- Menu ---")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("\nChoose an option: ")
        
        if choice == '1':
            register_user(cursor, connection)
        
        elif choice == '2':
            user_id = login_user(cursor)
            if user_id:
                while True:
                    print("\n--- User Menu ---")
                    print("1. View Feed")
                    print("2. Compose Tweet")
                    print("3. Search Tweets")
                    print("4. Search Users")
                    print("5. List Followers")
                    print("6. Follow a User")
                    print("7. Unfollow a User")
                    print("8. Logout")
                    option = input("\nChoose an option: ")
                    
                    if option == '1':
                        display_feed(cursor, user_id)
                    elif option == '2':
                        compose_tweet(cursor, connection, user_id)
                    elif option == '3':
                        keyword = input("Enter keyword to search tweets: ")
                        search_tweets(cursor, keyword)
                    elif option == '4':
                        keyword = input("Enter keyword to search users: ")
                        search_users(cursor, keyword)
                    elif option == '5':
                        list_followers(cursor, user_id)
                    elif option == '6':
                        flwee = input("Enter the user ID to follow: ")
                        follow_user(cursor, connection, user_id, flwee)
                    elif option == '7':
                        flwee = input("Enter the user ID to unfollow: ")
                        unfollow_user(cursor, connection, user_id, flwee)
                    elif option == '8':
                        print("\nLogged out.")
                        break
                    else:
                        print("Invalid option. Try again.")
        
        elif choice == '3':
            print("\nGoodbye!\n")
            break
        
        else:
            print("Invalid option. Try again.")
    
    connection.close()

# run the program
if __name__ == "__main__":
    main()

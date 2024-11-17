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
            SELECT T.tid, 'Tweet' AS type, T.tdate AS date, T.ttime AS time, T.text AS text
            FROM tweets T
            JOIN follows F ON T.writer_id = F.flwee
            WHERE F.flwer = ?
            ORDER BY T.tdate DESC, T.ttime DESC
            LIMIT 5 OFFSET 0;
        """, (user_id,))
        tweets = cursor.fetchall()
        # Fetch retweets
        cursor.execute("""
            SELECT RT.tid AS retweet_id, 'Retweet' AS type, RT.rdate AS date, T.ttime AS time, T.text AS text
            FROM retweets RT
            JOIN tweets T ON RT.tid = T.tid
            WHERE RT.retweeter_id = ?
            ORDER BY RT.rdate DESC, T.ttime DESC
            LIMIT 5 OFFSET 0;
        """, (user_id,))
        retweets = cursor.fetchall()

        print("\n--- Feed ---")
        print("\nTweets:")
        for tweet in tweets:
            print(f"Tweet ID: {tweet[0]}, Date: {tweet[2]}, Time: {tweet[3]}, Text: {tweet[4]}")

        print("\nRetweets:")
        for retweet in retweets:
            print(f"Retweet ID: {retweet[0]}, Date: {retweet[2]}, Time: {retweet[3]}, Text: {retweet[4]}")

    except sqlite3.Error as e:
        print("An error occurred while fetching the feed:", e)

# Compose tweet
def compose_tweet(cursor, connection, user_id):
    print("\n=== Compose Tweet ===")
    tweet_text = input("Enter your tweet (use # to tag hashtags): ")
    hashtags = re.findall(r'#\w+', tweet_text)

    reply_to_tid = input("If this is a reply, enter its tweet ID (or press Enter to skip): ")
    reply_to_tid = int(reply_to_tid) if reply_to_tid.isdigit() else None

    # Validate reply_to_tid if provided
    if reply_to_tid:
        cursor.execute("SELECT COUNT(*) FROM tweets WHERE tid = ?", (reply_to_tid,))
        if cursor.fetchone()[0] == 0:
            print("Error: Reply-to tweet ID does not exist. Please try again.")
            return

    # Ensure the user_id exists in the users table
    cursor.execute("SELECT COUNT(*) FROM users WHERE usr = ?", (user_id,))
    if cursor.fetchone()[0] == 0:
        print("Error: User ID does not exist. Please try again.")
        return

    try:
        # Generate a unique tid
        cursor.execute("SELECT COALESCE(MAX(tid), 0) FROM tweets")
        new_tid = cursor.fetchone()[0] + 1  # starting from 1 if no tweets exist

        # Insert the tweet into the tweets table
        cursor.execute("""
            INSERT INTO tweets (tid, writer_id, text, tdate, ttime, replyto_tid) 
            VALUES (?, ?, ?, DATE('now'), TIME('now'), ?)
        """, (new_tid, user_id, tweet_text, reply_to_tid))
        connection.commit()
        print(f"Tweet posted with ID: {new_tid}")

        # Normalize and insert hashtags into the hashtag_mentions table
        for tag in set([tag[1:].lower() for tag in hashtags]):
            cursor.execute("INSERT INTO hashtag_mentions (tid, term) VALUES (?, ?)", (new_tid, tag))
        connection.commit()

    except sqlite3.IntegrityError as e:
        print(f"An error occurred while posting the tweet: Integrity error: {e}")
    except sqlite3.Error as e:
        print(f"An error occurred while posting the tweet: {e}")

# retweet function
def retweet_tweet(cursor, connection, user_id):
    print("\n=== Retweet a Tweet ===")
    tweet_id = input("Enter the Tweet ID to retweet: ")
    
    try:
        # check if the tweet exists
        cursor.execute("SELECT writer_id FROM tweets WHERE tid = ?", (tweet_id,))
        result = cursor.fetchone()
        if not result:
            print("Error: The Tweet ID does not exist.")
            return
        
        original_writer_id = result[0]

        # check if the user has already retweeted this tweet
        cursor.execute("""
            SELECT COUNT(*) 
            FROM retweets 
            WHERE tid = ? AND retweeter_id = ?
        """, (tweet_id, user_id))
        if cursor.fetchone()[0] > 0:
            print("You have already retweeted this tweet.")
            return

        # insert the retweet into the retweets table
        cursor.execute("""
            INSERT INTO retweets (tid, retweeter_id, writer_id, spam, rdate) 
            VALUES (?, ?, ?, 0, DATE('now'))
        """, (tweet_id, user_id, original_writer_id))
        connection.commit()
        print("Retweet successful!")

    except sqlite3.Error as e:
        print(f"An error occurred while retweeting: {e}")

# Search tweets by keyword
def search_tweets(cursor, keyword):
    try:

        #newly added in--------------
        # Construct pattern to match only whole words
        pattern = f'% {keyword} %'  # Matches keyword surrounded by spaces
        pattern_start = f'{keyword} %'  # Matches keyword at the start
        pattern_end = f'% {keyword}'  # Matches keyword at the end
        exact_pattern = keyword  # Matches only the exact keyword
        #newly added in-------------

        #---------
        cursor.execute("""
            SELECT tid, writer_id, text, tdate, ttime 
            FROM tweets 
            WHERE (text LIKE ? COLLATE NOCASE
               OR text LIKE ? COLLATE NOCASE
               OR text LIKE ? COLLATE NOCASE
               OR text = ? COLLATE NOCASE)
               OR tid IN (SELECT tid FROM hashtag_mentions WHERE term = ?)
            ORDER BY tdate DESC
            LIMIT 5 OFFSET 0;
        """, (pattern, pattern_start, pattern_end, exact_pattern, keyword))
        #--------


      #  cursor.execute("""
      #      SELECT tid, writer_id, text, tdate, ttime 
      #      FROM tweets 
       #     WHERE text LIKE '%' || ? || '%' 
        #       OR tid IN (SELECT tid FROM hashtag_mentions WHERE term = ?)
         ##  LIMIT 5 OFFSET 0;
     #   """, (keyword, keyword))
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
def list_followers(cursor, connection, user_id):
    try:
        offset = 0  # starting offset for pagination
        while True:
            # fetch followers 5 at a time
            cursor.execute("""
                SELECT flwer, name 
                FROM follows 
                JOIN users ON follows.flwer = users.usr 
                WHERE flwee = ?
                LIMIT 5 OFFSET ?;
            """, (user_id, offset))
            followers = cursor.fetchall()
            
            if not followers:
                if offset == 0:
                    print("\nYou have no followers.")
                else:
                    print("\nNo more followers to display.")
                return

            print("\n--- Followers ---")
            for idx, follower in enumerate(followers, start=1 + offset):
                print(f"{idx}. User ID: {follower[0]}, Name: {follower[1]}")

            # more options to see more followers or select one
            print("\nOptions:")
            print("1. See more followers")
            print("2. Select a follower")
            print("3. Go back")

            choice = input("Choose an option: ")
            if choice == '1':
                offset += 5
            elif choice == '2':
                while True:
                    follower_choice = input("Enter the ID of a follower to view details, or 'q' to go back: ")
                    if follower_choice.lower() == 'q':
                        return
                    if follower_choice.isdigit():
                        follower_choice_id = int(follower_choice)
                        selected_follower = next((f[0] for f in followers if f[0] == follower_choice_id), None)
                        if selected_follower is None:
                            print("Invalid choice. Please try again.")
                            continue
                        break
                    else:
                        print("Invalid choice. Please try again.")

                #  details of the selected follower
                cursor.execute("""
                    SELECT 
                        (SELECT COUNT(*) FROM tweets WHERE writer_id = ?) AS num_tweets,
                        (SELECT COUNT(*) FROM follows WHERE flwer = ?) AS num_following,
                        (SELECT COUNT(*) FROM follows WHERE flwee = ?) AS num_followers;
                """, (selected_follower, selected_follower, selected_follower))
                stats = cursor.fetchone()

                print(f"\n--- Details for User ID {selected_follower} ---")
                print(f"Number of Tweets: {stats[0]}")
                print(f"Number of Users Followed: {stats[1]}")
                print(f"Number of Followers: {stats[2]}")

                # the 3 most recent tweets
                cursor.execute("""
                    SELECT tid, text, tdate, ttime 
                    FROM tweets 
                    WHERE writer_id = ?
                    ORDER BY tdate DESC, ttime DESC
                    LIMIT 3;
                """, (selected_follower,))
                tweets = cursor.fetchall()

                print("\n--- Recent Tweets ---")
                if tweets:
                    for tweet in tweets:
                        print(f"Tweet ID: {tweet[0]}, Text: {tweet[1]}, Date: {tweet[2]}, Time: {tweet[3]}")
                else:
                    print("This user has no tweets.")

                # additional options
                while True:
                    print("\nOptions:")
                    print("1. Follow this user")
                    print("2. See more tweets")
                    print("3. Go back")
                    option = input("Choose an option: ")

                    if option == '1':
                        follow_user(cursor, connection, user_id, selected_follower)
                    elif option == '2':
                        tweet_offset = 3
                        while True:
                            cursor.execute("""
                                SELECT tid, text, tdate, ttime 
                                FROM tweets 
                                WHERE writer_id = ?
                                ORDER BY tdate DESC, ttime DESC
                                LIMIT 5 OFFSET ?;
                            """, (selected_follower, tweet_offset))
                            more_tweets = cursor.fetchall()

                            if not more_tweets:
                                print("\nNo more tweets to display.")
                                break

                            for tweet in more_tweets:
                                print(f"Tweet ID: {tweet[0]}, Text: {tweet[1]}, Date: {tweet[2]}, Time: {tweet[3]}")

                            tweet_offset += 5
                            more = input("See more tweets? (y/n): ").lower()
                            if more != 'y':
                                break
                    elif option == '3':
                        break
                    else:
                        print("Invalid option. Please try again.")
            elif choice == '3':
                return
            else:
                print("Invalid option. Please try again.")
    except sqlite3.Error as e:
        print("An error occurred while listing followers or fetching details:", e)

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
                    print("3. Retweet a Tweet")  
                    print("4. Search Tweets")
                    print("5. Search Users")
                    print("6. List Followers")
                    print("7. Follow a User")
                    print("8. Unfollow a User")
                    print("9. Logout")
                    option = input("\nChoose an option: ")
                    
                    if option == '1':
                        display_feed(cursor, user_id)
                    elif option == '2':
                        compose_tweet(cursor, connection, user_id)
                    elif option == '3':  
                        retweet_tweet(cursor, connection, user_id)
                    elif option == '4':
                        keyword = input("Enter keyword to search tweets: ")
                        search_tweets(cursor, keyword)
                    elif option == '5':
                        keyword = input("Enter keyword to search users: ")
                        search_users(cursor, keyword)
                    elif option == '6':
                        list_followers(cursor, connection, user_id)
                    elif option == '7':
                        flwee = input("Enter the user ID to follow: ")
                        follow_user(cursor, connection, user_id, flwee)
                    elif option == '8':
                        flwee = input("Enter the user ID to unfollow: ")
                        unfollow_user(cursor, connection, user_id, flwee)
                    elif option == '9':
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

-- SQLite

--1. Login Query: done
--Find out if userID and pwd exists in table, by searching through it
SELECT * FROM users WHERE usr = ? AND pwd = ?;

--2. Registration Query: done
--If a user does not exist, register them
INSERT INTO users (usr, name, email, phone, pwd) VALUES (?, ?, ?, ?, ?);

--3. List Tweets:
--List all tweets and retweets after user login
SELECT T.tid, T.writer_id, T.text, T.tdate, T.ttime
FROM tweets T
WHERE T.writer_id = F.flower
UNION ALL
SELECT RT.tid, RT.writer_id, RT.text, RT.tdate, T.ttime
FROM retweets RT
WHERE RT.writer_id = F.flower
ORDER By T.tdate, RT.tdate DESC
LIMIT 5

--4. Search for tweets by keywords:
SELECT tid, writer_id, text, tdate, ttime 
FROM tweets 
WHERE text LIKE '%' || ? || '%' 
   OR tid IN (
       SELECT tid FROM hashtag_mentions WHERE term = ?
   )
ORDER BY tdate DESC
LIMIT 5 OFFSET ?;

--5. Search for users by keywords:
SELECT U.usr, U.name, U.
FROM users U
Where U.name LIKE '%' || ? || '%' 


--6: Compose a tweet: done
-- if a tweet contains a hashtag, insert # into hashtag_mentions table
INSERT INTO tweets (tid, writer_id, text, tdate, ttime, replyto_tid) 
VALUES (?, ?, ?, DATE('now'), TIME('now'), ?);
INSERT INTO hashtag_mentions (tid, term) VALUES (?, ?);


--7: List followers: done
--list the followers of the user 
SELECT flwer, name 
FROM follows 
JOIN users ON follows.flwer = users.usr 
WHERE flwee = ?
LIMIT 5 OFFSET ?;

--retrieve user details
SELECT 
    (SELECT COUNT(*) FROM tweets WHERE writer_id = ?) AS num_tweets,
    (SELECT COUNT(*) FROM follows WHERE flwer = ?) AS num_following,
    (SELECT COUNT(*) FROM follows WHERE flwee = ?) AS num_followers;

--retrieve the most recent 3 tweets
SELECT tid, text, tdate, ttime 
FROM tweets 
WHERE writer_id = ?
ORDER BY tdate DESC, ttime DESC
LIMIT 3;



--display all tables
--SELECT * FROM tweets;
--SELECT * FROM hashtag_mentions;
/*
try:
    # Connect to the SQLite database
    connection = sqlite3.connect('/Users/angelasolanki/Desktop/CMPUT291/prj-sample.db')
    cursor = connection.cursor()
    print("Connected to the database successfully!")

    # Example query to check the connection (optional)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in the database:", tables)

except sqlite3.Error as e:
    print(f"An error occurred: {e}")

finally:
    # Close the connection when done
    if connection:
        connection.close()
        print("Connection closed.") 
    */
    

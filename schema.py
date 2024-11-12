import sqlite3

# Connect to (or create) the database
connection = sqlite3.connect("social_network.db")  # Creates social_network.db
cursor = connection.cursor()

# Enable foreign key constraints (SQLite requires this command)
cursor.execute("PRAGMA foreign_keys = ON;")

# Define your reordered schema with table drops and creations
schema = """
DROP TABLE IF EXISTS hashtag_mentions;
DROP TABLE IF EXISTS retweets;
DROP TABLE IF EXISTS include;
DROP TABLE IF EXISTS follows;
DROP TABLE IF EXISTS tweets;
DROP TABLE IF EXISTS lists;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    usr         int,
    name        text,
    email       text,
    phone       int,
    pwd         text,
    primary key (usr)
);

CREATE TABLE follows (
    flwer       int,
    flwee       int,
    start_date  date,
    primary key (flwer, flwee),
    foreign key (flwer) references users(usr) ON DELETE CASCADE,
    foreign key (flwee) references users(usr) ON DELETE CASCADE
);

CREATE TABLE lists (
    owner_id    int,
    lname       text,
    PRIMARY KEY (owner_id, lname),
    FOREIGN KEY (owner_id) REFERENCES users(usr) ON DELETE CASCADE
);

CREATE TABLE tweets (
    tid         int,
    writer_id   int,
    text        text,
    tdate       date, 
    ttime       time,
    replyto_tid int,
    PRIMARY KEY (tid),
    FOREIGN KEY (writer_id) REFERENCES users(usr) ON DELETE CASCADE,
    FOREIGN KEY (replyto_tid) REFERENCES tweets(tid) ON DELETE CASCADE
);

CREATE TABLE retweets (
    tid         int,
    retweeter_id   int, 
    writer_id      int, 
    spam        int,
    rdate       date,
    PRIMARY KEY (tid, retweeter_id),
    FOREIGN KEY (tid) REFERENCES tweets(tid) ON DELETE CASCADE,
    FOREIGN KEY (retweeter_id) REFERENCES users(usr) ON DELETE CASCADE,
    FOREIGN KEY (writer_id) REFERENCES users(usr) ON DELETE CASCADE
);

CREATE TABLE hashtag_mentions (
    tid         int,
    term        text,
    primary key (tid, term),
    FOREIGN KEY (tid) REFERENCES tweets(tid) ON DELETE CASCADE
);

CREATE TABLE include (
    owner_id    int,
    lname       text,
    tid         int,
    PRIMARY KEY (owner_id, lname, tid),
    FOREIGN KEY (owner_id, lname) REFERENCES lists(owner_id, lname) ON DELETE CASCADE,
    FOREIGN KEY (tid) REFERENCES tweets(tid) ON DELETE CASCADE
);
"""

# Execute the schema script to create tables
cursor.executescript(schema)

# Insert sample data
users_data = [
    (1, "Alice", "alice@example.com", 1234567890, "alicepass"),
    (2, "Bob", "bob@example.com", 2345678901, "bobpass"),
    (3, "Charlie", "charlie@example.com", 3456789012, "charliepass")
]

tweets_data = [
    (1, 1, "Hello world!", "2023-01-01", "12:00:00", None),
    (2, 2, "This is a tweet!", "2023-01-02", "13:00:00", None),
    (3, 1, "Reply to my own tweet", "2023-01-02", "14:00:00", 1)  # reply to tweet ID 1
]

# Insert sample data into users table
cursor.executemany("INSERT INTO users (usr, name, email, phone, pwd) VALUES (?, ?, ?, ?, ?)", users_data)

# Insert sample data into tweets table
cursor.executemany("INSERT INTO tweets (tid, writer_id, text, tdate, ttime, replyto_tid) VALUES (?, ?, ?, ?, ?, ?)", tweets_data)

# Verify tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in database:", tables)

# Commit changes and close the connection
connection.commit()
connection.close()

print("Database and tables created successfully with sample data.")
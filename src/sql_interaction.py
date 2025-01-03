import sqlite3

USER_IDS_SQL = """
CREATE TABLE IF NOT EXISTS User_Ids(
    user_id text PRIMARY KEY
);
"""

USER_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS Users(
    user_id text NOT NULL ,
    username text NOT NULL ,
    LP INTEGER,
    MR INTEGER,
    Rank text,
    occurence_dt TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User_Ids(user_id)
);
"""

MATCHES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS Matches(
    Replay_ID text NOT NULL PRIMARY KEY,
    occurence_dt TEXT NOT NULL,
    match_type text NOT NULL,
    views INTEGER
);
"""

MATCH_CONTESTANTS_SQL = """
CREATE TABLE IF NOT EXISTS Match_Contestants(
    Replay_ID text NOT NULL,
    Side text,
    User_ID text NOT NULL,
    character text,
    control_type text,
    result text,
    PRIMARY KEY (Replay_ID, User_ID),
    FOREIGN KEY (Replay_ID) REFERENCES Matches(Replay_ID),
    FOREIGN KEY (User_ID) REFERENCES User_Ids(user_id)
);
"""

ROUND_SQL = """
CREATE TABLE IF NOT EXISTS Match_Rounds(
    Replay_ID text NOT NULL,
    Round_Number INTEGER NOT NULL,
    User_Id text NOT NULL,
    Result text NOT NULL,
    PRIMARY KEY (Replay_Id, User_Id, Round_Number),
    FOREIGN KEY (Replay_ID) REFERENCES Matches(Replay_ID),
    FOREIGN KEY (User_ID) REFERENCES User_Ids(user_id)
);
"""

def sqlite_init(filepath):
    conn = sqlite3.connect(filepath)
    conn.execute(USER_IDS_SQL)
    conn.execute(USER_TABLE_SQL)
    conn.execute(MATCHES_TABLE_SQL)
    conn.execute(MATCH_CONTESTANTS_SQL)
    conn.execute(ROUND_SQL)
    conn.close()
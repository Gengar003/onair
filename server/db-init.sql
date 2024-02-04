CREATE TABLE IF NOT EXISTS signs(
    url TEXT PRIMARY KEY,
    registered_ts INTEGER, 
    last_successful_ts INTEGER DEFAULT 0
)
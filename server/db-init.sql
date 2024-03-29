CREATE TABLE IF NOT EXISTS signs(
    url TEXT PRIMARY KEY,
    num_failures INTEGER DEFAULT 0,
    registered_ts INTEGER, 
    last_successful_ts INTEGER DEFAULT 0
)
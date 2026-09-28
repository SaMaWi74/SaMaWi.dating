PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT OR REPLACE INTO schema_meta (key, value)
VALUES ('schema_version', '1');

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    birth_date TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_active_at TEXT,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','active','suspended','deleted'))
);

CREATE TABLE IF NOT EXISTS profiles (
    user_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    bio TEXT,
    country_code TEXT,
    region TEXT,
    locality TEXT,
    latitude_private REAL,
    longitude_private REAL,
    verification_status TEXT NOT NULL DEFAULT 'unverified',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS dating_intentions (
    code TEXT PRIMARY KEY,
    label TEXT NOT NULL
);

INSERT OR IGNORE INTO dating_intentions(code,label) VALUES
('relationship','Relationship'),
('dating','Dating'),
('friendship','Friendship'),
('activities','Activities'),
('friends_plus','Friends+'),
('adventure','Adventure');

CREATE TABLE IF NOT EXISTS profile_intentions (
    user_id TEXT NOT NULL,
    intention_code TEXT NOT NULL,
    PRIMARY KEY (user_id, intention_code),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (intention_code) REFERENCES dating_intentions(code)
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    sender_user_id TEXT NOT NULL,
    recipient_user_id TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    moderation_status TEXT NOT NULL DEFAULT 'pending'
        CHECK (moderation_status IN ('pending','allowed','held','blocked')),
    risk_score INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (sender_user_id) REFERENCES users(id),
    FOREIGN KEY (recipient_user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS reports (
    id TEXT PRIMARY KEY,
    reporter_user_id TEXT NOT NULL,
    reported_user_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reporter_user_id) REFERENCES users(id),
    FOREIGN KEY (reported_user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active_at);
CREATE INDEX IF NOT EXISTS idx_profiles_locality ON profiles(country_code, region, locality);
CREATE INDEX IF NOT EXISTS idx_messages_sender_created ON messages(sender_user_id, created_at);

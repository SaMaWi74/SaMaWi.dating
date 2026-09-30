CREATE TABLE IF NOT EXISTS profile_photos (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    r2_key TEXT NOT NULL UNIQUE,
    is_primary INTEGER NOT NULL DEFAULT 0,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_profile_photos_user_order
ON profile_photos(user_id, sort_order, created_at);

CREATE UNIQUE INDEX IF NOT EXISTS idx_profile_photos_primary
ON profile_photos(user_id) WHERE is_primary = 1;

INSERT OR IGNORE INTO profile_photos (id, user_id, r2_key, is_primary, sort_order)
SELECT lower(hex(randomblob(16))), user_id, profile_photo_key, 1, 0
FROM profiles
WHERE profile_photo_key IS NOT NULL AND profile_photo_key <> '';

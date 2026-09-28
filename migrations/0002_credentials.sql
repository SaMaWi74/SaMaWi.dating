-- SaMaWi Dating: credentials and email verification state
ALTER TABLE users ADD COLUMN password_hash TEXT;
ALTER TABLE users ADD COLUMN email_verified_at TEXT;

CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);

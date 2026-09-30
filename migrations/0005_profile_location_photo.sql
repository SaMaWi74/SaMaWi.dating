ALTER TABLE profiles ADD COLUMN postal_code TEXT;
ALTER TABLE profiles ADD COLUMN profile_photo_key TEXT;
CREATE INDEX IF NOT EXISTS idx_profiles_location ON profiles(country_code, postal_code, locality);

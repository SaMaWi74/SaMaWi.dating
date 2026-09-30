-- Extended profile, interests and interview model

ALTER TABLE profiles ADD COLUMN gender TEXT;
ALTER TABLE profiles ADD COLUMN looking_for TEXT;
ALTER TABLE profiles ADD COLUMN smoking_status TEXT;
ALTER TABLE profiles ADD COLUMN education TEXT;
ALTER TABLE profiles ADD COLUMN children_status TEXT;
ALTER TABLE profiles ADD COLUMN household TEXT;
ALTER TABLE profiles ADD COLUMN relationship_status TEXT;
ALTER TABLE profiles ADD COLUMN wants_children TEXT;
ALTER TABLE profiles ADD COLUMN height_cm INTEGER;
ALTER TABLE profiles ADD COLUMN weight_kg INTEGER;
ALTER TABLE profiles ADD COLUMN hair_color TEXT;
ALTER TABLE profiles ADD COLUMN eye_color TEXT;
ALTER TABLE profiles ADD COLUMN fitness_level TEXT;
ALTER TABLE profiles ADD COLUMN religion TEXT;
ALTER TABLE profiles ADD COLUMN motto TEXT;

CREATE TABLE IF NOT EXISTS profile_languages (
    user_id TEXT NOT NULL,
    language_code TEXT NOT NULL,
    PRIMARY KEY (user_id, language_code),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS profile_diets (
    user_id TEXT NOT NULL,
    diet_code TEXT NOT NULL,
    PRIMARY KEY (user_id, diet_code),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS interest_categories (
    code TEXT PRIMARY KEY,
    sort_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS interests (
    code TEXT PRIMARY KEY,
    category_code TEXT NOT NULL,
    label_de TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (category_code) REFERENCES interest_categories(code)
);

CREATE TABLE IF NOT EXISTS profile_interests (
    user_id TEXT NOT NULL,
    interest_code TEXT NOT NULL,
    PRIMARY KEY (user_id, interest_code),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (interest_code) REFERENCES interests(code)
);

CREATE TABLE IF NOT EXISTS interview_questions (
    code TEXT PRIMARY KEY,
    question_de TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS profile_interview_answers (
    user_id TEXT NOT NULL,
    question_code TEXT NOT NULL,
    answer TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (user_id, question_code),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (question_code) REFERENCES interview_questions(code)
);

INSERT OR IGNORE INTO interest_categories(code,sort_order) VALUES
('film',10),('music',20),('outdoor',30),('indoor',40),('going_out',50),('art_making',60),
('music_making',70),('literature',80),('collecting',90),('sciences',100),('travel',110),
('destinations',120),('water_sports',130),('winter_sports',140),('martial_arts',150),
('fitness',160),('endurance',170),('extreme_sports',180),('ball_sports',190);

INSERT OR IGNORE INTO interview_questions(code,question_de,sort_order) VALUES
('describe_yourself','Beschreibe dich in ein paar Sätzen',10),
('desired_partner','Beschreibe deinen Wunschpartner',20),
('ideal_relationship','Wie sieht deine optimale Beziehung aus?',30),
('breakfast','Was gibt’s bei Dir zum Frühstück?',40),
('important_in_life','Was ist Dir wichtig im Leben?',50),
('type_zodiac','Welcher Typ bist Du? Welches Sternzeichen/Aszendent hast Du?',60),
('perfect_holiday','Beschreibe Deinen perfekten Urlaub.',70),
('typical_weekend','Wie sieht Dein Wochenende typischerweise aus?',80),
('free_time','Was machst Du in Deiner Freizeit?',90),
('desert_island','Welche 3 Dinge würdest Du auf eine einsame Insel nehmen, und warum?',100);

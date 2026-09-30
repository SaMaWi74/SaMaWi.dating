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
    label_de TEXT,
    label_en TEXT,
    label_fr TEXT,
    label_it TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS interests (
    code TEXT PRIMARY KEY,
    category_code TEXT NOT NULL,
    label_de TEXT NOT NULL,
    label_en TEXT,
    label_fr TEXT,
    label_it TEXT,
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
    question_en TEXT,
    question_fr TEXT,
    question_it TEXT,
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

INSERT OR IGNORE INTO interest_categories(code,label_de,label_en,label_fr,label_it,sort_order) VALUES
('film','Filmgeschmack','Movies','Films','Film',10),
('music','Musikgeschmack','Music','Musique','Musica',20),
('outdoor','Outdoor-Aktivitäten','Outdoor activities','Activités de plein air','Attività all’aperto',30),
('indoor','Indoor-Aktivitäten','Indoor activities','Activités en intérieur','Attività al chiuso',40),
('going_out','Ausgehen','Going out','Sorties','Uscire',50),
('art_making','Kunst selber machen','Making art','Créer de l’art','Fare arte',60),
('music_making','Musik selber machen','Making music','Faire de la musique','Fare musica',70),
('literature','Literatur','Literature','Littérature','Letteratura',80),
('collecting','Ich sammle','Collecting','Collections','Collezionismo',90),
('sciences','Wissenschaften','Sciences & knowledge','Sciences et savoir','Scienze e conoscenza',100),
('travel','Reisen','Travel','Voyages','Viaggi',110),
('destinations','Reiseziele','Destinations','Destinations','Destinazioni',120),
('water_sports','Wassersport','Water sports','Sports nautiques','Sport acquatici',130),
('winter_sports','Wintersport','Winter sports','Sports d’hiver','Sport invernali',140),
('martial_arts','Kampfsport','Martial arts','Arts martiaux','Arti marziali',150),
('fitness','Fitness','Fitness','Fitness','Fitness',160),
('endurance','Ausdauersport','Endurance sports','Sports d’endurance','Sport di resistenza',170),
('extreme_sports','Extremsport','Extreme sports','Sports extrêmes','Sport estremi',180),
('ball_sports','Ballsport','Ball sports','Sports de balle','Sport con la palla',190);

INSERT OR IGNORE INTO interview_questions(code,question_de,question_en,question_fr,question_it,sort_order) VALUES
('describe_yourself','Beschreibe dich in ein paar Sätzen','Describe yourself in a few sentences','Décris-toi en quelques phrases','Descriviti in poche frasi',10),
('desired_partner','Beschreibe deinen Wunschpartner','Describe the partner you are looking for','Décris le partenaire que tu recherches','Descrivi il partner che stai cercando',20),
('ideal_relationship','Wie sieht deine optimale Beziehung aus?','What does your ideal relationship look like?','À quoi ressemble ta relation idéale ?','Com’è la tua relazione ideale?',30),
('breakfast','Was gibt’s bei Dir zum Frühstück?','What do you have for breakfast?','Qu’est-ce que tu prends au petit-déjeuner ?','Cosa mangi a colazione?',40),
('important_in_life','Was ist Dir wichtig im Leben?','What is important to you in life?','Qu’est-ce qui est important pour toi dans la vie ?','Cosa è importante per te nella vita?',50),
('type_zodiac','Welcher Typ bist Du? Welches Sternzeichen/Aszendent hast Du?','What kind of person are you? What is your zodiac sign/ascendant?','Quel genre de personne es-tu ? Quel est ton signe astrologique/ascendant ?','Che tipo di persona sei? Qual è il tuo segno zodiacale/ascendente?',60),
('perfect_holiday','Beschreibe Deinen perfekten Urlaub.','Describe your perfect holiday.','Décris tes vacances parfaites.','Descrivi la tua vacanza perfetta.',70),
('typical_weekend','Wie sieht Dein Wochenende typischerweise aus?','What does a typical weekend look like for you?','À quoi ressemble généralement ton week-end ?','Com’è di solito il tuo fine settimana?',80),
('free_time','Was machst Du in Deiner Freizeit?','What do you do in your free time?','Que fais-tu pendant ton temps libre ?','Cosa fai nel tempo libero?',90),
('desert_island','Welche 3 Dinge würdest Du auf eine einsame Insel nehmen, und warum?','Which 3 things would you take to a desert island, and why?','Quelles sont les 3 choses que tu emporterais sur une île déserte, et pourquoi ?','Quali 3 cose porteresti su un’isola deserta, e perché?',100);

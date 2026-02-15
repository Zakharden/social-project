-- SQLite schema for Skill Exchange Platform

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    birth_date DATE NOT NULL,
    location TEXT NOT NULL,
    photo_path TEXT DEFAULT '/static/images/default-avatar.jpg',
    teach_skills TEXT,
    learn_skills TEXT,
    languages TEXT,
    interests TEXT,
    work_place TEXT,
    study_place TEXT,
    about TEXT,
    social_vk TEXT,
    social_tg TEXT,
    social_gh TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    used BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reviewer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    reviewed_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS exchanges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',
    progress INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS available_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    is_booked BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS meetings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    initiator_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    participant_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    meeting_link TEXT NOT NULL,
    scheduled_time DATETIME NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS random_coffee_meetings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organizer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    date DATETIME NOT NULL,
    city TEXT NOT NULL,
    description TEXT NOT NULL,
    is_online BOOLEAN NOT NULL DEFAULT FALSE,
    link TEXT NOT NULL,
    organizer_name TEXT NOT NULL,
    organizer_age INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_skills (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    skill_type TEXT CHECK (skill_type IN ('teach', 'learn')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, skill_id, skill_type)
);

CREATE TABLE IF NOT EXISTS blog_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    excerpt TEXT,
    author_name TEXT NOT NULL,
    article_url TEXT NOT NULL,
    views INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_reviews_reviewed_id ON reviews(reviewed_id);
CREATE INDEX IF NOT EXISTS idx_exchanges_user_id ON exchanges(user_id);
CREATE INDEX IF NOT EXISTS idx_available_slots_user_id ON available_slots(user_id);
CREATE INDEX IF NOT EXISTS idx_meetings_initiator_id ON meetings(initiator_id);
CREATE INDEX IF NOT EXISTS idx_meetings_participant_id ON meetings(participant_id);
CREATE INDEX IF NOT EXISTS idx_meetings_scheduled_time ON meetings(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_random_coffee_meetings_date ON random_coffee_meetings(date);
CREATE INDEX IF NOT EXISTS idx_user_skills_user_id ON user_skills(user_id);
CREATE INDEX IF NOT EXISTS idx_user_skills_skill_id ON user_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_blog_posts_created_at ON blog_posts(created_at);

INSERT INTO skills (name, category) VALUES
    ('Python', 'Programming'),
    ('JavaScript', 'Programming'),
    ('Java', 'Programming'),
    ('C++', 'Programming'),
    ('C#', 'Programming'),
    ('Ruby', 'Programming'),
    ('PHP', 'Programming'),
    ('Swift', 'Programming'),
    ('Kotlin', 'Programming'),
    ('HTML', 'Web'),
    ('CSS', 'Web'),
    ('React', 'Web'),
    ('Vue.js', 'Web'),
    ('Angular', 'Web'),
    ('Node.js', 'Web'),
    ('Django', 'Web'),
    ('Flask', 'Web'),
    ('SQL', 'Database'),
    ('MongoDB', 'Database'),
    ('PostgreSQL', 'Database'),
    ('Redis', 'Database'),
    ('Docker', 'DevOps'),
    ('Kubernetes', 'DevOps'),
    ('AWS', 'Cloud'),
    ('Git', 'DevOps'),
    ('Linux', 'System'),
    ('Agile', 'Methodology'),
    ('Scrum', 'Methodology'),
    ('UI/UX Design', 'Design'),
    ('Data Science', 'Data'),
    ('Machine Learning', 'Data')
ON CONFLICT(name) DO NOTHING;


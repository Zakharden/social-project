-- Skill Exchange Platform schema (PostgreSQL)
-- The script is idempotent and can be safely re-run.

-- Users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    location VARCHAR(255) NOT NULL,
    photo_path VARCHAR(255) DEFAULT '/static/images/default-avatar.jpg',
    -- Legacy fields (kept for backward compatibility with older templates/code)
    teach_skills TEXT[],
    learn_skills TEXT[],
    languages TEXT[],
    interests TEXT[],
    work_place VARCHAR(255),
    study_place VARCHAR(255),
    about TEXT,
    social_vk VARCHAR(255),
    social_tg VARCHAR(255),
    social_gh VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Password reset
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE
);

-- Reviews
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    reviewer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    reviewed_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Skill exchanges
CREATE TABLE IF NOT EXISTS exchanges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    progress INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Availability slots
CREATE TABLE IF NOT EXISTS available_slots (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    is_booked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Meetings between users
CREATE TABLE IF NOT EXISTS meetings (
    id SERIAL PRIMARY KEY,
    initiator_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    participant_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    meeting_link TEXT NOT NULL,
    scheduled_time TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Random coffee (community meetings)
CREATE TABLE IF NOT EXISTS random_coffee_meetings (
    id SERIAL PRIMARY KEY,
    organizer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    date TIMESTAMP NOT NULL,
    city VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    is_online BOOLEAN NOT NULL DEFAULT FALSE,
    link VARCHAR(500) NOT NULL,
    organizer_name VARCHAR(200) NOT NULL,
    organizer_age INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Skills directory
CREATE TABLE IF NOT EXISTS skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User skills (teach/learn)
CREATE TABLE IF NOT EXISTS user_skills (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    skill_type VARCHAR(20) CHECK (skill_type IN ('teach', 'learn')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, skill_id, skill_type)
);

-- Blog posts (external links)
CREATE TABLE IF NOT EXISTS blog_posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    excerpt TEXT,
    author_name VARCHAR(100) NOT NULL,
    article_url VARCHAR(255) NOT NULL,
    views INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens(token);
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

-- Seed base skills (safe to re-run)
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
ON CONFLICT (name) DO NOTHING;


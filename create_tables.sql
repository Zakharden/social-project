-- Создание таблицы пользователей
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    location VARCHAR(255) NOT NULL,
    photo_path VARCHAR(255) DEFAULT '/static/images/default-avatar.jpg',
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

-- Создание таблицы токенов для сброса пароля
CREATE TABLE password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    token VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE
);

-- Создание таблицы отзывов
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    reviewer_id INTEGER REFERENCES users(id),
    reviewed_id INTEGER REFERENCES users(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы обменов навыками
CREATE TABLE exchanges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    progress INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы доступных слотов для календаря
CREATE TABLE available_slots (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    is_booked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для оптимизации запросов
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_reviews_reviewed_id ON reviews(reviewed_id);
CREATE INDEX idx_exchanges_user_id ON exchanges(user_id);
CREATE INDEX idx_available_slots_user_id ON available_slots(user_id);
CREATE INDEX idx_password_reset_tokens_token ON password_reset_tokens(token);

-- Создание таблицы встреч
CREATE TABLE meetings (
    id SERIAL PRIMARY KEY,
    initiator_id INTEGER REFERENCES users(id),
    participant_id INTEGER REFERENCES users(id),
    platform VARCHAR(50) NOT NULL,
    meeting_link TEXT NOT NULL,
    scheduled_time TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индекса для оптимизации запросов встреч
CREATE INDEX idx_meetings_initiator_id ON meetings(initiator_id);
CREATE INDEX idx_meetings_participant_id ON meetings(participant_id);
CREATE INDEX idx_meetings_scheduled_time ON meetings(scheduled_time); 
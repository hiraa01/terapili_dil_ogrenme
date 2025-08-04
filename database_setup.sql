-- Terapili Dil Öğrenme Veritabanı Kurulum Scripti
-- Bu dosyayı MySQL'de çalıştırarak gerekli tabloları oluşturun

-- Veritabanını oluştur (eğer yoksa)
CREATE DATABASE IF NOT EXISTS proje_db;
USE proje_db;

-- Kullanıcılar tablosu
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    level VARCHAR(10) DEFAULT 'A1',
    language VARCHAR(20) DEFAULT 'english',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Sohbetler tablosu
CREATE TABLE IF NOT EXISTS chats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) DEFAULT 'Yeni Sohbet',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Sohbet mesajları tablosu
CREATE TABLE IF NOT EXISTS chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chat_id INT NOT NULL,
    message_type ENUM('user', 'bot') NOT NULL,
    message_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
);

-- Günlük yazıları tablosu
CREATE TABLE IF NOT EXISTS diary_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    text TEXT NOT NULL,
    mood VARCHAR(50),
    words JSON,
    bot_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Kelime puanları tablosu
CREATE TABLE IF NOT EXISTS word_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    word VARCHAR(100) NOT NULL,
    score INT DEFAULT 1,
    game_type VARCHAR(20) DEFAULT 'daily',
    last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_word (user_id, word)
);

-- Günlük kelimeler tablosu
CREATE TABLE IF NOT EXISTS daily_words (
    id INT AUTO_INCREMENT PRIMARY KEY,
    language VARCHAR(20) NOT NULL,
    level VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    word VARCHAR(100) NOT NULL,
    translations JSON NOT NULL,
    hint TEXT NOT NULL,
    difficulty INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_daily_word (language, level, date, word)
);

-- Kullanıcı ilerleme tablosu
CREATE TABLE IF NOT EXISTS user_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_points INT DEFAULT 0,
    daily_streak INT DEFAULT 0,
    last_daily_date DATE,
    level_progress JSON DEFAULT '{}',
    chat_words_count INT DEFAULT 0,
    diary_words_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_progress (user_id)
);

-- İndeksler (performans için)
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_chats_user_id ON chats(user_id);
CREATE INDEX idx_chat_messages_chat_id ON chat_messages(chat_id);
CREATE INDEX idx_diary_entries_user_id ON diary_entries(user_id);
CREATE INDEX idx_word_scores_user_id ON word_scores(user_id);
CREATE INDEX idx_daily_words_language_level_date ON daily_words(language, level, date);
CREATE INDEX idx_user_progress_user_id ON user_progress(user_id);

-- Örnek veriler (isteğe bağlı)
-- INSERT INTO users (username, email, password_hash, level, language) VALUES 
-- ('Test User', 'test@example.com', 'hashed_password', 'A1', 'english');

-- Tabloları kontrol et
SHOW TABLES;

-- Tablo yapılarını kontrol et
DESCRIBE users;
DESCRIBE chats;
DESCRIBE chat_messages;
DESCRIBE diary_entries;
DESCRIBE word_scores;
DESCRIBE daily_words;
DESCRIBE user_progress; 
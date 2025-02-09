-- CREATE TABLE users (
--     user_id        BIGINT AUTO_INCREMENT PRIMARY KEY,  -- PK
--     username       VARCHAR(50) NOT NULL,               -- 사용자명
--     email          VARCHAR(100) NOT NULL UNIQUE,        -- 이메일(유니크)
--     password       VARCHAR(255) NOT NULL,              -- 비밀번호(해싱된 값)
--     created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     updated_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
-- );

-- CREATE TABLE industries (
--     industry_id    INT AUTO_INCREMENT PRIMARY KEY,  -- PK
--     industry_name  VARCHAR(100) NOT NULL           -- 산업명
-- );

-- CREATE TABLE user_industries (
--     user_id        BIGINT NOT NULL,
--     industry_id    INT NOT NULL,
--     PRIMARY KEY (user_id, industry_id),
--     FOREIGN KEY (user_id)
--         REFERENCES users (user_id)
--         ON DELETE CASCADE ON UPDATE CASCADE,
--     FOREIGN KEY (industry_id)
--         REFERENCES industries (industry_id)
--         ON DELETE CASCADE ON UPDATE CASCADE
-- );


-- CREATE TABLE chat_sessions (
--     chat_session_id  BIGINT AUTO_INCREMENT PRIMARY KEY,  -- PK
--     user_id          BIGINT NOT NULL,                    -- 세션 생성 회원 ID
--     created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     updated_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
--     FOREIGN KEY (user_id)
--         REFERENCES users (user_id)
--         ON DELETE CASCADE ON UPDATE CASCADE
-- );


-- CREATE TABLE chat_messages (
--     chat_message_id  BIGINT AUTO_INCREMENT PRIMARY KEY,  -- PK
--     chat_session_id  BIGINT NOT NULL,                    -- 어떤 세션에 속한 메시지인지
--     sender_role      ENUM('user','assistant','system') NOT NULL,  -- 메시지 주체
--     message          TEXT NOT NULL,                      -- 실제 대화 내용
--     created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (chat_session_id)
--         REFERENCES chat_sessions (chat_session_id)
--         ON DELETE CASCADE ON UPDATE CASCADE
-- );







-- INSERT INTO users (username, email, password)
-- VALUES
-- ('admin',   'admin@example.com',   'admin'),
-- ('alice',   'alice@example.com',   'hashed_pw_1'),
-- ('bob',     'bob@example.com',     'hashed_pw_2'),
-- ('charlie', 'charlie@example.com', 'hashed_pw_3'),
-- ('david',   'david@example.com',   'hashed_pw_4'),
-- ('erin',    'erin@example.com',    'hashed_pw_5'),
-- ('frank',   'frank@example.com',   'hashed_pw_6'),
-- ('grace',   'grace@example.com',   'hashed_pw_7'),
-- ('hank',    'hank@example.com',    'hashed_pw_8'),
-- ('irene',   'irene@example.com',   'hashed_pw_9'),
-- ('jack',    'jack@example.com',    'hashed_pw_10');


-- INSERT INTO industries (industry_name)
-- VALUES
-- ('Technology'),
-- ('Finance'),
-- ('Healthcare'),
-- ('Retail'),
-- ('Manufacturing'),
-- ('Education'),
-- ('Hospitality'),
-- ('Transportation'),
-- ('Entertainment'),
-- ('Agriculture');


-- INSERT INTO user_industries (user_id, industry_id)
-- VALUES
-- (1, 1),
-- (1, 2),
-- (2, 1),
-- (2, 3),
-- (3, 2),
-- (3, 4),
-- (4, 4),
-- (4, 1),
-- (5, 5),
-- (6, 2),
-- (7, 3),
-- (8, 1),
-- (9, 7),
-- (10, 8),
-- (10, 1);


-- INSERT INTO chat_sessions (user_id)
-- VALUES
-- (1),
-- (2),
-- (3),
-- (4),
-- (5),
-- (6),
-- (7),
-- (8),
-- (9),
-- (10);


-- INSERT INTO chat_messages (chat_session_id, sender_role, message)
-- VALUES
-- -- 세션 1에 대한 메시지 3개
-- (1, 'user',      'Hello, this is user 1.'),
-- (1, 'assistant', 'Hello user 1, how can I help you?'),
-- (1, 'user',      'I am just testing the chat.'),

-- -- 세션 2
-- (2, 'user',      'User 2 checking in.'),
-- (2, 'assistant', 'Hi user 2, how may I assist you?'),
-- (2, 'user',      'Just exploring the service.'),

-- -- 세션 3
-- (3, 'user',      'What is the weather like today?'),
-- (3, 'assistant', 'The forecast is sunny with a chance of clouds.'),
-- (3, 'user',      'Thanks for the info!'),

-- -- 세션 4
-- (4, 'user',      'Hi there, user 4 here!'),
-- (4, 'assistant', 'Hello user 4! What can I do for you today?'),
-- (4, 'user',      'I need some suggestions for dinner.'),

-- -- 세션 5
-- (5, 'system',    'System message for session 5.'),
-- (5, 'assistant', 'How can I help you, user 5?'),
-- (5, 'user',      'I have a question about your API.'),

-- -- 세션 6
-- (6, 'user',      'Hello, user 6 wants to chat.'),
-- (6, 'assistant', 'Hi user 6, I am here to help.'),
-- (6, 'user',      'Great, let me ask a few things.'),

-- -- 세션 7
-- (7, 'assistant', 'Welcome user 7!'),
-- (7, 'user',      'Thank you, assistant.'),
-- (7, 'assistant', 'How may I assist you?'),

-- -- 세션 8
-- (8, 'user',      'Greetings from user 8.'),
-- (8, 'assistant', 'Hi user 8, nice to meet you.'),
-- (8, 'system',    'System check: everything looks good.'),

-- -- 세션 9
-- (9, 'user',      'User 9 saying hello.'),
-- (9, 'assistant', 'Hello user 9, how can I help?'),
-- (9, 'user',      'No issues, just testing the waters.'),

-- -- 세션 10
-- (10, 'assistant','Assistant message for session 10.'),
-- (10, 'user',     'User 10 here. Thanks.'),
-- (10, 'assistant','Anytime, user 10!');

#-- init.sql 파일
CREATE TABLE
IF NOT EXISTS delivery
(
    id INT AUTO_INCREMENT PRIMARY KEY,
    tracking_number VARCHAR
(255) NOT NULL,
    status VARCHAR
(50) NOT NULL,
    location VARCHAR
(255)
);
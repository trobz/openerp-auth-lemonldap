/* setup user and database */
DROP DATABASE IF EXISTS lemon_user_auth;

CREATE DATABASE IF NOT EXISTS lemon_user_auth CHARACTER SET = 'utf8';
USE lemon_user_auth;

/* setup tables */

CREATE TABLE IF NOT EXISTS lemon_user (
    id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    oe_id INT NOT NULL,
    oe_database VARCHAR(250) NOT NULL DEFAULT "",
    username VARCHAR(250) NOT NULL,
    email VARCHAR(250) NOT NULL DEFAULT "",
    created_at TIMESTAMP NOT NULL DEFAULT 0,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=MYISAM;

CREATE TABLE IF NOT EXISTS lemon_auth (
    id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    username VARCHAR(250) NOT NULL,
    password VARCHAR(40) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT 0,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=MYISAM;

CREATE INDEX lemon_auth_username_index on lemon_auth(username);
CREATE INDEX lemon_user_username_index on lemon_user(username);


GRANT ALL PRIVILEGES ON lemon_user_auth.* TO 'lemonldap'@'localhost' IDENTIFIED BY 'We_1deQnBc';

/* insert default admin user */

INSERT INTO lemon_user (oe_id, oe_database, username, email, created_at, updated_at) VALUES (1, 'webaddons', 'admin', 'admin@lemon.dev', null, null);
INSERT INTO lemon_auth (username, password, created_at, updated_at) VALUES ('admin', sha1('admin'), null, null);

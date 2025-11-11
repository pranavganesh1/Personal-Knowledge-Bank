DROP DATABASE IF EXISTS pkb1;
create database pkb1;
use pkb1;

CREATE TABLE app_user (
user_id INT auto_increment primary key,
name varchar(100) not null,
email varchar(150) not null unique,
created_at timestamp default current_timestamp
);


create table notebook (
notebook_id INT auto_increment primary key,
user_id INT not null,
title varchar(200) not null,
description TEXT,
created_at timestamp default current_timestamp
);

create table category (
category_id INT auto_increment primary key,
name varchar(100) not null unique,
description text
);

create table category_hierarchy (
parent_category_id INT not null,
sub_category_id INt not null,
primary key (parent_category_id, sub_category_id),
foreign key (parent_category_id) references category(category_id) on delete cascade,
foreign key (sub_category_id) references category(category_id) on delete cascade,
CHECK (parent_category_id <> sub_category_id)
);

create table note (
note_id INT auto_increment primary key,
user_id Int not null,
category_id int,
notebook_id int,
title varchar(200) not null,
content text,
is_public boolean default false,
created_at timestamp default current_timestamp,
updated_at timestamp default current_timestamp on update current_timestamp,
foreign key (user_id) references app_user (user_id) on delete cascade,
foreign key (category_id) references category(category_id),
foreign key (notebook_id) references notebook(notebook_id) on delete set null
);

create table note_history (
history_id INT auto_increment primary key,
note_id INT,
title_snapshot varchar (100),
content_snapshot text,
edited_by INT,
version_at timestamp default current_timestamp,
foreign key(note_id) references note(note_id) on delete cascade,
foreign key (edited_by) references app_user(user_id)
);

create table tag (
tag_id INT auto_increment primary key,
name varchar(80) not null unique
);

create table note_tag(
note_id int not null,
tag_id int not null,
primary key (note_id, tag_id),
foreign key (note_id) references note(note_id) on delete cascade,
foreign key (tag_id) references tag(tag_id) on delete cascade
);

create table attachment(
attachment_id INT auto_increment primary key,
note_id int not null,
filename varchar(225) not null,
filepath text,
uploaded_at timestamp default current_timestamp,
foreign key (note_id)references note(note_id) on delete cascade
);
create table collaboration(
collab_id INT auto_increment primary key,
note_id int not null,
shared_with_user_id int not null,
access_level ENUM('read','write','owner') not null,
shared_at timestamp default current_timestamp,
unique(note_id, shared_with_user_id),
foreign key (note_id) references note (note_id) on delete cascade,
foreign key (shared_with_user_id)references app_user(user_id) on delete cascade
);

CREATE TABLE comment (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    note_id INT NOT NULL,
    user_id INT NOT NULL,
    comment_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES note(note_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES app_user(user_id) ON DELETE CASCADE
);


CREATE TABLE reminder (
    reminder_id INT AUTO_INCREMENT PRIMARY KEY,
    note_id INT NOT NULL,
    user_id INT NOT NULL,
    reminder_text VARCHAR(300),
    due_date DATETIME,
    status ENUM('pending','done','skipped') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES note(note_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES app_user(user_id) ON DELETE CASCADE
);

CREATE TABLE tag_suggestion (
    suggestion_id INT AUTO_INCREMENT PRIMARY KEY,
    note_id INT NOT NULL,
    tag_id INT NOT NULL,
    confidence DECIMAL(5,4) DEFAULT 0.0,
    suggested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES note(note_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tag(tag_id)
);

CREATE TABLE bookmark (
    bookmark_id INT AUTO_INCREMENT PRIMARY KEY,
    note_id INT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(note_id, user_id),
    FOREIGN KEY (note_id) REFERENCES note(note_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES app_user(user_id) ON DELETE CASCADE
);





insert into app_user (name,email) values
('Pranav','pranav@example.com'),
('aman','aman@example.com'),
('aaron','aaron@example.com'),
('aashilesh','aashilesh@example.com'),
('aaditya','aaditya@example.com');
--
-- select * from app_user;
--

insert into category (name, description) values
('Course Notes','Notes for courses'),
('Personal','Personal knowledge and diary'),
('Work','Work-related notes'),
('Programming','Code snippets and references'),
('Research','Research papers and project findings');
--
-- select * from category;
--

insert into category_hierarchy values (1,4);
--
-- select * from category_hierarchy;
--

INSERT INTO notebook (user_id, title, description) VALUES
(1,'DBMS Notes','Concepts, SQL, and normalization'),
(1,'Daily Journal','Everyday personal thoughts'),
(2,'Team Project','Collaborative space for shared tasks'),
(3,'Work Tasks','Work-related documentation'),
(4,'Coding Practice','Code snippets and problem-solving');
--
-- select * from notebook;
--

INSERT INTO tag (name) VALUES 
('sql'),
('mysql'),
('design'),
('todo'),
('ai');
--
-- SELECT * FROM tag;
--

insert into note (user_id, category_id, notebook_id, title, content, is_public) values
(1,1,1,'ER Model','ER diagram and normalization','0'),
(1,4,1,'Indexing Tips','Use proper indexing for performance','1'),
(2,2,2,'Daily Reflection','Worked on group project module','0'),
(3,3,4,'Client Meeting','Discussed project timeline','0'),
(4,4,5,'Python Basics','Learning functions and loops','1');
--
SELECT note_id, title, content, user_id, category_id, notebook_id, is_public, created_at 
FROM note;
--

INSERT INTO note_tag VALUES 
(1,3),
(2,1),
(2,2),
(3,4),
(5,5);
--
-- select nt.note_id, n.title as note_title, t.name as tag_name
-- from note_tag nt
-- join note n on nt.note_id = n.note_id
-- join tag t on nt.tag_id = t.tag_id;
--


INSERT INTO bookmark (note_id, user_id) VALUES 
(2,1),
(3,1),
(4,2),
(1,3),
(5,2);
--
-- SELECT b.bookmark_id, u.name AS bookmarked_by, n.title AS note_title, b.created_at
-- FROM bookmark b
-- JOIN app_user u ON b.user_id = u.user_id
-- JOIN note n ON b.note_id = n.note_id;
--


INSERT INTO collaboration (note_id, shared_with_user_id, access_level) VALUES
(1,2,'write'),
(2,3,'read'),
(3,4,'read'),
(4,5,'write'),
(5,1,'read');
--
-- SELECT c.collab_id, n.title AS note_title, u.name AS shared_with, c.access_level, c.shared_at
-- FROM collaboration c
-- JOIN note n ON c.note_id = n.note_id
-- JOIN app_user u ON c.shared_with_user_id = u.user_id;
--


INSERT INTO reminder (note_id, user_id, reminder_text, due_date)
VALUES 
(1,1,'Revise ER diagram', NOW() + INTERVAL 1 DAY),
(2,1,'Recheck indexing strategy', NOW() + INTERVAL 2 DAY),
(3,2,'Finish project summary', NOW() + INTERVAL 3 DAY),
(4,3,'Prepare meeting notes', NOW() + INTERVAL 1 DAY),
(5,4,'Complete Python exercises', NOW() + INTERVAL 4 DAY);
--
-- SELECT r.reminder_id, n.title AS note_title, u.name AS user_name, 
--        r.reminder_text, r.due_date, r.status
-- FROM reminder r
-- JOIN note n ON r.note_id = n.note_id
-- JOIN app_user u ON r.user_id = u.user_id;
--




-- ===============================
-- TRIGGERS & PROCEDURES
-- ===============================

DELIMITER $$

-- Drop existing
DROP TRIGGER IF EXISTS trg_note_version;
DROP TRIGGER IF EXISTS trg_notebook_updated;
DROP TRIGGER IF EXISTS trg_auto_todo_reminder;

DROP PROCEDURE IF EXISTS suggest_tag;
DROP PROCEDURE IF EXISTS share_note;
DROP PROCEDURE IF EXISTS mark_reminder_done;
DELIMITER ;

DELIMITER $$
-- Trigger 1: Version History
CREATE TRIGGER trg_note_version
BEFORE UPDATE ON note
FOR EACH ROW
BEGIN
    INSERT INTO note_history(note_id, title_snapshot, content_snapshot, edited_by, version_at)
    VALUES (OLD.note_id, OLD.title, OLD.content, OLD.user_id, NOW());
END $$
DELIMITER ;

DELIMITER $$
-- Trigger 2: Update notebook timestamp
CREATE TRIGGER trg_notebook_updated
AFTER UPDATE ON note
FOR EACH ROW
BEGIN
    IF OLD.notebook_id IS NOT NULL THEN
        UPDATE notebook SET created_at = NOW() WHERE notebook_id = OLD.notebook_id;
    END IF;
END $$
DELIMITER ;

DELIMITER $$
-- Trigger 3: Auto reminder when tag='todo'
CREATE TRIGGER trg_auto_todo_reminder
AFTER INSERT ON note_tag
FOR EACH ROW
BEGIN
    DECLARE tag_name VARCHAR(80);
    SELECT name INTO tag_name FROM tag WHERE tag_id = NEW.tag_id;
    IF tag_name = 'todo' THEN
        INSERT INTO reminder (note_id, user_id, reminder_text, due_date, status)
        SELECT NEW.note_id, n.user_id, 'Complete TODO item', NOW() + INTERVAL 7 DAY, 'pending'
        FROM note n WHERE n.note_id = NEW.note_id;
    END IF;
END $$
DELIMITER ;

DELIMITER $$
-- Procedure 1: suggest_tag
CREATE PROCEDURE suggest_tag(IN p_note INT, IN p_tag INT, IN p_conf DECIMAL(5,4))
BEGIN
    INSERT INTO tag_suggestion(note_id, tag_id, confidence, suggested_at)
    VALUES (p_note, p_tag, p_conf, NOW());
END $$
DELIMITER ;

DELIMITER $$
-- Procedure 2: share_note
CREATE PROCEDURE share_note(IN p_note INT, IN p_user INT, IN p_access VARCHAR(20))
BEGIN
    INSERT INTO collaboration(note_id, shared_with_user_id, access_level, shared_at)
    VALUES (p_note, p_user, p_access, NOW()) AS newrow
    ON DUPLICATE KEY UPDATE 
        access_level = newrow.access_level,
        shared_at = newrow.shared_at;
END $$
DELIMITER ;

DELIMITER $$
-- Procedure 3: mark_reminder_done
CREATE PROCEDURE mark_reminder_done(IN p_reminder INT)
BEGIN
    UPDATE reminder SET status='done' WHERE reminder_id = p_reminder;
END $$
DELIMITER ;
-- ===============================
-- TEST SECTION
-- ===============================

-- 1️ Test trigger: Update note → creates note_history
UPDATE note SET content = CONCAT(content, ' (edited)') WHERE note_id = 2;
SELECT * FROM note_history WHERE note_id = 2;

select * from note_history;


-- 2️ Test trigger: Add 'todo' tag → auto creates reminder
INSERT INTO note_tag (note_id, tag_id) VALUES (4,4);
SELECT * FROM reminder WHERE note_id = 4;

-- 3️ Test procedure: Suggest tag
CALL suggest_tag(1,3,0.95);
SELECT * FROM tag_suggestion;

-- 4️ Test procedure: Share note
CALL share_note(1,2,'write');
SELECT * FROM collaboration;

-- 5️ Test procedure: Mark reminder done
CALL mark_reminder_done(2);
SELECT * FROM reminder WHERE reminder_id = 2;



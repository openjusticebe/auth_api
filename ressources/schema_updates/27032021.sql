CREATE TYPE user_lang AS ENUM ('fr', 'nl', 'de', 'other');
CREATE TYPE user_status AS ENUM ('inactive', 'active', 'new');
ALTER TABLE users ADD COLUMN language user_lang DEFAULT 'fr';
ALTER TABLE users ADD COLUMN fname VARCHAR(100);
ALTER TABLE users ADD COLUMN lname VARCHAR(100);
ALTER TABLE users ADD COLUMN salt VARCHAR(255) default '';
ALTER TABLE users ADD COLUMN interest VARCHAR(50);
ALTER TABLE users ADD COLUMN status user_status default 'new';

DROP TYPE IF EXISTS user_type_enum;
DROP INDEX IF EXISTS user_ukey;
DROP INDEX IF EXISTS user_email;
DROP TABLE IF EXISTS users;

CREATE TYPE user_type_enum AS ENUM ('superadmin', 'admin', 'moderator', 'user');

CREATE TABLE "users" (
    id_internal SERIAL PRIMARY KEY,
    date_created TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    date_updated TIMESTAMP WITH TIME ZONE,
    userid UUID NOT NULL,
    name VARCHAR(100),
    username VARCHAR(100),
    email VARCHAR(200) UNIQUE NOT NULL,
    email_valid BOOLEAN,
    count_uploads JSONB,
    flags TEXT[],
    ukey VARCHAR(12),
    pass VARCHAR(100),
    profession TEXT,
    description TEXT,
    linkedin VARCHAR(250),
    twitter VARCHAR(250),
    access_prod user_type_enum DEFAULT NULL,
    access_test user_type_enum DEFAULT NULL,
    access_staging user_type_enum DEFAULT NULL,
    access_dev user_type_enum DEFAULT NULL
);

CREATE INDEX user_ukey ON "users" (ukey);
CREATE INDEX user_userid ON "users" (userid);
CREATE INDEX user_email ON "users" (email);

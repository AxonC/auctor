-- Required for the uuid type.
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE tasks (
    id uuid CONSTRAINT todos_pk PRIMARY KEY DEFAULT uuid_generate_v4(),
    name text NOT NULL,
    description text NOT NULL,
    username varchar(60) NOT NULL,
    priority smallint NOT NULL,
    duration smallint NOT NULL,
    due_date timestamp NOT NULL,
    completed_at timestamp
);

CREATE TABLE users (
    username varchar(60) PRIMARY KEY,
    name varchar(60) NOT NULL,
    password varchar(128) NOT NULL,
    UNIQUE(username)
);
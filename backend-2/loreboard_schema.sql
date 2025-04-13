-- Characters table
CREATE TABLE characters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    physical TEXT DEFAULT '',
    personality TEXT DEFAULT '',
    background TEXT DEFAULT '',
    goals TEXT DEFAULT '',
    relationships TEXT DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Places table
CREATE TABLE places (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    physical TEXT DEFAULT '',
    environment TEXT DEFAULT '',
    purpose TEXT DEFAULT '',
    history TEXT DEFAULT '',
    location TEXT DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Items table
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    physical TEXT DEFAULT '',
    function TEXT DEFAULT '',
    origin TEXT DEFAULT '',
    ownership TEXT DEFAULT '',
    properties TEXT DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Aliases table
CREATE TABLE aliases (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL, -- 'character', 'place', 'item'
    entity_id INTEGER NOT NULL,
    alias VARCHAR(255) NOT NULL
);

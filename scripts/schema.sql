-- This schema is used to setup a Database to run the tests.
-- It represents a semantic network: a labeled, directed graph

CREATE TABLE nodes(
    -- e.g. "Despacito", "Justin Bieber", "Pop", etc.
    name varchar(50) NOT NULL,

    -- e.g. "song", "artist", "genre", etc.
    type varchar(50) NOT NULL,

    -- NOTE: this field is an alias for SQLite's "row_id" column
    -- Setting this column to NULL at insert, will automatically populate it
    id INTEGER PRIMARY KEY
);

-- TODO: add constraints about node type (probably in a trigger function)
CREATE TABLE edges(
    source  int NOT NULL REFERENCES nodes(id),
    dest    int NOT NULL REFERENCES nodes(id),
    rel     varchar(40) NOT NULL,
    score   real NOT NULL CHECK (score >= 0 AND score <= 100),
    PRIMARY KEY (source, dest, rel)
);

CREATE TABLE artists(
    node_id                 int PRIMARY KEY REFERENCES nodes(id) NOT NULL,
    num_spotify_followers   int
);

CREATE TABLE songs(
    main_artist_id  int REFERENCES artists(node_id) NOT NULL,
    popularity      int CHECK ((popularity >= 0 AND popularity <= 100) OR popularity = NULL),
    duration_ms     int,
    node_id         int REFERENCES nodes(id) NOT NULL,
    spotify_uri     varchar(100)
);

CREATE TABLE genres(
    node_id int REFERENCES nodes(id) NOT NULL
);

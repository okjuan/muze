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

    -- see Spotify's audio features object:
    -- - https://developer.spotify.com/documentation/web-api/reference/object-model/#audio-features-object
    acousticness        real CHECK(acousticness >= 0 AND acousticness <= 1),
    danceability        real CHECK(danceability >= 0 AND danceability <= 1),
    energy              real CHECK(energy >= 0 AND energy <= 1),
    instrumentalness    real CHECK(instrumentalness >= 0 AND instrumentalness <= 1),
    liveness            real CHECK(liveness >= 0 AND liveness <= 1),
    loudness            real CHECK(loudness >= -60 AND loudness <= 0), -- in dB
    speechiness         real CHECK(speechiness >= 0 AND speechiness <= 1),
    valence             real CHECK(valence >= 0 AND valence <= 1),

    tempo               real CHECK(tempo > 0 AND tempo < 1000),
    mode                varchar(6) CHECK(mode == 'major' OR mode == 'minor'),
    musical_key         int CHECK(musical_key >= 0 AND musical_key < 12),
    -- see: https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-analysis/
    time_signature      int CHECK(time_signature >= 3 AND time_signature <= 7),

    popularity      int CHECK ((popularity >= 0 AND popularity <= 100) OR popularity = NULL),
    duration_ms     int,
    node_id         int REFERENCES nodes(id) NOT NULL,
    spotify_uri     varchar(100) UNIQUE
);

CREATE TABLE genres(
    node_id int REFERENCES nodes(id) NOT NULL
);

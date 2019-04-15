INSERT INTO nodes (name, type, id) VALUES ("Justin Bieber", "artist", 1);
INSERT INTO nodes (name, type, id) VALUES ("Justin Timberlake", "artist", 2);
INSERT INTO nodes (name, type, id) VALUES ("U2", "artist", 3);
INSERT INTO nodes (name, type, id) VALUES ("Shawn Mendes", "artist", 4);
INSERT INTO nodes (name, type, id) VALUES ("The Anti Justin Bieber", "artist", 5);

INSERT INTO artists (node_id, num_spotify_followers) VALUES (1, 4000);
INSERT INTO artists (node_id, num_spotify_followers) VALUES (2, 3000);
INSERT INTO artists (node_id, num_spotify_followers) VALUES (3, 2000);
INSERT INTO artists (node_id, num_spotify_followers) VALUES (4, 1000);
INSERT INTO artists (node_id, num_spotify_followers) VALUES (5, 0004);

INSERT INTO nodes (name, type, id) VALUES ("Despacito", "song", 10);
INSERT INTO nodes (name, type, id) VALUES ("Rock Your Body", "song", 11);
INSERT INTO nodes (name, type, id) VALUES ("Beautiful Day", "song", 12);
INSERT INTO nodes (name, type, id) VALUES ("In My Blood", "song", 13);
INSERT INTO nodes (name, type, id) VALUES ("Sorry", "song", 14);
INSERT INTO nodes (name, type, id) VALUES ("Sorry", "song", 15);

INSERT INTO nodes (name, type, id) VALUES ("Pop", "genre", 20);
INSERT INTO nodes (name, type, id) VALUES ("Super pop", "genre", 21);

INSERT INTO songs (main_artist_id, popularity, duration_ms, node_id, spotify_uri, valence)
    VALUES (1, 10, 222222, 10, 'spotify:track:Despacito', 0.1);
INSERT INTO songs (main_artist_id, popularity, duration_ms, node_id, spotify_uri, valence)
    VALUES (1, 20, 333333, 14, 'spotify:track:Sorry', 0.3);
INSERT INTO songs (main_artist_id, popularity, duration_ms, node_id, spotify_uri, valence)
    VALUES (2, 30, 444444, 11, 'spotify:track:RockYourBody', 0.7);
INSERT INTO songs (main_artist_id, popularity, duration_ms, node_id, spotify_uri, valence)
    VALUES (3, 60, 111111, 12, 'spotify:track:BeautifulDay', 1);
INSERT INTO songs (main_artist_id, node_id) VALUES (4, 13);
INSERT INTO songs (main_artist_id, node_id) VALUES (5, 15);

-- * Define some edges for testing
-- -------------------------------
-- Justin Bieber is similar to Justin Timberlake and Shawn Mendes
INSERT INTO edges (source, dest, rel, score) VALUES (1, 2, "similar to", 75);
INSERT INTO edges (source, dest, rel, score) VALUES (1, 4, "similar to", 100);
INSERT INTO edges (source, dest, rel, score) VALUES (1, 20, "of genre", 100);
INSERT INTO edges (source, dest, rel, score) VALUES (1, 21, "of genre", 100);
INSERT INTO edges (source, dest, rel, score) VALUES (2, 20, "of genre", 100);

-- "Despacito" is similar to "Rock Your Body"
INSERT INTO edges (source, dest, rel, score) VALUES (10, 11, "similar to", 100);

-- Justin Bieber and U2 are related in some unimportant way
INSERT INTO edges (source, dest, rel, score) VALUES (1, 3, "other relation", 50);
-- "Despacito" and "Beautiful Day" are related in some unimportant way
INSERT INTO edges (source, dest, rel, score) VALUES (10, 12, "other relation", 50);
import random
import sqlite3
from contextlib import closing


class KnowledgeBaseAPI:
    """
    This layer stores the interface to the knowledge-engine.
    It is primarily used by the query-engine and knowledge-generation
    components.
    """

    def __init__(self, dbName):
        self.dbName = dbName
        self.approved_relations = dict(
            similarity="similar to",
            genre="of genre",
        )
        # based on Spotify's audio features object
        self.song_audio_features = set([
            "acousticness", "danceability", "energy", "tempo",
            "instrumentalness", "liveness", "loudness", "mode",
            "speechiness", "valence", "musical_key", "time_signature",
        ])

        LESS_COMP = lambda val1, val2: val1 < val2
        MORE_COMP = lambda val1, val2: val1 > val2
        self.SONG_ADJECTIVES = dict(
            [ # workaround for keys containing spaces
                ("more acoustic", dict(name='acousticness', comparison=MORE_COMP)),
                ("less acoustic", dict(name='acousticness', comparison=LESS_COMP)),
                ("less dancey", dict(name='danceability', comparison=LESS_COMP)),
                ("more popular", dict(name="popularity", comparison=MORE_COMP)),
                ("less popular", dict(name="popularity", comparison=LESS_COMP)),
            ],
            happier=dict(name='valence', comparison=MORE_COMP),
            sadder=dict(name='valence', comparison=LESS_COMP),
            dancier=dict(name='danceability', comparison=MORE_COMP),
            longer=dict(name='duration_ms', comparison=MORE_COMP),
            shorter=dict(name='duration_ms', comparison=MORE_COMP),
        )

    def _get_audio_feature_name(self, adjective):
        """Maps comparison phrase to its audio feature name.

        E.g.
            "more acoustic" => "acousticness"
            "less acoustic" => "acousticness"
            "happier"       => "valence"
            "sadder"        => "valence"

        Params:
            adjective (str): e.g. "more acoustic", "happier".

        Returns:
            (str): name of audio feature corresponding to adjective
                None if not found. e.g. "acousticness" for "more acoustic".
        """
        return self.SONG_ADJECTIVES.get(adjective, {}).get("name")

    def _get_comparison_func(self, adjective):
        """Returns a function f that determines whether the given adjective
        describes the relationship between two values.

        E.g. for adjective "more acoustic", function f is returned such that:
            - f(val1=0.1, val2=0.2) returns True.
            - f(val1=0.2, val2=0.1) returns False.
            - f(val1=0.2, val2=0.2) returns False.
            Where the args val1 and val2 are values for levels of
            acousticness.

        Params:
            adjective (str): e.g. "more acoustic", "happier".

        Returns:
            (func): with two parameters, val1 and val2, which
                are compared to determine whether val1 has relationship with
                val2 as described by the given adjective.
                For example: if adjective is "more acoustic", then calling the
                function with val1=0.1 and val2=0.5 (for acousticness)
                returns True since val2 has a higher acoustic value.
        """
        return self.SONG_ADJECTIVES.get(adjective, {}).get("comparison")

    def __str__(self):
        return "Knowledge Representation API object for {} DB.".format(self.dbName)

    @property
    def connection(self):
        conn = sqlite3.connect(self.dbName)
        # enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = 1")
        return conn

    def songs_are_related(self, song1_id, song2_id, rel_str):
        """Determines whether any two given songs are related in the way described.

        E.g. Determines whether 'thank u, next' is 'more acoustic' than 'bad idea'.
        E.g. Determines whether 'thank u, next' is 'happier' than 'bad idea'.

        NOTE: order of params matters.

        Params:
            song1_id (int): ID of song's node in semantic network.
            song2_id (int): ID of song's node in semantic network.

        Returns:
            (bool): True iff the two given songs are related in the way described.
        """
        if rel_str not in self.SONG_ADJECTIVES.keys():
            print(f"ERROR: relationship '{rel_str}' is not recognized.")
            return False

        compare_func = self._get_comparison_func(rel_str)
        if compare_func is None:
            print(f"ERROR: could not find comparison function for relationship: '{rel_str}'")
            return False

        feature_name = self._get_audio_feature_name(rel_str)
        if feature_name is None:
            print(f"ERROR: could not find feature name for relationship: '{rel_str}'")
            return False

        song1_data = self.get_song_data(song_id=song1_id)
        song2_data = self.get_song_data(song_id=song2_id)

        if len(song1_data) == 0:
            print(f"ERROR: Could not find song with id={song1_id}")
            return False
        if len(song2_data) == 0:
            print(f"ERROR: Could not find song with id={song2_id}")
            return False

        song1_val = song1_data[0].get(feature_name)
        song2_val = song2_data[0].get(feature_name)

        if song1_val is None:
            print(f"ERROR: could not find '{feature_name}' value for song with id={song1_id}")
            return False
        if song2_val is None:
            print(f"ERROR: could not find '{feature_name}' value for song '{song2_id}'")
            return False
        return compare_func(song1_val, song2_val)

    def get_related_entities(self, entity_name, rel_str="similar to"):
        """Finds all entities connected to the given entity in the semantic network.

        The given entity may be any of song, an artist, etc. The returned entity may or may not be
        the same type of entity.

        A warning is issued if the given rel_str not one of the 'approved' ones.

        NOTE: as of Oct 5 2019, the database does not contain song-song similarity data.
            (Even though the schema supports it; it's just an issue of filling up the DB!)

        Params:
            entity_name (string): name of entity (e.g. "Justin Bieber").
            rel_str (string): e.g. "similar to", "of genre".

        Returns:
            (list of strings): names of entities related to given entity.
                e.g. ["Justin Timberlake", "Shawn Mendes"]
        """
        if rel_str not in self.approved_relations.values():
            print("WARN: querying for invalid relations. Only allow: {}".format(self.approved_relations))

        try:
            with closing(self.connection) as con:
                # Auto-commit
                with con:
                    with closing(con.cursor()) as cursor:
                        # Inner query retrieves IDs of all related entities
                        cursor.execute("""
                            SELECT name
                            FROM nodes
                            WHERE id IN (
                                SELECT dest
                                FROM edges JOIN nodes ON source == id
                                WHERE name LIKE (?) AND rel == (?)
                            );
                        """, (entity_name, rel_str))
                        # [("Justin Timberlake",), ("Shawn Mendes",)] => ["Justin Timberlake", "Shawn Mendes"]
                        return [x[0] for x in cursor.fetchall()]

        except sqlite3.OperationalError as e:
            print("ERROR: Could not find entities similar to entity with name '{}': {}".format(entity_name, str(e)))
            return []

    def get_all_song_names(self):
        """Gets all song names from database.

        Returns:
            (list of str): song names.
        """
        try:
            # Auto-close
            with closing(self.connection) as con:
                # Auto-commit
                with con:
                    # Auto-close
                    with closing(con.cursor()) as cursor:
                        cursor.execute("""
                            SELECT name
                            FROM nodes
                            WHERE type = "song";
                        """)
                        return [x[0] for x in cursor.fetchall()]
        except sqlite3.OperationalError as e:
            print("ERROR: Could not retrieve songs: {}".format(str(e)))
        return []

    def get_song_data(self, song_name=None, song_id=None):
        """Gets all songs that match given name, along with their artists.

        Params:
            song_name (str): optional only if song_id is provided e.g. "thank u, next".
            song_id (int): ID of song in semantic network; optional only if song_id is provided.

        Returns:
            (list of dicts): each dict contains song_name and artist_name keys. Empty if not matches found or error.
                e.g. [
                    {
                        id: 1,
                        song_name: "Despacito",
                        artist_name: "Justin Bieber",
                        duration_ms: 11111,
                        popularity: 100,
                        spotify_uri: 'spotify:track:6ohzjop0VYBRZ12ichlwg5',

                        acousticness:   0.1,
                        danceability:   0.2,
                        energy:         0.3,
                        instrumentalness:   0.4,
                        liveness:       0.1,
                        loudness:       0.2,
                        speechiness:    0.3,
                        valence:        0.4,

                        tempo:          90,
                        mode:           'major',
                        musical_key:    3,
                        time_signature: 4,
                    },
                    ...
                ]
        """
        if song_name is None and song_id is None:
            print("ERROR: Require one of song name and song ID to retrieve song data.")
            return []
        elif song_name is None:
            song_name = "%" # match any string

        try:
            # Auto-close.
            with closing(self.connection) as con:
                # Auto-commit
                with con:
                    # Auto-close.
                    with closing(con.cursor()) as cursor:
                        cursor.execute("""
                            SELECT
                                song.name, artist.name, song.duration_ms, song.popularity,
                                song.id, song.spotify_uri, song.acousticness, song.danceability,
                                song.energy, song.instrumentalness, song.liveness, song.loudness,
                                song.speechiness, song.valence, song.tempo, song.mode,
                                song.musical_key, song.time_signature

                            FROM (
                                SELECT *
                                FROM songs JOIN nodes ON node_id == id
                                WHERE name LIKE (?)
                            ) AS song JOIN nodes AS artist ON main_artist_id == artist.id;
                        """, (song_name,))
                        return [
                            dict(
                                song_name=x[0], artist_name=x[1], duration_ms=x[2], popularity=x[3],
                                id=x[4], spotify_uri=x[5], acousticness=x[6], danceability=x[7],
                                energy=x[8], instrumentalness=x[9], liveness=x[10], loudness=x[11],
                                speechiness=x[12], valence=x[13], tempo=x[14], mode=x[15],
                                musical_key=x[16], time_signature=x[17],
                            ) for x in cursor.fetchall()
                            if song_id is None or song_id == x[4]
                        ]

        except sqlite3.OperationalError as e:
            print("ERROR: Could not retrieve data for song with name '{}': {}".format(song_name, str(e)))
            return []

    def get_artist_data(self, artist_name):
        """Get artist info.

        Params:
            artist_name (string): e.g. "Justin Bieber".

        Returns:
            (list of dict): keys: id, name, num_spotify_followers, genres. Empty if no matching artists found.
                e.g. [{
                    genres=['Pop'],
                    id=1,
                    num_spotify_followers=4000,
                    name="Justin Bieber",
                }, ...]
        """
        try:
            # Auto-close.
            with closing(self.connection) as con:
                # Auto-commit
                with con:
                    # Auto-close.
                    with closing(con.cursor()) as cursor:
                        cursor.execute("""
                            SELECT id, name, num_spotify_followers
                            FROM artists JOIN nodes ON node_id == id
                            WHERE name LIKE (?);
                        """, (artist_name,))
                        res_tuples = cursor.fetchall()

        except sqlite3.OperationalError as e:
            print("ERROR: Could not retrieve data for artist with name '{}': {}".format(artist_name, str(e)))
            return []

        results = []
        for res_tuple in res_tuples:
            results.append(dict(
                id=res_tuple[0],
                name=res_tuple[1],
                num_spotify_followers=res_tuple[2],
                genres=self.get_related_entities(artist_name, self.approved_relations["genre"]),
            ))
        return results

    def get_all_artist_names(self):
        """Get artist names.

        Returns:
            (list of str): artist names.
        """
        try:
            # Auto-close.
            with closing(self.connection) as con:
                # Auto-commit
                with con:
                    # Auto-close.
                    with closing(con.cursor()) as cursor:
                        cursor.execute("""
                            SELECT name
                            FROM nodes
                            WHERE type = "artist";
                        """)
                        return [x[0] for x in cursor.fetchall()]

        except sqlite3.OperationalError as e:
            print("ERROR: Could not retrieve artist data: {}".format(str(e)))
        return []

    def get_songs_by_artist(self, artist):
        """Retrieves list of songs for given artist.

        Param:
            artist (string): e.g. "Justin Bieber"

        Returns:
            (list of dicts): containing song names and semantic network IDs by given artist.
                None if artist is ambiguous or not found.
                e.g. [{"song_name": "Despacito", "id": 1}, {"song_name": "Sorry", "id":2}]
        """
        matching_artist_node_ids = self._get_matching_node_ids(artist)
        if len(matching_artist_node_ids) == 0:
            print("ERROR: could not find entry for artist '{}'".format(artist))
            return None

        elif len(matching_artist_node_ids) > 1:
            print("ERROR: found multiple entries for ambiguous artist name '{}'.".format(artist))
            return None

        artist_node_id = matching_artist_node_ids[0]
        try:
            with closing(self.connection) as con:
                with con:
                    with closing(con.cursor()) as cursor:
                        cursor.execute("""
                            SELECT name, node_id
                            FROM (
                                SELECT songs.node_id as node_id
                                FROM songs JOIN artists ON main_artist_id = artists.node_id
                                WHERE artists.node_id = (?)
                            ) as x JOIN nodes ON x.node_id = id;
                        """, (artist_node_id,))

                        # unpack tuples e.g. [("Despacito",)] => ["Despacito"]
                        return [dict(song_name=x[0], id=x[1]) for x in cursor.fetchall()]

        except sqlite3.OperationalError as e:
            print("ERROR: failed to find songs for artist '{0}'".format(
                artist))
            return None

    def get_random_song(self):
        """Returns Spotify URI for random song (or None)"""
        songs = self.get_all_song_names()
        song_name = songs[random.randrange(len(songs))]
        hits = self.get_song_data(song_name=song_name)
        if len(hits) == 0:
            # Just return Oops! I did it again by Britney
            return 'spotify:track:6naxalmIoLFWR0siv8dnQQ'
        else:
            return hits[0].get('spotify_uri')

    def get_node_ids_by_entity_type(self, entity_name):
        """Retrieves and organizes IDs of all nodes that match given entity name.

        Return:
            (dict): key=entity_types of all nodes with the given name, val=list of int IDs. Empty if no matches.
                e.g. {"artist": [1, 2], "song": [5,7]}
        """
        try:
            with closing(self.connection) as con:
                with con:
                    with closing(con.cursor()) as cursor:
                        cursor.execute("""
                            SELECT type, id
                            FROM nodes
                            WHERE name == (?)
                        """, (entity_name,))
                        node_ids_by_type = dict()
                        for x in cursor.fetchall():
                            ids = node_ids_by_type.setdefault(x[0], [])
                            ids.append(x[1])
                            node_ids_by_type[x[0]] = ids
                        return node_ids_by_type

        except sqlite3.OperationalError as e:
            print("ERROR: Could not retrieve ids for entity with name '{}': {}".format(entity_name, str(e)))
            return None

    def _get_matching_node_ids(self, node_name):
        """Retrieves IDs of all nodes matching the given name.

        Params:
            node_name (string): name of entity node. E.g. "Justin Bieber".

        Returns:
            (list of ints): ids of nodes corresponding to given name; empty if none found.
        """
        try:
            with closing(self.connection) as con:
                with con:
                    with closing(con.cursor()) as cursor:
                        cursor.execute("""
                            SELECT id
                            FROM nodes
                            WHERE name LIKE (?)
                        """, (node_name,))
                        res = cursor.fetchall()

        except sqlite3.OperationalError as e:
            print("ERROR: An error occurred when retrieving node ids: {}".format(e))

        if len(res) == 0:
            print("ERROR: Could not find node ID for name '{0}'.".format(node_name))
            return []

        elif len(res) > 1:
            print("Found multiple node IDs for name '{0}', returning first result.".format(node_name))

        # e.g. [(10,), (11,)] => [10, 11]
        return [x[0] for x in res]

    def connect_entities(self, source_node_name, dest_node_name, rel_str, score):
        """Inserts edge row into edges table.

        Params:
            source_node_name (string): Node name of entity with the outgoing edge.
                E.g. "Justin Bieber"; "Despacito"; "Pop"; etc.

            dest_node_name (string): Node name of entity with the incoming edge.
                E.g. "Shawn Mendes"; "In My Blood"; "Pop"; etc.

            rel_str (string): Type of relationship, which must be already present in 'relations' table.
                E.g. "similar to", "of genre".

            score (int): edge weight corresponding to percentage, must be [0,100] range.

        Returns:
            (bool): False if error occurred, True otherwise.
        """
        if rel_str not in self.approved_relations.values():
            print("WARN: adding unapproved relation. Only allow: {}".format(self.approved_relations))

        matching_src_nodes = self._get_matching_node_ids(source_node_name)
        matching_dst_nodes = self._get_matching_node_ids(dest_node_name)
        if len(matching_src_nodes) != 1 or len(matching_dst_nodes) != 1:
            print("ERROR: Could not find unique match for entities '{}', '{}'. Found {}, {} matches respectively" .format(
                source_node_name,
                dest_node_name,
                len(matching_src_nodes),
                len(matching_dst_nodes)),
            )
            return False

        source_node_id, dest_node_id = matching_src_nodes[0], matching_dst_nodes[0]

        try:
            with closing(self.connection) as conn:
                with conn:
                    with closing(conn.cursor()) as cursor:
                        cursor.execute("""
                            INSERT INTO edges (source, dest, rel, score)
                            VALUES (?, ?, ?, ?)
                        """, (source_node_id, dest_node_id, rel_str, score))

        except sqlite3.OperationalError as e:
            print("ERROR: Could not connect entities '{0}' and '{1}': {2}".format(
                source_node_name, dest_node_name, str(e)))
            return False

        except sqlite3.IntegrityError as e:
            print("ERROR: Could not connect entities '{0}' and '{1}' due to schema constraints: {2}".format(
                source_node_name, dest_node_name, str(e)))
            return False

        return True

    def _is_valid_entity_type(self, entity_type):
        """Indicates whether given entity type is valid.

        NOTE:
            - Ideally, we would have a table in our database for valid entity types.
            - Also, using enums would probably be cleaner.
        """
        return entity_type in ["artist", "song", "genre"]

    def add_artist(self, name, genres=[], num_spotify_followers=None):
        """Inserts given values into two tables: artists and nodes.

        Ensures that:
        - Given artist is only added if they are not already in the database.
        - Given artist is either added to both or neither.

        Params:
            name (string): e.g. "Justin Bieber"
            genres (list): e.g. ['indie r&b', 'malaysian indie']
            num_spotify_followers (int): number of Spotify followers.

        Returns:
            (int): node_id corresponding to given artist if added or already existed; None otherwise.
        """
        matching_nodes = self.get_node_ids_by_entity_type(name).get("artist", [])
        if len(matching_nodes) > 0:
            print("WARN: Artist '{}' already exists in semantic network. Aborting insertion.".format(name))
            return matching_nodes[0]

        node_id = self._add_node(name, "artist")
        if node_id is None:
            print("ERROR: Failed to add artist '{}' to semantic network.".format(name))
            return None

        try:
            with closing(self.connection) as con:
                with con:
                    with closing(con.cursor()) as cursor:
                        cursor.execute("""
                            INSERT INTO artists (node_id, num_spotify_followers) VALUES (?, ?);
                        """, (node_id, num_spotify_followers))

        except sqlite3.OperationalError as e:
            print("ERROR: Could not add artist '{0}'".format(
                name))
            return None

        except sqlite3.IntegrityError as e:
            print("ERROR: Could not add artist '{}' due to schema constraints: {}"
                .format(name, str(e)))
            return None

        for genre in genres:
            if self.add_genre(genre) is not None:
                genre_rel_str = self.approved_relations["genre"]
                if not self.connect_entities(name, genre, genre_rel_str, 100):
                    print("ERROR: could not connect genre '{}' and artist '{}'".format(genre, name))

            else:
                print("ERROR: Could not add genre '{}' for artist '{}'".format(genre, name))

        return node_id

    def add_song(self, name, artist, duration_ms=None, popularity=None, spotify_uri=None, audio_features=dict()):
        """Inserts given values into two tables: songs and nodes.

        Ensures that:
            - Given song is either added to both or neither.
            - Given artist is not ambiguous (only matches one 'artist' entry in nodes table).
            - Given tuple (song, artist) is only added if it does not already exist in database.

        Params:
            name (string): e.g. "Despacito"
            artist (string): e.g. "Justin Bieber"
            duration_ms (int): length of song e.g. 22222.
            popularity (int): in [0,100] range.
            spotify_uri (str): used for streaming e.g. 'spotify:track:6ohzjop0VYBRZ12ichlwg5'
            audio_features (dict): keys should be present in self.song_audio_features; otherwise,
                they are ignored e.g. {
                    'acousticness': 0.78,
                    'danceability': 0.647,
                    'energy': 0.309,
                    ...
                }

        Returns:
            (int): node_id corresponding to song if added or already existed; None otherwise.
        """
        matching_artist_node_ids = self.get_node_ids_by_entity_type(artist).get("artist", [])
        if len(matching_artist_node_ids) != 1:
            print("ERROR: Failed to add song '{}' because given artist '{}' corresponded to {} IDs (need 1)."
                .format(name, artist, len(matching_artist_node_ids)))
            return None
        artist_node_id = matching_artist_node_ids[0]

        existing_songs = self.get_song_data(name)
        for tmp_song in existing_songs:
            if tmp_song["artist_name"] == artist:
                print("WARN: Song '{}' by artist '{}' already exists in semantic network. Aborting insertion.".format(name, artist))
                return None

        node_id = self._add_node(name, "song")
        if node_id is None:
            print("ERROR: Failed to add song '{}' due to an error.".format(name))
            return None

        # Set ommitted audio features to None
        for audio_feature in self.song_audio_features:
            if audio_feature not in audio_features:
                audio_features[audio_feature] = None

        # Check for unknown audio features
        for audio_feature in audio_features:
            if audio_feature not in self.song_audio_features:
                print(f"WARN: audio feature '{audio_feature}' (given for song '{name}')\
                    is not recognized.")

        try:
            with closing(self.connection) as con:
                with con:
                    with closing(con.cursor()) as cursor:
                        x = audio_features
                        vals = (
                            artist_node_id, node_id, duration_ms, popularity, spotify_uri,
                            x['acousticness'], x['danceability'], x['energy'],
                            x['instrumentalness'], x['liveness'], x['mode'], x['loudness'],
                            x['speechiness'], x['valence'], x['tempo'], x['musical_key'],
                            x['time_signature'],
                        )
                        cursor.execute("""
                            INSERT INTO songs (
                                main_artist_id, node_id, duration_ms, popularity, spotify_uri,
                                acousticness, danceability, energy, instrumentalness, liveness, mode,
                                loudness, speechiness, valence, tempo, musical_key, time_signature
                            )
                            VALUES (
                                ?, ?, ?, ?, ?,
                                ?, ?, ?, ?, ?, ?,
                                ?, ?, ?, ?, ?, ?
                            );
                        """, vals)

        except sqlite3.OperationalError as e:
            print(f"ERROR: Could not add song '{name}' with artist '{artist}': {e}")
            return None

        except sqlite3.IntegrityError as e:
            print("ERROR: Could not add song '{}' with artist '{}' due to schema constraints: {}"
                .format(name, artist, str(e)))
            return None

        return node_id

    def add_genre(self, name):
        """Adds given value into two tables: genres and nodes.

        Ensures that:
        - Given genre is eiter added to both or neither.
        - Given genre is only added if not already in the database.

        Returns:
            (int): node_id if genre was added or it already existed; None otherwise (e.g. error occurred).
        """
        matching_nodes = self.get_node_ids_by_entity_type(name).get("genre", [])
        if len(matching_nodes) > 0:
            print("WARN: Genre '{}' already exists in semantic network. Aborting insertion.".format(name))
            return matching_nodes[0]

        node_id = self._add_node(name, "genre")
        if node_id is None:
            print("ERROR: Failed to add genre '{}' to semantic network.".format(name))
            return None

        try:
            with closing(self.connection) as con:
                with con:
                    with closing(con.cursor()) as cursor:
                        cursor.execute("""
                            INSERT INTO genres (node_id) VALUES (?);
                        """, (node_id,))

        except sqlite3.OperationalError as e:
            print("ERROR: Could not add artist '{0}'".format(
                name))
            return None

        except sqlite3.IntegrityError as e:
            print("ERROR: Could not add genre '{}' due to schema constraints: {}"
                .format(name, str(e)))
            return None
        return node_id

    def _add_node(self, entity_name, entity_type):
        """Adds given entity to knowledge representation system.

        In particular, this function adds a node to the semantic network by
        inserting it into the nodes table.

        Params:
            entity_name (string): for one of song, artist, etc.
                e.g. "Despacito", "Justin Bieber"

        Returns:
            id (int): id of new entry in nodes table for given entry; None if insertion failed.
        """
        if not self._is_valid_entity_type(entity_type):
            print("ERROR: Given entity type '{0}' is invalid.".format(entity_type))
            return None

        try:
            with closing(self.connection) as con:
                with con:
                    with closing(con.cursor()) as cursor:
                        # NULL is passed so that SQLite assigns the auto-generated row_id value
                        # see:  - https://www.sqlite.org/autoinc.html
                        #       - https://stackoverflow.com/questions/7905859/is-there-an-auto-increment-in-sqlite
                        cursor.execute("""
                            INSERT INTO nodes (name, type, id) VALUES (?, ?, NULL);
                        """, (entity_name, entity_type,))

        except sqlite3.OperationalError as e:
            print("ERROR: Could not insert entity with name '{}' into nodes table: {}".format(entity_name, str(e)))
            return None

        except sqlite3.IntegrityError as e:
            print("ERROR: Integrity constraints prevented insertion of entity with name '{}' into nodes table: {}"
                .format(entity_name, str(e)))
            return None

        node_ids = self.get_node_ids_by_entity_type(entity_name).get(entity_type, [])

        # NOTE: taking the max is a heuristic to disambiguate between multiplet matching ID:
        # Since we _just_ inserted the node and its id is autogenerated, it must have the largest id.
        return max(node_ids)

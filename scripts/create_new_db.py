"""
Author: John Verwolf.

This is an executable script that creates and saves
a new DB.

Example:
    python3 create_new_db.py -d ./knowledge_base/knowledge_base.db

    # With Spotify Credentials:
    python3 create_new_db.py -d ./knowledge_base/knowledge_base.db -s 123 123

"""

import os
import sys
from argparse import ArgumentParser

sys.path.append('../')
sys.path.append('.')
from scripts import test_db_utils


def setup_db_with_spotify_data(spotify_client_id,
                               spotify_secret_key,
                               infile,
                               db_path=None,
                               ):
    try:
        db_path = test_db_utils \
            .create_and_populate_db_with_spotify(spotify_client_id,
                                                 spotify_secret_key,
                                                 infile,
                                                 path=db_path,
                                                 )
    except FileNotFoundError as e:
        print("Please run cli.py from project directory!")
        sys.exit(1)
    return db_path


def setup_db(path: str = None):
    try:
        db_path = test_db_utils.create_and_populate_db(path)
    except FileNotFoundError as e:
        print("Please run cli.py from project directory!")
        sys.exit(1)
    return db_path

def main():
    print("Running DB setup script...")

    parser = ArgumentParser()
    parser.add_argument("-d", type=str, dest="db_path",
                        help=" Specifies a relative path to the DB, (include "
                             "the filename). Ex: -d ./new_db.sql")
    parser.add_argument("-s", type=str, nargs='*', dest="spotify_creds",
                        help=" Pulls data from Spotify, requires Spotify_client_id and"
                             " spotify_secret_key  "
                             "Ex: -s 12345 12345")
    parser.add_argument("-f", type=str, dest="infile",
                        help="Name of file containing artist names separated by newlines")
    args = parser.parse_args()

    db_path = args.db_path

    if os.path.isfile(db_path):
        print("Error: File \"{}\" already exists.".format(db_path),
              file=sys.stderr)
        sys.exit()

    if args.spotify_creds:
        try:
            spotify_client_id = args.spotify_creds[0]
            spotify_secret_key = args.spotify_creds[1]

        except Exception as e:
            print("Error, incorrect Spotify key format. "
                  "\nEx:"
                  "\n\tpython3 populate_db.py -d ./some_new_db.sql -s 1231231 12312312"
                  "\n{}".format(e),
                  file=sys.stdout)
            sys.exit()

        if args.infile is not None:
            infile = open(args.infile, "r")
        else:
            infile = sys.stdin
        setup_db_with_spotify_data(spotify_client_id,
                                   spotify_secret_key,
                                   infile,
                                   db_path=db_path,
                                   )
    else:
        setup_db(db_path)


if __name__ == "__main__":
    main()

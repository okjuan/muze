import sys
sys.path.extend(['.', '../'])

from knowledge_base.api import KnowledgeBaseAPI

SONG_FILE_NAME = "song_names.csv"
ARTIST_FILE_NAME = "artist_names.csv"
USAGE ="Usage: python extract_entities.py [-a for artists] [-s (for songs)] [-t (for running tests)]"

def print_to_csv(items, filename):
    with open(filename, "w") as f:
        for entry in items:
            entry = remove_dash_section(remove_parenthised_section(entry))
            # CSV format with itself as synonym
            f.write(f"\"{entry}\",\"{entry}\"\n")

def remove_parenthised_section(s):
    tokens = s.split("(")
    no_paren = ""
    for t in tokens:
        if ")" in t:
            no_paren += t.split(")")[-1]
        else:
            no_paren += t
    return no_paren.strip()

def remove_dash_section(s):
    return s.split("-")[0].strip()

def test_remove_parenthised_section():
    test_cases = [
        dict(input="Hello ()", expected="Hello"),
        dict(input="() Hello", expected="Hello"),
        dict(input="() Hello ()", expected="Hello"),
    ]
    total, fails = 0, 0
    for t in test_cases:
        res = remove_parenthised_section(t['input'])
        if res != t['expected']:
            print(f"FAIL: '{t['input']}' expected '{t['expected']}' got '{res}'")
            fails += 1
        total += 1
    print(f"Finished running test_remove_parenthised_section: Ran {total} tests with {fails} failures.")

def test_remove_dash_section():
    total, fails = 0, 0
    test_cases = [
        dict(input="Hello -", expected="Hello"),
        dict(input="Hello - Hi -", expected="Hello"),
        dict(input="Hello - (Ok)", expected="Hello"),
    ]
    total, fails = 0, 0
    for t in test_cases:
        res = remove_dash_section(t['input'])
        if res != t['expected']:
            print(f"FAIL: '{t['input']}' expected '{t['expected']}' got '{res}'")
            fails += 1
        total += 1
    print(f"Finished running test_remove_dash_section: Ran {total} tests with {fails} failures.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-t":
        print("Running tests...")
        test_remove_parenthised_section()
        test_remove_dash_section()

    else:
        music_api = KnowledgeBaseAPI("knowledge_base/knowledge_base.db")

        # print songs
        if sys.argv[1] == "-s":
            print("Fetching song names..")
            song_names = music_api.get_all_song_names()
            print_to_csv(song_names, SONG_FILE_NAME)
            print(f"Wrote to {SONG_FILE_NAME}")

        # print artists
        elif sys.argv[1] == "-a":
            print("Fetching artist names..")
            artist_names = music_api.get_all_artist_names()
            print_to_csv(artist_names, ARTIST_FILE_NAME)
            print(f"Wrote to {ARTIST_FILE_NAME}")

        else:
            print(USAGE)
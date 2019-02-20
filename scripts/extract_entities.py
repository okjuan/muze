import sys
sys.path.extend(['.', '../'])

from knowledge_base.api import KnowledgeBaseAPI

def print_to_csv(items, filename):
    with open(filename, "w") as f:
        for entry in items:
            # CSV format with itself as synonym
            # Truncate name to remove parentheses
            entry_no_paren = entry.split("(")[0]
            f.write(f"\"{entry_no_paren}\",\"{entry_no_paren}\"\n")



if __name__ == "__main__":
    music_api = KnowledgeBaseAPI("knowledge_base/knowledge_base.db")

    # print songs
    if len(sys.argv) == 1 or sys.argv[1] == "-s":
        song_names = music_api.get_all_song_names()
        print_to_csv(song_names, "song_names.csv")

    # print artists
    elif sys.argv[1] == "-a":
        artist_names = music_api.get_all_artist_names()
        print_to_csv(artist_names, "artist_names.csv")
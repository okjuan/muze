"""
Tests Dialogflow agent's voice recognition using generated voice files.
"""

import random
import requests
import subprocess
import sys

sys.path.extend(['.', '../', '../..'])
from knowledge_base.api import KnowledgeBaseAPI


SONG_SET_SIZE = 1
SH_GENERATE_DIALOGFLOW_ACCESS_TOKEN = "gcloud auth application-default print-access-token"
SH_CREATE_AUDIO_FILE = 'say -o play_song.wav --data-format=LEI16@22050 "{0}"'
SH_B64_ENCODE_AUDIO_FILE = f"base64 -i play_song.wav"


def test_find_slightly_different_song_intent(phrase_formats, audio_feature_adjectives, songs, out_file):
    """Checks intent, params, and confidence level in Dialogflow request for
    detecting the 'Find Slightly Different Song' intent.

    Params:
        phrase_formats (strings): with format fields 'song' and 'adj'.
        audio_feature_adjectives (list): 2-tuples, where 1st field is the name of one to be sent
            and the 2nd field is the name of the one expected to be detected by Dialogflow.
        songs (list): e.g. ["thank u, next", "bad idea", "needy"].
    """
    out_file.write("Testing intent: 'Find Slightly Different Song'\n")
    detect_intent_failures, song_extract_failures, adj_extract_failures = 0, 0, 0
    conf_level_sum, num_tests, num_passed = 0, 0, 0
    for phrase_f in phrase_formats:
        for adj, nominal_adj in audio_feature_adjectives:
            for song in songs:
                test_passed = True
                test_phrase = phrase_f.format(song=song, adj=adj),
                resp_contents = send_detect_intent_req(test_phrase)
                if resp_contents is None:
                    print(f"ERROR: could not run test with phrase: '{test_phrase}'")
                    continue

                detected_intent = resp_contents['detected_intent']
                if detected_intent != 'Find Slightly Different Song':
                    out_file.write(f"- Phrase: {test_phrase}\n")
                    out_file.write(f"\tDetected intent:\t '{detected_intent}'\n")
                    detect_intent_failures += 1
                    test_passed = False

                extracted_song = resp_contents['extracted_params'].get("song", "")
                if extracted_song.upper() != song.upper():
                    out_file.write(f"\tSong:\t '{extracted_song}' != '{song}' (expected)\n")
                    song_extract_failures += 1
                    test_passed = False

                extracted_adj = resp_contents['extracted_params'].get("audio_feature_adjective", "")
                if extracted_adj.upper() != nominal_adj.upper():
                    out_file.write(f"\tAdj:\t '{extracted_adj}' != '{nominal_adj}' (expected)\n")
                    adj_extract_failures += 1
                    test_passed = False

                conf_level_sum += resp_contents['conf_level']
                num_tests += 1
                if test_passed:
                    num_passed += 1

    out_file.write(f"""
        {detect_intent_failures} failures to match intent.
        {song_extract_failures} failures to extract song name.
        {adj_extract_failures} failures to extract adjective
        Average intent matching confidence: {float(conf_level_sum)/num_tests}.
        {num_passed}/{num_tests} (passed/total)
    """)

def test_find_song_intent(phrase_formats, songs, out_file):
    """Checks intent, params, and confidence level in Dialogflow request for
    detecting the 'Find Song' intent.
    """
    out_file.write("Testing intent: 'Find Song':\n")
    detect_intent_failures, param_extract_failures = 0, 0
    conf_level_sum, num_tests, num_passed = 0, 0, 0
    for phrase_f in phrase_formats:
        for song in songs:
            test_passed = True
            test_phrase = phrase_f.format(song=song),
            resp_contents = send_detect_intent_req(test_phrase)
            if resp_contents is None:
                print(f"ERROR: could not run test with phrase: '{test_phrase}'")
                continue

            detected_intent = resp_contents['detected_intent']
            if detected_intent != 'Find Song':
                out_file.write(f"- Phrase: {test_phrase}\n")
                out_file.write(f"\tDetected intent:\t '{detected_intent}'\n")
                detect_intent_failures += 1
                test_passed = False

            extracted_song = resp_contents['extracted_params'].get("song", "")
            if extracted_song.upper() != song.upper():
                out_file.write(f"\tSong:\t '{extracted_song}' != '{song}' (expected)\n")
                param_extract_failures += 1
                test_passed = False

            conf_level_sum += resp_contents['conf_level']
            num_tests += 1
            if test_passed:
                num_passed += 1

    out_file.write(f"""
        {detect_intent_failures} failures to match intent.
        {param_extract_failures} failures to extract params.
        Average intent matching confidence: {float(conf_level_sum)/num_tests}.
        {num_passed}/{num_tests} (passed/total)
        ===
    """)

def send_detect_intent_req(phrase):
    """Requests Dialogflow agent to detect intent with given audio data.

    Params:
        phrase (string): e.g. "Play thank u, next".

    Returns:
        (dict): Key fields of response body used for testing. None if request fails.
            e.g. {
                "detected_intent": "Find Slightly Different Song"
                "extracted_params": {
                    "song": "thank you",
                    "audio_feature_adjective": "more acoustic"
                },
                "conf_level": 0.82,
            }
    """
    dialogflow_access_token = run_sh(SH_GENERATE_DIALOGFLOW_ACCESS_TOKEN)
    run_sh(SH_CREATE_AUDIO_FILE.format(phrase))
    b64_encoded_audio = run_sh(SH_B64_ENCODE_AUDIO_FILE)

    resp = requests.post(
        url="https://dialogflow.googleapis.com/v2/projects/muze-2b5fa/agent/sessions/123:detectIntent",
        headers=dict(
            Authorization=f"Bearer {dialogflow_access_token}",
        ),
        json=dict(
            queryInput=dict(
                audioConfig=dict(
                    audioEncoding="AUDIO_ENCODING_LINEAR_16",
                    sampleRateHertz=22050,
                    languageCode="en",
                )
            ),
            inputAudio=b64_encoded_audio,
        ),
    )

    if resp.status_code != 200:
        print(f"ERROR: POST request to Dialogflow failed with status code {resp.status_code}")
        print(f"\t message: {resp.text}")
        return None

    try:
        body = resp.json()
    except Exception as e:
        print(f"ERROR: could not parse response body, {e}: {resp}")
        return None

    remove_file("play_song.wav")

    return dict(
        detected_intent=body['queryResult']['intent']['displayName'],
        extracted_params=body['queryResult']['parameters'],
        conf_level=body['queryResult']['intentDetectionConfidence'],
    )

def remove_file(f):
    try:
        run_sh(f"rm {f}")
    except Exception as e:
        print(f"ERR: could not remove file '{f}': {e}")

def run_sh(cmd):
    res = subprocess.run(cmd.split(" "), capture_output=True)
    return res.stdout.strip().decode('utf-8')

def main():
    try:
        music_api = KnowledgeBaseAPI('knowledge_base/knowledge_base.db')
    except Exception as e:
        print("Couldn't create instance of music api. Probably just need to re-run from root dir.")
        print("Error:", e)
        exit()

    if len(sys.argv) == 2:
        try:
            num_songs = int(sys.argv[1])
        except Exception:
            print("ERR: runtime arg should be an int, but got:", sys.argv[1])
            num_songs = SONG_SET_SIZE
            pass
    else:
        num_songs = SONG_SET_SIZE

    print(f"Running tests with {num_songs} songs...")
    test_songs = random.sample(music_api.get_all_song_names(), num_songs)

    with open("test_find_song.out", "w") as f:
        test_find_song_intent(["Play {song}", "Play song {song}"], test_songs, f)

    with open("test_find_slightly_different_song.out", "w") as f:
        test_phrases = ["Find something like {song} but {adj}", "Play a song like {song} but {adj}"]
        adjectives = [
            # Actual            # Nominal
            ("more acoustic",   "more acoustic"),
            ("happier",         "happier"),
            ("more obscure",    "less popular"),
        ]
        test_find_slightly_different_song_intent(test_phrases, adjectives, test_songs, f)
        f.write(f"Tested phrases: {test_phrases}\n")
        f.write(f"Test adjectives: {[a[0] for a in adjectives]}\n")


if __name__ == "__main__":
    main()

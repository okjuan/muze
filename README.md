## Overview
This is an app for discovering and listening to music:

> Play No One by Alicia Keys

> Play something like No One but more acoustic

> Play something like No One but less popular

> Play something like No One but sadder

The app integrates with:
* Spotify's [Web Playback SDK](https://developer.spotify.com/documentation/web-playback-sdk/) for streaming music and [Web API](https://developer.spotify.com/documentation/web-api/) compiling music metadata
* [Dialogflow](https://dialogflow.com/) to create a natural language user interface

The app consists of:
* A minimal web client that communicates user events to the server and streams music
* A server app that:
    * handles user events from the client
    * communicates with a Dialogflow agent to process raw natural language user input
    * exposes a webhook endpoint for Dialogflow to call during [fulfillment](https://dialogflow.com/docs/fulfillment)
    * contains a music knowledge API that exposes info about musical entities (songs, artists, genres, relationships therein) organized in a semantic network
        * originally developed as part of an another [collaborative project](https://github.com/MIR-Directed-Research/intelligent-music-recommender).

## Setup
### Prerequisites
* [SQLite3](https://www.sqlite.org/download.html)
* [Python](https://www.python.org/downloads/) 3.5 or higher and [pip](https://pypi.org/project/pip/)
* [Spotify premium account](https://www.spotify.com/us/premium/?utm_source=ca-en_brand_contextual_text&utm_medium=paidsearch&utm_campaign=alwayson_ucanz_ca_premiumbusiness_premium_brand+contextual+text+exact+ca-en+google&gclid=CjwKCAjwhbHlBRAMEiwAoDA3450erN_3OgzZ-r-D7byldS_fHtBu9qB4ezr_pEoPDQsepMWP1Q_7NxoCWvEQAvD_BwE&gclsrc=aw.ds) for streaming music

### Dependencies
Whether or not you use a virtual environment:
```
pip install -r requirements.txt
```

## Music Knowledge API
In general, the Knowledge Representation (KR) API exposes a collection of functions that encapsulate all SQL queries and logic relating to managing the database; through the KR API, callers may retrieve from and add information to the database. A detailed description is available in `design_docs/Music Knowledge Base Design Doc.pdf`.

## Testing
### Demoing the Application
This section contains brief instructions for running the app. It is necessary to make the Muze service **publicly available** so that it can communicate with the Dialogflow agent; [ngrok](https://ngrok.com/) is an easy way to relay HTTP messages between the locally running Muze service (e.g. on localhost) and a proxy server.

*NOTE*: A Spotify premium account is necessary to stream music.

#### Local Set Up
* Run the serverside app: `python app/server.py`
* Run `./ngrok http 5000` to connect local server to relay server, making it publicly available
* Copy HTTPS URL on the screen (e.g. `https://f313aea9.ngrok.io`)
* In Dialogflow console, in Fulfillment tab, enable the Webhook option and paste the ngrok HTTPS url with `/webhook` appended to it (e.g. `https://f313aea9.ngrok.io/webhook`)
* Make sure to get a fresh access token for [Spotify](https://developer.spotify.com/documentation/web-playback-sdk/quick-start/#authenticating-with-spotify), and paste them in `client/player.js`; this will be replaced with

#### Using the App
* Navigate to `http://localhost:5000` and enter "Play No One by Alicia Keys".
* The webpage should begin playing "No One" by Alicia Keys.
* In addition to retrieving explicitly given songs, the app is capable of serving fine grained recommendations: enter "Play something like No One but more acoustic".
* The webpage should beging playing "If I Ain't Got You" by Alicia Keys (or perhaps another song)

### Unit Tests
Run the tests from the project's root folder:
```
$ python run_tests.py
...
----------------------------------------------------------------------
Ran 56 tests in 0.943s

OK
```

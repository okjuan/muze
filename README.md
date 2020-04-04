<div>
    <a href="http://muze-player.herokuapp.com/">
    <img style="display: inline-block; margin: 100px" src="./imgs/v0.3-app-screenshot.png" width="1000px" />
    </a>
<!--     <img style="display: inline-block; padding: 10px" src="./imgs/v0.3-app-mobile-screenshot.jpeg" width="100px"/> -->
</div>

## Overview
[Muze Radio](http://muze-player.herokuapp.com/) is a web app for [interactively exploring and listening to music](https://github.com/okjuan/muze/wiki/Project-Motivations). This is its source code repo.

The app integrates with Spotify's [Web Playback SDK](https://developer.spotify.com/documentation/web-playback-sdk/) for streaming music and [Web API](https://developer.spotify.com/documentation/web-api/) for compiling music metadata.

The app consists of:
* A minimal web client that streams music and communicates user events to the server via [web sockets](https://www.fullstackpython.com/websockets.html).
* A server app that contains a music knowledge API exposing info about musical entities (songs, artists, genres, relationships therein) that is internally organized using a [semantic network](https://en.wikipedia.org/wiki/Semantic_network).

## Music Knowledge API
The [Music Knowledge Representation API](./knowledge_base/api.py) exposes a collection of functions that encapsulate all SQL queries and logic relating to managing the database; through the API, callers may retrieve/add information from/to the database. Among other things, the API supports queries such as:
* [Get Artists Metadata](https://github.com/okjuan/muze/blob/145325720dcc2b87ab09fdbf7d5496a76f35c001/knowledge_base/api.py#L289)
* [Get Related Entities](https://github.com/okjuan/muze/blob/145325720dcc2b87ab09fdbf7d5496a76f35c001/knowledge_base/api.py#L145)
* [Are These Two Songs Related?](https://github.com/okjuan/muze/blob/145325720dcc2b87ab09fdbf7d5496a76f35c001/knowledge_base/api.py#L95)

A detailed description is available in [`design_docs/Music Knowledge Base Design Doc.pdf`](https://github.com/okjuan/muze/blob/master/design_docs/Music%20Knowledge%20Base%20Design%20Doc.pdf). This component was originally developed as part of a [distinct, collaborative project](https://github.com/MIR-Directed-Research/intelligent-music-recommender).

## Development
To run the app, you need [SQLite3](https://www.sqlite.org/download.html), [Python](https://www.python.org/downloads/) 3.5 or higher, and [pip](https://pypi.org/project/pip/). To actually use the app, you need a [Spotify premium account](https://www.spotify.com/us/premium/?utm_source=ca-en_brand_contextual_text&utm_medium=paidsearch&utm_campaign=alwayson_ucanz_ca_premiumbusiness_premium_brand+contextual+text+exact+ca-en+google&gclid=CjwKCAjwhbHlBRAMEiwAoDA3450erN_3OgzZ-r-D7byldS_fHtBu9qB4ezr_pEoPDQsepMWP1Q_7NxoCWvEQAvD_BwE&gclsrc=aw.ds) for streaming music.

Install Python packages:
```
$ pip install -r requirements.txt
```

### Running the App Locally
```
$ bash app/run-local.sh
```
The script:
* Temporarily points the client to localhost
* Opens an SSH tunnel to [Serveo](https://serveo.net/) to make the app running locally publicly available

*NOTE*: A Spotify premium account is necessary to stream music.

### Unit Tests
Run the tests from the project's root folder:
```
$ python run_tests.py
...
----------------------------------------------------------------------
Ran 56 tests in 0.943s

OK
```

### Known Issues
Issues, bugs, and impending work are organized in the [GitHub project](https://github.com/okjuan/muze/projects/1). Some issues include:
* API handles ambiguity naively (e.g. if an artist name has multiple matches in the database).
* The app loads only on Chrome browser.

/*
    This script is based on Spotify developers tutorials:
    - https://developer.spotify.com/documentation/web-playback-sdk/quick-start/#
    - https://developer.spotify.com/documentation/web-playback-sdk/reference/#playing-a-spotify-uri

    Sets up Spotify web player and exposes play method to use the player.
*/

const getBearerTokenFromUrl = () => {
    // Adapted from https://glitch.com/edit/#!/spotify-implicit-grant
    // get bearer token
    const hash = window.location.hash
        .substring(1)
        .split('&')
        .reduce(function (initial, item) {
            if (item) {
                var parts = item.split('=');
                initial[parts[0]] = decodeURIComponent(parts[1]);
            }
            return initial;
    }, {});
    window.location.hash = '';  // clean up URL
    return hash.access_token;
}
let bearerToken = getBearerTokenFromUrl(),
    mostRecentTrackUri = undefined,
    player = undefined;

const getBearerToken = () => {
    if (bearerToken !== undefined) {
        return bearerToken;
    }

    const clientId = '90897bcca11f4c78810f7ecadfc0a4ed';
    const redirectUri = 'https://muze-player.herokuapp.com'
    const scopes = ['streaming', 'user-read-playback-state', "user-read-email", "user-read-private"];
    const authEndpoint = `https://accounts.spotify.com/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scopes}&response_type=token&show_dialog=true`;
    // Redirect to Spotify authorization
    window.location = encodeURI(authEndpoint);
}

const updateTrackInfo = (songName, artistName, albumName) => {
    let elem = $("#track-name");
    elem.text(`${songName}`);

    elem = $("#artist-name");
    elem.text(`${artistName}`);

    elem = $("#album-name");
    elem.text(`${albumName}`);
}

const updateAlbumArt = (albumArtUrl, songLink) => {
    let albumArtElem = $('#album-art');
    albumArtElem.attr('src', albumArtUrl);

    let songLinkElem = $('#album-art-link');
    songLinkElem.attr('href', songLink);
}

const showSongMetadataElem = () => {
    $('#music-metadata-container').css('display', 'block');
}

const InitPlayer = () => {
    // Spotify is linked in HTML page
    player = new Spotify.Player({
      name: 'Muze',
      getOAuthToken: cb => { cb(getBearerToken()); }
    });

    player.addListener('initialization_error', ({ message }) => {
        console.error(`Received an initialization error from Spotify player: ${message}`);
    });
    player.addListener('authentication_error', ({ message }) => {
        console.error(`Received an auth'n error from Spotify player: ${message}`);
    });
    player.addListener('account_error', ({ message }) => {
        console.error(`Received an account error from Spotify player: ${message}`);
    });
    player.addListener('playback_error', ({ message }) => {
        console.error(`Received a playback error from Spotify player: ${message}`);
    });

    // Ready
    player.addListener('ready', ({ device_id }) => {
      console.log('Ready with Device ID', device_id);
    });

    // Not Ready
    player.addListener('not_ready', ({ device_id }) => {
      console.log('Device ID has gone offline', device_id);
    });

    // Event https://developer.spotify.com/documentation/web-playback-sdk/reference/#event-player-state-changed
    // Obj. https://developer.spotify.com/documentation/web-playback-sdk/reference/#object-web-playback-state
    player.addListener('player_state_changed', ({ track_window: { current_track } }) => {
        if (current_track !== undefined && current_track['uri'] !== mostRecentTrackUri) {
            updateAlbumArt(
                current_track['album']['images'][0]['url'],
                `https://open.spotify.com/track/${current_track['id']}`
            );
            updateTrackInfo(
                current_track['name'],
                current_track['artists'][0]['name'],
                current_track['album']['name']
            );
            showSongMetadataElem();
            mostRecentTrackUri = current_track['uri'];
        }
    });
};

const GetCurrentSong = () => {
    return player.getCurrentState().then((state) => {
        if (!state) {
            return undefined;
        }
        return {
            spotify_uri: state.track_window.current_track.uri,
            name: state.track_window.current_track.name
        }
    });
}

const PlaySong = (spotify_uri) => {
    if (spotify_uri === undefined) {
        console.log("ERROR: Cannot play song because no spotify URI was specified.");
        return false;
    } else if (player === undefined) {
        console.log("ERROR: Cannot play song because player is not initialized.");
        return false;
    }
    player._options.getOAuthToken(access_token => {
        fetch(`https://api.spotify.com/v1/me/player/play?device_id=${player._options.id}`, {
            method: 'PUT',
            body: JSON.stringify({ uris: [spotify_uri] }),
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${access_token}`
            },
        });
    });
}

const Player = {
    Init: InitPlayer,
    IsConnected: false,
    PlaySong: PlaySong,
    GetCurrentSong: GetCurrentSong
}

Player.Connect = () => {
    // Connect to the player and return promise
    player.connect().then((success) => {
        if (success) {
            console.log("Connected player!");
            Player.IsConnected = true;
        } else {
            console.log("ERROR: could not connect player");
            Player.IsConnected = false;
        }
    });
}

export { Player }

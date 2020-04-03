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
    return !hash.access_token? undefined : hash.access_token;
}
let bearerToken = getBearerTokenFromUrl(),
    mostRecentTrackUri = undefined,
    player = undefined;

const redirectToLogin = ({authEndpointTemplate, clientId, authScopes, redirectUrl}) => {
    // Redirect to Spotify authorization
    window.location = encodeURI(authEndpointTemplate.For({
        clientId: clientId,
        scopes: authScopes,
        redirectUrl: redirectUrl
    }));
}

const Player = {
    IsConnected: false,
    OnReady: () => { console.log("it's ready!!"); },
    _OnReady: ({ device_id }) => {
        console.log('Ready with Device ID', device_id);
        Player.OnReady();
    },
    OnSongChange: ({songName, artistName, albumName, albumArtLink, songLink}) => {
        console.log("Now Playing " + songName + " by " + artistName);
    }
}

Player.Init = () => {
    // Spotify is linked in HTML page
    player = new Spotify.Player({
      name: 'Muze',
      getOAuthToken: cb => { cb(bearerToken); }
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
    player.addListener('ready', Player._OnReady);

    // Not Ready
    player.addListener('not_ready', ({ device_id }) => {
      console.log('Device ID has gone offline', device_id);
    });

    // Event https://developer.spotify.com/documentation/web-playback-sdk/reference/#event-player-state-changed
    // Obj. https://developer.spotify.com/documentation/web-playback-sdk/reference/#object-web-playback-state
    player.addListener('player_state_changed', ({ track_window: { current_track } }) => {
        if (current_track !== undefined && current_track['uri'] !== mostRecentTrackUri) {
            Player.OnSongChange({
                songName: current_track['name'],
                artistName: current_track['artists'][0]['name'],
                albumName: current_track['album']['name'],
                albumArtLink: current_track['album']['images'][0]['url'],
                songLink: `https://open.spotify.com/track/${current_track['id']}`
            })
        }
    });
};

Player.GetCurrentSong = () => {
    if (player === undefined) {
        console.log("ERROR: Cannot get current song because player is not initialized.");
        return undefined;
    } else if (Player.IsConnected == false) {
        console.log("ERROR: Cannot get current song because player is disconnected.");
        return undefined;
    }

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

Player.PlaySong = ({spotify_uri}) => {
    if (spotify_uri === undefined) {
        console.log("ERROR: Cannot play song because no spotify URI was specified.");
        return false;
    } else if (player === undefined) {
        console.log("ERROR: Cannot play song because player is not initialized.");
        return false;
    } else if (Player.IsConnected == false) {
        console.log("ERROR: Cannot play song because player is disconnected.");
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

Player.Connect = ({authEndpointTemplate, clientId, authScopes, redirectUrl, onReady}) => {
    if (Player.IsConnected === true) {
        console.log("Player already connected.");
        onReady();
    }
    if (player === undefined) {
        console.log("ERROR: Cannot get current song because player is not initialized.");
        return;
    }
    if (bearerToken === undefined) {
        console.log("Must log in before the Spotify Player can connect. Redirecting..")
        redirectToLogin({
            authEndpointTemplate: authEndpointTemplate,
            clientId: clientId,
            authScopes: authScopes,
            redirectUrl: redirectUrl
        });
        return;
    }

    Player.OnReady = onReady;
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

const GetPlayer = () => {
    return Player
}

export { GetPlayer }

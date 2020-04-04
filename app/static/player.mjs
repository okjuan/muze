let mostRecentTrackUri = undefined, player = undefined;
const Player = {
    IsConnected: false,
    OnReady: ({ device_id }) => {
        console.log('Ready with Device ID', device_id);
    },
    OnSongChange: ({songName, artistName, albumName, albumArtLink, songLink}) => {
        console.log("Now Playing " + songName + " by " + artistName);
    },
    BearerToken: undefined
}

Player.Init = () => {
    if (Player.BearerToken === undefined) {
        console.log("ERROR: Cannot initialize Player without bearer token.")
        return;
    }

    player = new Spotify.Player({
      name: 'Muze Radio',
      getOAuthToken: cb => { cb(Player.BearerToken); }
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

    player.addListener('ready', Player.OnReady);

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

    player.connect().then((success) => {
        if (success) {
            console.log("Connected player!");
            Player.IsConnected = true;
        } else {
            console.log("ERROR: could not connect player");
            Player.IsConnected = false;
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
    return fetch(`https://api.spotify.com/v1/me/player/play?device_id=${player._options.id}`, {
        method: 'PUT',
        body: JSON.stringify({ uris: [spotify_uri] }),
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${Player.BearerToken}`
        },
    });
}

export { Player }

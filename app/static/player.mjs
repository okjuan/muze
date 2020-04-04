import { Utils } from './utils.mjs'

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
    Utils.ThrowIfNullOrUndefined(Player.BearerToken);
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
    ThrowIfNullOrUndefined(player);
    if (Player.IsConnected == false) {
        throw new Error("Cannot get current song because player is disconnected.");
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
    Utils.ThrowIfNullOrUndefined(spotify_uri);
    Utils.ThrowIfNullOrUndefined(player);
    if (Player.IsConnected == false) {
        throw new Error("Cannot play song because player is disconnected.");
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

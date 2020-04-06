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

Player.Init = async () => {
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

    player.addListener('player_state_changed', ({ track_window: { current_track } }) => {
        if (current_track !== undefined && current_track['uri'] !== mostRecentTrackUri) {
            Player.OnSongChange({
                songName: current_track['name'],
                artistName: current_track['artists'][0]['name'],
                albumName: current_track['album']['name'],
                albumArtLink: current_track['album']['images'][0]['url'],
                songLink: Player.TrackLink.For({trackUri: current_track['id']})
            })
        }
    });

    try {
        var success = await player.connect();
    } catch (err) {
        Player.IsConnected = false;
        throw new Error("ERROR: could not connect player");
    } finally {
        if (success) {
            console.log("Connected player!");
            Player.IsConnected = success;
        } else {
            Player.IsConnected = false;
            throw new Error("ERROR: could not connect player");
        }
    }
};

Player.GetCurrentSong = async () => {
    Utils.ThrowIfNullOrUndefined(player);
    if (Player.IsConnected == false) {
        throw new Error("Cannot get current song because player is disconnected.");
    }
    var state = await player.getCurrentState();
    if (!state) {
        throw new Error("Couldn't get current song because player's state was undefined.");
    }
    return {
        spotifyUri: state.track_window.current_track.uri,
        songName: state.track_window.current_track.name
    };
}

Player.PlaySong = ({spotify_uri}) => {
    Utils.ThrowIfNullOrUndefined(spotify_uri);
    Utils.ThrowIfNullOrUndefined(player);
    if (Player.IsConnected == false) {
        throw new Error("Cannot play song because player is disconnected.");
    }
    return fetch(Player.PlayEndpoint.For({deviceId: player._options.id}), {
        method: 'PUT',
        body: JSON.stringify({ uris: [spotify_uri] }),
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${Player.BearerToken}`
        },
    });
}

export { Player }

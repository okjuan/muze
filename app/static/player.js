/*
    This script is based on Spotify developers tutorials:
    - https://developer.spotify.com/documentation/web-playback-sdk/quick-start/#
    - https://developer.spotify.com/documentation/web-playback-sdk/reference/#playing-a-spotify-uri

    Sets up Spotify web player and exposes play method to use the player.
*/

// =====
// Adapted from https://glitch.com/edit/#!/spotify-implicit-grant
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
window.location.hash = '';

let bearer_token = hash.access_token;

const authEndpoint = 'https://accounts.spotify.com/authorize';
const clientId = '90897bcca11f4c78810f7ecadfc0a4ed';
const redirectUri = 'https://muze.serveo.net'
const scopes = ['streaming'];

// If there is no token, redirect to Spotify authorization
if (!bearer_token) {
    window.location = encodeURI(`${authEndpoint}?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scopes}&response_type=token&show_dialog=true`);
}
// =====

var player = undefined;
window.onSpotifyWebPlaybackSDKReady = () => {
    // Spotify is linked in HTML page
    player = new Spotify.Player({
      name: 'Muze',
      getOAuthToken: cb => { cb(bearer_token); }
    });

    // Error handling
    player.addListener('initialization_error', ({ message }) => { console.error(message); });
    player.addListener('authentication_error', ({ message }) => { console.error(message); });
    player.addListener('account_error', ({ message }) => { console.error(message); });
    player.addListener('playback_error', ({ message }) => { console.error(message); });

    // Playback status updates
    player.addListener('player_state_changed', state => { console.log(state); });

    // Ready
    player.addListener('ready', ({ device_id }) => {
      console.log('Ready with Device ID', device_id);
    });

    // Not Ready
    player.addListener('not_ready', ({ device_id }) => {
      console.log('Device ID has gone offline', device_id);
    });

    // Connect to the player!
    player.connect().then(success => {
        if (success) {
          console.log('The Web Playback SDK successfully connected to Spotify!');
        } else {
            console.log('Uh oh! Could not connect player');
        }
      });
  };

// Gets access token and plays a track
const play = ({
    spotify_uri,
    // pick out the existing fields in the Spotify player the we wanna use
    playerInstance: {
        _options: {
            getOAuthToken,
            id
        }
    }
}) => {
    getOAuthToken(access_token => {
        fetch(`https://api.spotify.com/v1/me/player/play?device_id=${id}`, {
            method: 'PUT',
            body: JSON.stringify({ uris: [spotify_uri] }),
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${access_token}`
            },
        });
    });
};

const playSong = (spotify_uri) => {
    if (spotify_uri === undefined) {
        // Run Away With Me by Carly Rae Jepsen
        spotify_uri = 'spotify:track:7xGfFoTpQ2E7fRF5lN10tr';
    }
    if (player !== undefined) {
        play({
            playerInstance: player,
            spotify_uri: spotify_uri,
        });
    } else {
        console.log("Waiting for player to load...");
    }
}
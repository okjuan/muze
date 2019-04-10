/*
    This script is based on Spotify developers tutorials:
    - https://developer.spotify.com/documentation/web-playback-sdk/quick-start/#
    - https://developer.spotify.com/documentation/web-playback-sdk/reference/#playing-a-spotify-uri

    Sets up Spotify web player and exposes play method to use the player.
*/

var player = undefined;

window.onSpotifyWebPlaybackSDKReady = () => {
    // for prototyping phase, getting the bearer token manually is sufficient
    const token = 'BQCNuoy4qhEwi2NasH5-_-4OFY1iAzJWz0ucasTRG5yirQyoT3IGoRP-vL2lbWebvHKEfIKyVmpn9HtsZswj3Ld5XITgyvavs9UKNs7XUIwc444zTy5WbZK1vuJcrrBw1_61dmP3IesBiNIZcEfC4Zt-waypvrDWPWK8WA';
    // Spotify is linked in HTML page
    player = new Spotify.Player({
      name: 'Muze',
      getOAuthToken: cb => { cb(token); }
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
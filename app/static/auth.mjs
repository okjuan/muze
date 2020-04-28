/*
    This script is based on Spotify developers tutorials:
    - https://developer.spotify.com/documentation/web-playback-sdk/quick-start/#
    - https://developer.spotify.com/documentation/web-playback-sdk/reference/#playing-a-spotify-uri

    Sets up Spotify web player.
*/

const SpotifyAuth = {
    GetBearerTokenFromUrl: () => {
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
    },

    RedirectToLogin: ({authEndpointTemplate, clientId, authScopes, redirectUrl}) => {
        // Redirect to Spotify authorization
        window.location = encodeURI(authEndpointTemplate.For({
            clientId: clientId,
            scopes: authScopes,
            redirectUrl: redirectUrl
        }));
    }
}

export { SpotifyAuth }
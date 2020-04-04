import { Utils } from './utils.mjs'

const SpotifyConfig = {
    Auth: {
        ClientId: "90897bcca11f4c78810f7ecadfc0a4ed",
        Scopes: ["streaming", "user-read-playback-state", "user-read-email", "user-read-private", "playlist-modify-public"]
    },
    EndpointTemplates: {
        AuthToken: {
            For: ({clientId, scopes, redirectUrl}) => `https://accounts.spotify.com/authorize?client_id=${clientId}&redirect_uri=${redirectUrl}&scope=${scopes}&response_type=token&show_dialog=true`
        },
        AddTracksToPlaylist: {
            For: ({playlistId, trackUris}) => {
                Utils.ThrowIfNullOrUndefined(playlistId);
                Utils.ThrowIfNullOrUndefinedOrEmpty(trackUris);
                return `https://api.spotify.com/v1/playlists/${playlistId}/tracks?uris=${encodeURIComponent(trackUris.join(','))}`
            }
        }
    }
}

const AppConfig = {
    AppIndexUrl: 'https://muze-player.herokuapp.com'
}

export { AppConfig, SpotifyConfig }

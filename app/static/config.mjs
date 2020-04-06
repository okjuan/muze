import { Utils } from './utils.mjs'

const SpotifyConfig = {
    Auth: {
        ClientId: "90897bcca11f4c78810f7ecadfc0a4ed",
        Scopes: ["streaming", "user-read-playback-state", "user-read-email", "user-read-private", "playlist-modify-public"]
    },
    EndpointTemplates: {
        AddTracksToPlaylist: {
            For: ({playlistId, trackUris}) => {
                Utils.ThrowIfNullOrUndefined(playlistId);
                Utils.ThrowIfNullOrUndefinedOrEmpty(trackUris);
                return `https://api.spotify.com/v1/playlists/${playlistId}/tracks?uris=${encodeURIComponent(trackUris.join(','))}`
            }
        },
        AuthToken: {
            For: ({clientId, scopes, redirectUrl}) => {
                Utils.ThrowIfNullOrUndefined(clientId);
                Utils.ThrowIfNullOrUndefinedOrEmpty(scopes);
                Utils.ThrowIfNullOrUndefined(redirectUrl);
                return `https://accounts.spotify.com/authorize?client_id=${clientId}&redirect_uri=${redirectUrl}&scope=${scopes}&response_type=token&show_dialog=true`;
            }
        },
        PlaySong: {
            For: ({deviceId}) => {
                Utils.ThrowIfNullOrUndefined(deviceId);
                return `https://api.spotify.com/v1/me/player/play?device_id=${deviceId}`;
            }
        },
        TrackLink: {
            For: ({trackUri}) => {
                Utils.ThrowIfNullOrUndefined(trackUri);
                return `https://open.spotify.com/track/${trackUri}`;
            }
        }
    }
}

const AppConfig = {
    AppIndexUrl: 'https://muze-player.herokuapp.com'
}

export { AppConfig, SpotifyConfig }

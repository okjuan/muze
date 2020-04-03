const SpotifyConfig = {
    Auth: {
        ClientId: "90897bcca11f4c78810f7ecadfc0a4ed",
        Scopes: ["streaming", "user-read-playback-state", "user-read-email", "user-read-private"]
    },
    EndpointTemplates: {
        AuthToken: {
            For: ({clientId, scopes, redirectUrl}) => `https://accounts.spotify.com/authorize?client_id=${clientId}&redirect_uri=${redirectUrl}&scope=${scopes}&response_type=token&show_dialog=true`
        },
        AddTracksToPlaylist: {
            For: ({playlistId, trackUris}) => {
                if (playlistId === undefined) {
                    console.log(`ERROR: playlistId must be defined, but found ${playlistId}.`)
                    return;
                }
                if (trackUris === undefined || trackUris === []) {
                    console.log(`ERROR: need array of one or more trackUris but found ${trackUris}.`)
                    return;
                }
                return `https://api.spotify.com/v1/playlists/${playlistId}/tracks?${trackUris.join(',')}`
            }
        }
    }
}

const AppConfig = {
    AppIndexUrl: 'https://muze-player.herokuapp.com'
}

export { AppConfig, SpotifyConfig }

const SpotifyConfig = {
    EndpointTemplates: {
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

export { SpotifyConfig }
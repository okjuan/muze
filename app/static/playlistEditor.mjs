const PlaylistEditor = {
    urlTemplateForAddingTracksToPlaylist: undefined,
    bearerToken: undefined,
    AddSong: ({spotifyPlaylistId, spotifyTrackUri}) => {
        if (PlaylistEditor.urlTemplateForAddingTracksToPlaylist === undefined) {
            console.log("ERROR: HTTP endpoint for adding songs playlist not initialized.");
            console.log(`Aborting request to add '${spotifyTrackUri}' to playlist with ID: '${spotifyPlaylistId}'.`);
            return;
        }
        if (PlaylistEditor.bearerToken === undefined) {
            console.log("ERROR: bearer token not initialized in PlaylistEditor.");
            console.log(`Aborting request to add '${spotifyTrackUri}' to playlist with ID: '${spotifyPlaylistId}'.`);
            return;
        }
        let endpoint = PlaylistEditor.urlTemplateForAddingTracksToPlaylist.For({
            playlistId: spotifyPlaylistId, trackUris: [spotifyTrackUri]
        });
        fetch(endpoint, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${PlaylistEditor.bearerToken}`,
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        }).catch((err) => {
            console.log(`ERROR: Could not add song to playlist '${spotifyTrackUri}' to playlist with ID: '${spotifyPlaylistId}' with error: ${err}`)
        });
    }
};

const GetPlaylistEditor = ({urlTemplateForAddingTracksToPlaylist, bearerToken}) => {
    PlaylistEditor.urlTemplateForAddingTracksToPlaylist = urlTemplateForAddingTracksToPlaylist;
    PlaylistEditor.bearerToken = bearerToken;
    return PlaylistEditor;
};

export { GetPlaylistEditor };
const PlaylistEditor = {
    urlTemplateForAddingTracksToPlaylist: undefined,
    AddSong: ({spotifyPlaylistId, spotifyTrackUri}) => {
        if (PlaylistEditor.urlTemplateForAddingTracksToPlaylist === undefined) {
            console.log("ERROR: HTTP endpoint for adding songs playlist not initialized.");
            console.log(`Aborting request to add '${spotifyTrackUri}' to playlist with ID: '${spotifyPlaylistId}'.`);
            return;
        }
        console.log("Gonna do it!!! I swear!");
        console.log("Spotify Playlist Id: " + spotifyPlaylistId);
        console.log("Spotify Track URIs: " + spotifyTrackUri);
        console.log("Will call: " + PlaylistEditor.urlTemplateForAddingTracksToPlaylist.For({
            playlistId: spotifyPlaylistId, trackUris: [spotifyTrackUri]
        }));
    }
};

const GetPlaylistEditor = ({urlTemplateForAddingTracksToPlaylist}) => {
    PlaylistEditor.urlTemplateForAddingTracksToPlaylist = urlTemplateForAddingTracksToPlaylist;
    return PlaylistEditor;
};

export { GetPlaylistEditor };
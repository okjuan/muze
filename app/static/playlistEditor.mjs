import { Utils } from './utils.mjs'

const PlaylistEditor = {
    urlTemplateForAddingTracksToPlaylist: undefined,
    bearerToken: undefined,
    AddSong: async ({spotifyPlaylistId, spotifyTrackUri}) => {
        Utils.ThrowIfNullOrUndefined(PlaylistEditor.urlTemplateForAddingTracksToPlaylist);
        Utils.ThrowIfNullOrUndefined(PlaylistEditor.bearerToken);
        let endpoint = PlaylistEditor.urlTemplateForAddingTracksToPlaylist.For({
            playlistId: spotifyPlaylistId, trackUris: [spotifyTrackUri]
        });
        try {
            var response = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${PlaylistEditor.bearerToken}`,
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
            });
        } catch (err) {
            console.log(`ERROR: Could not add song to playlist '${spotifyTrackUri}' to playlist with ID: '${spotifyPlaylistId}' with error: ${err}`);
            return false;
        }
        return response.ok;
    }
};

const GetPlaylistEditor = ({urlTemplateForAddingTracksToPlaylist, bearerToken}) => {
    PlaylistEditor.urlTemplateForAddingTracksToPlaylist = urlTemplateForAddingTracksToPlaylist;
    PlaylistEditor.bearerToken = bearerToken;
    return PlaylistEditor;
};

export { GetPlaylistEditor };
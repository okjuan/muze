import { AppConfig, SpotifyConfig } from './config.mjs'
import { SpotifyAuthHelper } from './auth.mjs'
import { GetPlaylistEditor } from './playlistEditor.mjs'
import { Player } from './player.mjs'
import { View } from './view.mjs'


let bearerToken = SpotifyAuthHelper.GetBearerTokenFromUrl();
Player.BearerToken = bearerToken;
Player.TrackLink = SpotifyConfig.EndpointTemplates.TrackLink;
Player.PlayEndpoint = SpotifyConfig.EndpointTemplates.PlaySong;
window.onSpotifyWebPlaybackSDKReady = Player.Init;

View.OnReady(() => {
    View.PresentSinglePlayButton({ clickHandler: () => {
        if (bearerToken === undefined) {
            SpotifyAuthHelper.RedirectToLogin({
                authEndpointTemplate: SpotifyConfig.EndpointTemplates.AuthToken,
                clientId: SpotifyConfig.Auth.ClientId,
                authScopes: SpotifyConfig.Auth.Scopes,
                redirectUrl: AppConfig.AppIndexUrl
            });
        } else {
            socket.emit('get random song');
        }
    }});
})

const PlaylistEditor = GetPlaylistEditor({
    urlTemplateForAddingTracksToPlaylist: SpotifyConfig.EndpointTemplates.AddTracksToPlaylist,
    bearerToken: bearerToken
});

const State = {
    Streaming: false
};

var socket = io.connect(AppConfig.AppIndexUrl);
socket.on('connect', () => {
    socket.emit('start session');
});

socket.on('play song', async (data) => {
    try {
        await Player.PlaySong({spotify_uri: data['spotify_uri']});
    } catch (err) {
        // TODO: send err as telemetry
        socket.emit ("get random song");
        return;
    }
    if (State.Streaming == false) {
        // TODO: confirm that indeed there is a song playing BEFORE presenting options
        // - surely I should be checking something like Player.IsPlaying?
        View.PresentRecommendationControls({
            recommendationHandler: recommendationHandler,
            randomSongHandler: () => socket.emit("get random song"),
        });
        View.PresentPlaylistEditorControls({addSongHandler: addSongHandler});
    }
    State.Streaming = true;

    // code smell: is it really necessary to expose this method? couldn't we instead
    //             update the state when the View updates?
    View.SetState({ loading: false }); // code smell!!!
});

socket.on('msg', (msgStr) => {
    View.SetState({ loading: false }); // code smell!!!
    View.PresentMessage(msgStr);
});

Player.OnSongChange = ({ songName, artistName, albumName, albumArtLink, songLink }) => {
    View.UpdateCurrentlyPlaying({
        song: { name: songName, link: songLink },
        artist: { name: artistName },
        album: { name: albumName, coverLink: albumArtLink }
    })
};

const recommendationHandler = async ({recommendType}) => {
    try {
        var {spotifyUri, songName } = await Player.GetCurrentSong();
    } catch (err) {
        // TODO: send err as telemetry
        View.PresentMessage("I... can't think of anything right now. Ask me again later :~)");
    }
    socket.emit('get recommendation', {
        'song': songName,
        'spotify_uri': spotifyUri,
        'adjective': recommendType
    });
}

const addSongHandler = async () => {
    try {
        var {spotifyUri, songName} = await Player.GetCurrentSong();
    } catch (err) {
        View.PresentMessage(`Sorry, couldn't add '${songName}' to your playlist.`);
        return;
    }

    try {
        var success = await PlaylistEditor.AddSong({
            spotifyPlaylistId: "5EBSl6dF8hzu9KE0IYxM21",
            spotifyTrackUri: spotifyUri,
        });
    } catch (err) {
        // TODO: send err as telemetry
        View.PresentMessage(`Sorry, couldn't add '${songName}' to your playlist.`)
        return;
    }

    if (success) {
        View.PresentMessage(`Added '${songName}' to your playlist!`);
    } else {
        View.PresentMessage(`Sorry, couldn't add '${songName}' to your playlist.`)
    }
    View.SetState({ loading: false }); // code smell!!!
};

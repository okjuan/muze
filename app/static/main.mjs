import { AppConfig, SpotifyConfig } from './config.mjs'
import { SpotifyAuth } from './auth.mjs'
import { GetPlaylistEditor } from './playlistEditor.mjs'
import { Player } from './player.mjs'
import { View } from './view.mjs'


const State = {
    BearerToken: SpotifyAuth.GetBearerTokenFromUrl(),
    SongQueue: [],
    WaitingForNewSong: true
};

Player.BearerToken = State.BearerToken;
Player.TrackLink = SpotifyConfig.EndpointTemplates.TrackLink;
Player.PlayEndpoint = SpotifyConfig.EndpointTemplates.PlaySong;

Player.OnSongChange = ({songName, artistName, albumName, albumArtLink, songLink}) => {
    View.UpdateCurrentlyPlaying({
        song: { name: songName, link: songLink },
        artist: { name: artistName },
        album: { name: albumName, coverLink: albumArtLink }
    });
};

Player.OnSongEnd = async () => {
    if (State.SongQueue.length > 0) {
        playSong(State.SongQueue.shift());
    }
}

window.onSpotifyWebPlaybackSDKReady = Player.Init;

View.OnReady(() => {
    View.PresentSinglePlayButton({ clickHandler: () => {
        if (State.BearerToken === undefined) {
            SpotifyAuth.RedirectToLogin({
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
    bearerToken: State.BearerToken
});

var socket = io.connect(AppConfig.AppIndexUrl);
socket.on('connect', () => {
    socket.emit('start session');
});

socket.on('new song', async (data) => {
    let spotifyUris = data['spotify_uris'];
    if (spotifyUris.length === 0) {
        View.PresentMessage("Could not get recommendations :(");
    }
    if (State.WaitingForNewSong) {
        State.WaitingForNewSong = false;
        playSong(spotifyUris[0]);
        spotifyUris = spotifyUris.slice(1);
    }
    State.SongQueue.push(...spotifyUris);
    // code smell!!!
    View.SetState({ loading: false });
});

socket.on('msg', (msgStr) => {
    // code smell!!!
    View.SetState({ loading: false });
    View.PresentMessage(msgStr);
});

const playSong = async (spotifyUri) => {
    try {
        await Player.PlaySong({spotify_uri: spotifyUri});
    } catch (err) {
        // TODO: send err as telemetry
        View.PresentMessage("Couldn't play song :( Please try again later");
        return;
    }
    if (View.ShowingRecommendationButtons === false) {
        // TODO: confirm that indeed there is a song playing BEFORE presenting options
        // - surely I should be checking something like Player.IsPlaying?
        showPlayerControls();
    }
}

const showPlayerControls = async () => {
    View.PresentRecommendationControls({
        recommendationHandler: recommendationHandler,
        randomSongHandler: randomSongHandler,
    });
    View.PresentPlaylistEditorControls({addSongHandler: addSongHandler});

    // code smell: is it really necessary to expose this method? couldn't we instead
    //             update the state when the View updates?
    View.SetState({ loading: false });
}

const randomSongHandler = () => {
    State.SongQueue = [];
    State.WaitingForNewSong = true;
    socket.emit("get random song");
}

const recommendationHandler = async ({recommendType}) => {
    try {
        var {spotifyUri, songName } = await Player.GetCurrentSong();
    } catch (err) {
        // TODO: send err as telemetry
        View.PresentMessage("I... can't think of anything right now. Ask me again later :~)");
    }
    State.SongQueue = [];
    State.WaitingForNewSong = true
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

    // code smell!!!
    View.SetState({ loading: false });
};
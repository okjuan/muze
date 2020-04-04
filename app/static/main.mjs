import { AppConfig, SpotifyConfig } from './config.mjs'
import { SpotifyAuthHelper } from './auth.mjs'
import { GetPlaylistEditor } from './playlistEditor.mjs'
import { Player } from './player.mjs'
import { View } from './view.mjs'

let bearerToken = SpotifyAuthHelper.GetBearerTokenFromUrl();
if (bearerToken === undefined) {
  SpotifyAuthHelper.RedirectToLogin({
    authEndpointTemplate: SpotifyConfig.authEndpointTemplate,
    clientId: SpotifyConfig.Auth.ClientId,
    authScopes: SpotifyConfig.Auth.Scopes,
    redirectUrl: AppConfig.AppIndexUrl
  });
}
Player.BearerToken = bearerToken;

window.onSpotifyWebPlaybackSDKReady = Player.Init;

View.OnReady(() => {
  View.PresentSinglePlayButton({clickHandler: () => socket.emit('get random song')});
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
  View.SetState({loading: false}); // code smell!!!
});

socket.on('msg', (msgStr) => {
  View.SetState({loading: false}); // code smell!!!
  View.PresentMessage(msgStr);
});

Player.OnSongChange = ({songName, artistName, albumName, albumArtLink, songLink}) => {
  View.UpdateCurrentlyPlaying({
    song: {name: songName, link: songLink},
    artist: {name: artistName},
    album: {name: albumName, coverLink: albumArtLink}
  })
};

const recommendationHandler = ({recommendType}) => {
  try {
    Player.GetCurrentSong().then(({spotify_uri, name}) => {
      // TODO: handle case where Promise does not resolve nicely
      socket.emit('get recommendation', {
        'song': name,
        'spotify_uri': spotify_uri,
        'adjective': recommendType
      });
    });
  } catch (err) {
    // TODO: send err as telemetry
    View.PresentMessage("I... can't think of anything right now. Ask me again later :~)");
  }
}

const addSongHandler = () => {
  try {
    Player.GetCurrentSong().then(({spotify_uri, name}) => {
      // TODO: handle case where Promise does not resolve nicely
      try {
        PlaylistEditor.AddSong({
          // TODO: parametrize. (placeholder: 'fizz buzz tangle' by jcgalleg)
          spotifyPlaylistId: "2ZjWb4BpsCMNX22waSfNuq",
          spotifyTrackUri: spotify_uri,
        });
        View.PresentMessage(`Added '${name}' to your playlist!`)
      } catch (err) {
        // TODO: send err as telemetry
        View.PresentMessage(`Sorry, couldn't add '${name}' to your playlist.`)
      } finally {
        View.SetState({loading: false}); // code smell!!!
      }
    });
  } catch (err) {
    // TODO: send err as telemetry
    View.PresentMessage(`Sorry, couldn't add '${name}' to your playlist.`)
  }
};

import { AppConfig, SpotifyConfig } from './config.mjs'
import { GetPlayer } from './player.mjs'
import { GetPlaylistEditor } from './playlistEditor.mjs'
import { View } from './view.mjs'

const State = {
  Playing: false
};

const Player = GetPlayer();
const PlaylistEditor = GetPlaylistEditor({
  urlTemplateForAddingTracksToPlaylist: SpotifyConfig.EndpointTemplates.AddTracksToPlaylist
});

Player.OnSongChange = ({songName, artistName, albumName, albumArtLink, songLink}) => {
  View.UpdateCurrentlyPlaying({
    song: {name: songName, link: songLink},
    artist: {name: artistName},
    album: {name: albumName, coverLink: albumArtLink}
  })
};

window.onSpotifyWebPlaybackSDKReady = Player.Init;

var socket = io.connect(AppConfig.AppIndexUrl);
socket.on('connect', () => {
  socket.emit('start session');
});

socket.on('play song', (data) => {
  if (State.Playing == false) {
    // TODO: confirm that indeed there is a song playing BEFORE presenting options
    // - surely I should be checking something like Player.IsPlaying?
    View.PresentRecommendationControls({
      recommendationHandler: recommendationHandler,
      randomSongHandler: () => socket.emit("get random song"),
    });
    View.PresentPlaylistEditorControls({addSongHandler: addSongHandler});
  }
  Player.PlaySong({spotify_uri: data['spotify_uri']});
  State.Playing = true;

  // code smell: is it really necessary to expose this method? couldn't we instead
  //             update the state when the View updates?
  View.SetState({loading: false}); // code smell!!!
});

socket.on('msg', (msgStr) => {
  View.SetState({loading: false}); // code smell!!!
  // TODO: present messages in a user-friendly manner
  alert(msgStr);
});

const recommendationHandler = ({recommendType}) => {
  Player.GetCurrentSong().then(({spotify_uri, name}) => {
    // TODO: handle case where Promise does not resolve nicely
    socket.emit('get recommendation', {
      'song': name,
      'spotify_uri': spotify_uri,
      'adjective': recommendType
    });
  });
}

const addSongHandler = () => {
  Player.GetCurrentSong().then(({spotify_uri, name}) => {
    // TODO: handle case where Promise does not resolve nicely
    PlaylistEditor.AddSong({
      // TODO: parametrize. (placeholder: 'fizz buzz tangle' by jcgalleg)
      spotifyPlaylistId: "2ZjWb4BpsCMNX22waSfNuq",
      spotifyTrackUri: spotify_uri,
    });
    View.SetState({loading: false}); // code smell!!!
  });
};

View.OnReady(() => {
  View.PresentSinglePlayButton({
    clickHandler: () => {
      Player.Connect({
        authEndpointTemplate: SpotifyConfig.EndpointTemplates.AuthToken,
        clientId: SpotifyConfig.Auth.ClientId,
        authScopes: SpotifyConfig.Auth.Scopes,
        redirectUrl: AppConfig.AppIndexUrl,
        onReady: () => { socket.emit('get random song') }
      })
    }
  });
})

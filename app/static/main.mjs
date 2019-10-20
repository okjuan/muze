// Author: Juan Carlos Gallegos.

import { GetPlayer } from './player.mjs'
import { View } from './view.mjs'

const State = {
  Playing: false
}

const Player = GetPlayer(({songName, artistName, albumName, albumArtLink, songLink}) => {
  View.UpdateCurrentlyPlaying({
    song: {name: songName, link: songLink},
    artist: {name: artistName},
    album: {name: albumName, coverLink: albumArtLink}
  })
});

window.onSpotifyWebPlaybackSDKReady = Player.Init;

var socket = io.connect('https://muze-player.herokuapp.com');
socket.on('connect', () => {
  socket.emit('start session');
});

socket.on('play song', (data) => {
  if (State.Playing == false) {
    // TODO: confirm that indeed there is a song playing BEFORE presenting options
    View.PresentRecommendationControls(recommendationHandler, () => socket.emit("get random song"));
  }
  Player.PlaySong(data['spotify_uri']);
  State.Playing = true;
  View.SetState({loading: false});
});

const recommendationHandler = (recommendType) => {
  Player.GetCurrentSong().then(({spotify_uri, name}) => {
    // TODO: handle case where Promise does not resolve nicely
    socket.emit('get recommendation', {
      'song': name,
      'spotify_uri': spotify_uri,
      'adjective': recommendType
    });
  });
}

socket.on('msg', (msgStr) => {
  View.SetState({loading: false});
  // TODO: present messages in a user-friendly manner
  alert(msgStr);
})

View.OnReady(() => {
  View.PresentSinglePlayButton(() => {
    Player.Connect(() => {
      socket.emit('get random song');
    })
  });
})

// Author: Juan Carlos Gallegos.

var socket = io.connect('https://muze-player.herokuapp.com');
socket.on('connect', () => {
  socket.emit('start session');
});

socket.on('session key', (data) => {
  sessionKey = data['session_key'];
});

socket.on('play song', (data) => {
  playSong(data['spotify_uri']);
});

$(document).ready(() => {
  $('#random-song').on('click', () => {
    console.log("Getting a random song!");
    socket.emit('get random song');
  });
});

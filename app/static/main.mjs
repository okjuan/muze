// Author: Juan Carlos Gallegos.

import { GetPlayer } from './player.mjs'

const Player = GetPlayer(({songName, artistName, albumName, albumArtLink, songLink}) => {
  let elem = $("#track-name");
  elem.text(`${songName}`);

  elem = $("#artist-name");
  elem.text(`${artistName}`);

  elem = $("#album-name");
  elem.text(`${albumName}`);

  let albumArtElem = $('#album-art');
  albumArtElem.attr('src', albumArtLink);

  let songLinkElem = $('#album-art-link');
  songLinkElem.attr('href', songLink);

  $('#music-metadata-container').css('display', 'block');
});

window.onSpotifyWebPlaybackSDKReady = Player.Init;

var socket = io.connect('https://muze-player.herokuapp.com');
socket.on('connect', () => {
  socket.emit('start session');
});

socket.on('play song', (data) => {
  Player.PlaySong(data['spotify_uri']);
  $('.loading').removeClass('loading');
  // TODO: confirm that indeed there is a song playing BEFORE presenting options
  presentRecommendationOptions();
});

// TODO: present messages in a user-friendly manner
socket.on('msg', (msgStr) => {
  $('.loading').removeClass('loading');
  alert(msgStr);
})

$(document).ready(() => {
  $('#random-song').on('click', () => {
    Player.Connect(() => {
      socket.emit('get random song');
      $('#random-song').addClass('loading');
    });
  });
});

const presentRecommendationOptions = () => {
  let randSongBtn = $('#random-song');
  if (randSongBtn.length === 0) {
    return;
  }
  randSongBtn.hide('slow', () => {
    randSongBtn.after(getRecommendationButtons());
    randSongBtn.remove();
  });
}

const setElemClass = (id, cssClass) => {
  $('#'+id).addClass(cssClass);
}

const getRecommendationButtons = () => {
  let recommendationButtons = [];
  for (let btn of [
    {adj: undefined,        title: 'More like this',         id: 'similar-rec-btn'},
    {adj: 'less acoustic',  title: 'More electric!',         id: 'more-electric-rec-btn'},
    {adj: 'more acoustic',  title: 'No, more acoustic',      id: 'more-acoustic-rec-btn'},
    {adj: 'less popular',   title: 'Actually, more obscure', id: 'more-obscure-rec-btn'},
    {adj: 'more popular',   title: 'More mainstream please', id: 'more-popular-rec-btn'},
    {adj: 'happier',        title: 'Damn, cheer up',         id: 'happier-rec-btn'},
    {adj: 'sadder',         title: 'Make it sad :(',         id: 'sadder-rec-btn'},
    {adj: 'dancier',        title: 'I wanna dance to it!',   id: 'dancier-rec-btn'},
  ]) {
    recommendationButtons.push($('<button></button>')
      .attr('id', btn.id)
      .addClass("btn btn-primary btn-sm m-2")
      .text(btn.title)
      .on('click', () => {
        setElemClass(btn.id, 'loading');
        Player.GetCurrentSong().then(({spotify_uri, name}) => {
          // TODO: handle case where Promise does not resolve nicely
          socket.emit('get recommendation', {
            'song': name,
            'spotify_uri': spotify_uri,
            'adjective': btn.adj
          });
        });
      })
    );
  }
  recommendationButtons.push($('<button></button>')
    .attr('id', 'random-rec-btn')
    .addClass("btn btn-sm m-2")
    .text("Just random!")
    .on('click', () => { socket.emit('get random song'); })
  );
  return recommendationButtons;
};

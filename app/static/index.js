/*
  Original Author: Patrick Catanzariti
  Original Source Code: https://github.com/sitepoint-editors/Api-AI-Personal-Assistant-Demo
  Original Tutorial: https://www.sitepoint.com/how-to-build-your-own-ai-assistant-using-api-ai/

  Edited by Juan Carlos Gallegos.

  * It accepts user input and sends to server via websockets
  * Plays Spotify song if included server's response
*/

var socket = io.connect('https://muze-player.herokuapp.com');
socket.on('connect', () => {
  socket.emit('start session');
});

socket.on('session key', (data) => {
  sessionKey = data['session_key'];
});

socket.on('play song', (data) => {
  respond('Aha!', data['msg'], 'success');
  playSong(data['spotify_uri']);
  updateInputPlaceholder();
});

socket.on('message', (data) => {
  respond('Whoops!', data['msg'], 'warn');
});

var sessionKey,
  $queryInput,
  $recBtn,
  recognition,
  messageRecording = "Recording...",
  messageCouldntHear = "I couldn't hear you, could you say that again?",
  messageInternalError = "Oh no, there has been an internal server error",
  messageSorry = "I'm sorry, I don't have the answer to that yet.",
  placeholders = [
    'e.g. Play thank u, next by Ariana Grande',
    'e.g. Play a song like needy but more acoustic',
    "e.g. Play a song like needy but dancier",
    'e.g. Play No One by Alicia Keys',
    'e.g. Play a song like No One but more popular',
    "e.g. Play a song like No One but happier",
    "e.g. Play a song like No One but sadder",
    "e.g. Play a song like No One but more electric",
    "e.g. Play a song like Girl on Fire but more obscure",
  ],
  placeholderIdx = 0;

$(document).ready(function() {
  $queryInput = $("#query-input");
  $recBtn = $("#rec");

  $queryInput.keypress(function(event) {
    if (event.which == 13) {
      event.preventDefault();
      send($queryInput.val());
    }
  });
  $recBtn.on("click", function(event) {
    switchRecognition();
  });
  $(".debug__btn").on("click", function() {
    $(this).next().toggleClass("is-active");
    return false;
  });
});

function startRecognition() {
  recognition = new webkitSpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onstart = function(event) {
    respond(messageRecording, '');
    updateRec();
  };
  recognition.onresult = function(event) {
    recognition.onend = null;

    var text = "";
    for (var i = event.resultIndex; i < event.results.length; ++i) {
      text += event.results[i][0].transcript;
    }
    setInput(text);
    stopRecognition();
  };
  recognition.onend = function() {
    respond(messageCouldntHear, 'error');
    stopRecognition();
  };
  recognition.lang = "en-US";
  recognition.start();
}

function stopRecognition() {
  if (recognition) {
    recognition.stop();
    recognition = null;
  }
  updateRec();
}

function switchRecognition() {
  if (recognition) {
    stopRecognition();
  } else {
    startRecognition();
  }
}

function setInput(text) {
  $queryInput.val(text);
  send($queryInput.val());
}

function updateRec() {
  let icon = $recBtn.find('i');
  if (recognition) {
    $recBtn.removeClass('btn-primary');
    icon.removeClass('icon-message');
    icon.addClass('icon-stop');

  } else {
    $recBtn.addClass('btn-primary');
    icon.removeClass('icon-stop');
    icon.addClass('icon-message');
  }
}

function send(userQuery) {
  socket.emit(
    'query',
    {'text': userQuery, 'session_key': sessionKey},
  );
}

function respond(title, msg, msgType) {
  if (msg == "") {
    msg = messageSorry;
    msgType = "error";
  }

  if (msg !== messageRecording) {
    var voiceMsg = new SpeechSynthesisUtterance();
    voiceMsg.voiceURI = "native";
    voiceMsg.text = msg;
    voiceMsg.lang = "en-US";
    window.speechSynthesis.speak(voiceMsg);
  }

  $('#query-response').remove();

  let elemClass = 'toast-primary';
  if (msgType === "success") {
    elemClass = 'toast-success';

  } else if (msgType === "warn") {
    elemClass = 'toast-warning';

  } else if (msgType === "error") {
    elemClass = 'toast-error';
  }

  $('<div/>', {
    id: 'query-response',
    class: 'toast ' + elemClass,
    css: 'display: block',
  }).prependTo('body');

  let toastElem = $('#query-response');
  // TODO: make them appear on same line
  $('<h6/>', {
    id: 'query-response-title',
    html: title,
    css: 'display: inline-block',
  }).appendTo(toastElem);
  $('<p/>', {
    id: 'query-response-msg',
    html: msg,
  }).appendTo(toastElem);
}

function updateInputPlaceholder() {
  placeholderIdx = (placeholderIdx + 1) % placeholders.length;
  $queryInput.attr('placeholder', placeholders[placeholderIdx]);
}
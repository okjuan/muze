/*
  Original Author: Patrick Catanzariti
  Original Source Code: https://github.com/sitepoint-editors/Api-AI-Personal-Assistant-Demo
  Original Tutorial: https://www.sitepoint.com/how-to-build-your-own-ai-assistant-using-api-ai/

  Edited by Juan Carlos Gallegos.

  * It accepts user input and sends to server via websockets
  * Plays Spotify song if included server's response
*/

var socket = io.connect('http://localhost:5000');
socket.on('connect', () => {
  socket.emit('start session');
});

socket.on('session key', (data) => {
  sessionKey = data['session_key'];
});

socket.on('play song', (data) => {
  respond(data['msg']);
  playSong(data['spotify_uri']);
});

socket.on('message', (data) => {
  respond(data['msg']);
});

var sessionKey,
  $speechInput,
  $recBtn,
  recognition,
  messageRecording = "Recording...",
  messageCouldntHear = "I couldn't hear you, could you say that again?",
  messageInternalError = "Oh no, there has been an internal server error",
  messageSorry = "I'm sorry, I don't have the answer to that yet.";

$(document).ready(function() {
  $speechInput = $("#speech");
  $recBtn = $("#rec");

  $speechInput.keypress(function(event) {
    if (event.which == 13) {
      event.preventDefault();
      send($speechInput.val());
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
    respond(messageRecording);
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
    respond(messageCouldntHear);
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
  $speechInput.val(text);
  send($speechInput.val());
}

function updateRec() {
  $recBtn.text(recognition ? "Stop" : "Speak");
}

function send(userQuery) {
  socket.emit(
    'query',
    {'text': userQuery, 'session_key': sessionKey},
  );
}

function respond(val) {
  if (val == "") {
    val = messageSorry;
  }

  if (val !== messageRecording) {
    var msg = new SpeechSynthesisUtterance();
    msg.voiceURI = "native";
    msg.text = val;
    msg.lang = "en-US";
    window.speechSynthesis.speak(msg);
  }

  $("#spokenResponse").addClass("is-active").find(".spoken-response__text").html(val);
}

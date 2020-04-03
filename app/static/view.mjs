const View = {
  RecommendationButtons: undefined,
  OnReady: (loadView) => {
    $(document).ready(loadView());
  },
  UpdateCurrentlyPlaying: ({song, artist, album}) => {
    let elem = $("#track-name");
    elem.text(`${song.name}`);

    elem = $("#artist-name");
    elem.text(`${artist.name}`);

    elem = $("#album-name");
    elem.text(`${album.name}`);

    let albumArtElem = $('#album-art');
    albumArtElem.attr('src', album.coverLink);

    let songLinkElem = $('#album-art-link');
    songLinkElem.attr('href', song.link);

    $('#music-metadata-container').css('display', 'block');
  },
  PresentSinglePlayButton: ({clickHandler}) => {
    // default view contains button for playing random song
    $('#random-song').on('click', () => {
      setElemClass('random-song', 'loading');
      clickHandler();
    });
  },
  PresentRecommendationControls: ({recommendationHandler, randomSongHandler}) => {
    if (View.RecommendationButtons === undefined) {
      View.RecommendationButtons = getRecommendationButtons(recommendationHandler, randomSongHandler);
    }

    let controlsContainer = $('#player-controls-container');
    if (controlsContainer.length === 0) {
      console.log("ERROR: Could not find location to present recommendation controls.")
      return;
    }

    let currentPlayerControls = controlsContainer.children();
    if (currentPlayerControls.length === 0) {
      controlsContainer.append(View.RecommendationButtons);

    } else {
      currentPlayerControls.hide('slow', () => {
        controlsContainer.append(View.RecommendationButtons);
        currentPlayerControls.remove();
      });
    }
  },

  PresentPlaylistEditorControls : ({addSongHandler}) => {
    let playlistControls = $("#playlist-controls");
    if (playlistControls.length === 0) {
      console.log("ERROR: Could not find where to present playlist controls.");
      return;
    }

    if (playlistControls.children().length !== 0) {
      console.log("Aborting presentation of palylist conotrols, as they are already present.");
    }

    playlistControls.append(
      $("<button></button>")
        .attr('id', 'add-song-to-playlist')
        .addClass('btn btn-primary btn-lg')
        .text('Save to Playlist')
        .on('click', () => {
          setElemClass('add-song-to-playlist', 'loading');
          addSongHandler();
        })
    );
  },

  // code smell: is it really necessary to expose this method? couldn't we instead
  //             update the state when the View updates?
  SetState: ({loading}) => {
    if (loading === false) {
      $('.loading').removeClass('loading');
    }
  }
}

const setElemClass = (id, cssClass) => {
  $('#'+id).addClass(cssClass);
}

const getRecommendationButtons = (recommendationHandler, randomSongHandler) => {
  let recommendationButtons = [];
  for (let btn of [
    {adj: undefined,        title: 'More like this',        id: 'similar-rec-btn'},
    {adj: 'less acoustic',  title: 'More electric',         id: 'more-electric-rec-btn'},
    {adj: 'more acoustic',  title: 'More acoustic',         id: 'more-acoustic-rec-btn'},
    {adj: 'less popular',   title: 'More obscure',          id: 'more-obscure-rec-btn'},
    {adj: 'more popular',   title: 'More mainstream',       id: 'more-popular-rec-btn'},
    {adj: 'more happy',     title: 'Happier',               id: 'happier-rec-btn'},
    {adj: 'less happy',     title: 'Sadder',                id: 'sadder-rec-btn'},
    {adj: 'less dancey',    title: 'Less dancey',           id: 'less-dancey-rec-btn'},
    {adj: 'more dancey',    title: 'Dancier',               id: 'dancier-rec-btn'},
  ]) {
    recommendationButtons.push($('<button></button>')
      .attr('id', btn.id)
      .addClass("btn btn-primary btn-sm m-2")
      .text(btn.title)
      .on('click', () => {
        setElemClass(btn.id, 'loading');
        recommendationHandler({recommendType: btn.adj});
      })
    );
  }
  recommendationButtons.push($('<button></button>')
    .attr('id', 'random-rec-btn')
    .addClass("btn btn-sm m-2")
    .text("Just random!")
    .on('click', () => {
      setElemClass('random-rec-btn', 'loading');
      randomSongHandler();
    })
  );
  return recommendationButtons;
};

export { View }
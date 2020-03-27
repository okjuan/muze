const View = {
  RecommendationButtons: undefined,
  OnReady: (loadHandler) => {
    $(document).ready(loadHandler);
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
    // view is loaded as default view in HTML
    $('#random-song').on('click', () => {
      setElemClass('random-song', 'loading');
      clickHandler();
    });
  },
  PresentRecommendationControls: ({recommendationHandler, randomSongHandler}) => {
    if (View.RecommendationButtons === undefined) {
      View.RecommendationButtons = getRecommendationButtons(recommendationHandler, randomSongHandler);
    }
    let randSongBtn = $('#random-song');
    if (randSongBtn.length === 0) {
      return;
    }
    randSongBtn.hide('slow', () => {
      randSongBtn.after(View.RecommendationButtons);
      randSongBtn.remove();
    });
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
    {adj: undefined,        title: 'More like this',         id: 'similar-rec-btn'},
    {adj: 'less acoustic',  title: 'More electric!',         id: 'more-electric-rec-btn'},
    {adj: 'more acoustic',  title: 'No, more acoustic',      id: 'more-acoustic-rec-btn'},
    {adj: 'less popular',   title: 'Actually, more obscure', id: 'more-obscure-rec-btn'},
    {adj: 'more popular',   title: 'More mainstream please', id: 'more-popular-rec-btn'},
    {adj: 'more happy',     title: 'Damn, cheer up',         id: 'happier-rec-btn'},
    {adj: 'less happy',     title: 'Make it sad :(',         id: 'sadder-rec-btn'},
    {adj: 'less dancey',    title: 'I don\'t dance',         id: 'dancier-rec-btn'},
    {adj: 'more dancey',    title: 'I wanna dance to it!',   id: 'dancier-rec-btn'},
  ]) {
    recommendationButtons.push($('<button></button>')
      .attr('id', btn.id)
      .addClass("btn btn-primary btn-sm m-2")
      .text(btn.title)
      .on('click', () => {
        setElemClass(btn.id, 'loading');
        recommendationHandler(btn.adj);
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
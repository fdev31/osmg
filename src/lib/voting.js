// FIXME: kickPlayerVote isn't a generic function, shouldn't be in utils
// FIXME: passing parameters to a generic function should be done in the Vue application code
// FIXME: kickPlayerVote uses hardcoded strings
// FIXME: kickPlayerVote uses translated strings
export async function kickPlayerVote(app, player, validate = "true") {
  let appliant;
  app.players.map((p) => {
    if (parseInt(p.id) === parseInt(app.myId)) appliant = p;
  });
  let description = `${appliant.name}%20veut%20d%C3%A9gager%20${player.name}`;
  vote({
    kicker: appliant,
    kicked: player,
    validate: validate,
    description: description,
    app: app,
  });
  app.gameData.hasVoted = true;
}

/**
 * Trigger a vote between players toward server
 *
 * @param {Object} query.kicker The player kicking.
 * @param {Object} query.kicked The player to kick.
 * @param {boolean} query.validate A binary choice , where true = yes and false = no.
 * @param {string} query.description The text describing the action.
 * @param {Object} query.app The vue app calling the function, must contain secret and sessionName values.
 */
async function vote(query) {
  let url = `http://${document.location.host}/c/session/vote?name=kick_${query.kicked.id}&validate=${query.validate}&description=${query.description}`;
  let action = await post(url, {
    id: parseInt(query.kicker.id),
    secret: parseInt(query.app.secret),
    sessionName: query.app.name,
  });
}

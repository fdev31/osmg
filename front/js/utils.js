async function getJson(url) {
  const req = await fetch(url);
  const data = await req.json();
  return data;
}
function extractJsonFromCookie() {
  for (let chunk of document.cookie.split("; ")) {
    if (chunk.startsWith("JS=")) {
      return JSON.parse(chunk.substr(3));
    }
  }
}

function setCookie(data) {
  document.cookie = "JS=" + JSON.stringify(data) + "; SameSite=Strict";
  return document.cookie;
}

function setEventStreamHandler(handler, query) {
  if (typeof query.topic == "undefined" || typeof query.uid == "undefined")
    throw "paramater missing";
  const evtSource = new EventSource(
    `/c/stream?topic=${query.topic}&uid=${query.uid}`
  );
  evtSource.addEventListener("update", (event) => {
    handler(JSON.parse(event.data));
  });
}
function runOnEnter(code) {
  if (event.key == "Enter") eval(code);
}
function copyURL(inputId) {
  let w = document.getElementById(inputId);
  w.select();
  w.setSelectionRange(0, 999);
  document.execCommand("copy");
}
function Vue2Obj(vueApp) {
  const r = {};
  for (let k of Object.keys(vueApp.$data)) {
    r[k] = JSON.parse(JSON.stringify(vueApp[k]));
  }
  return r;
}
function extractObj(o) {
  if (o.charAt || typeof o == "number") return o; // Plain
  if (o.length) return extractList(o); // list
  return Object.fromEntries(Object.keys(o).map((x) => [x, extractObj(o[x])]));
}
function extractList(l) {
  let r = [];
  for (let i = 0; i < l.length; i++) r.push(extractObj(l[i]));
  return r;
}

function setupStreamEventHandler(query, handlers) {
  setEventStreamHandler((data) => {
    if (handlers[data.cat]) {
      handlers[data.cat](data);
      console.log(data);
    } else {
      console.warn("No handler for " + data.cat);
      console.log(data);
    }
  }, query);
}

async function post(url, body) {
  var myHeaders = new Headers();
  myHeaders.append("Content-Type", "application/json");

  var raw = JSON.stringify(body);

  var requestOptions = {
    method: "POST",
    headers: myHeaders,
    body: raw,
    redirect: "follow",
  };

  var response = await fetch(url, requestOptions);
  const result = await response.json();
  return result;
}

function setAttr(e, name, val) {
  e.forEach((x) => x.setAttribute(name, val));
}
function show(e) {
  e.forEach((x) => (x.style.visibility = "visible"));
}
function hide(e) {
  e.forEach((x) => (x.style.visibility = "hidden"));
}

function arrayEquals(arr1, arr2) {
  if (!Array.isArray(arr1) || !Array.isArray(arr2))
    throw `arguments must be Array objects , ${typeof arr1} and ${typeof arr2} given`;
  if (arr1.length != arr2.length) return false;
  arr1.sort();
  arr2.sort();
  isEquals = true;
  arr1.every(function (element, index) {
    if (element !== arr2[index]) isEquals = false;
  });
  return isEquals;
}

function findPlayer(data, pid) {
  for (const player of data.players) {
    if (player.id == pid) {
      return player;
    }
  }
}
class Toaster {
  // # Initialiser
  // # function pour créer toast
  // # function pour définir les options
  constructor(id = "toaster") {
    this.anchor = document.getElementById(id);
    this.default_options = {
      closeTimeOut: 1000,
    };
  }
  findAnchor() {
    if (this.anchor == undefined)
      throw "No tag to work with. Be sure that you provide an id";
    return this.anchor;
  }
  createBody(classList = []) {
    this.findAnchor().classList.add("jom-toaster");
    let mainFrame = document.createElement("div");
    mainFrame.classList.add("jom-frame");
    classList.map((c) => {
      mainFrame.classList.add(c);
    });

    let message = createElement("div", "", ["jom-message"]);
    mainFrame.appendChild(message);
    this.findAnchor().appendChild(mainFrame);
  }
  addMessage(message) {
    let collection = this.findAnchor().getElementsByClassName("jom-message");
    collection = Array.from(collection);
    console.log(collection);
    collection.forEach((x) => {
      x.innerHTML = message;
    });
  }
  /**
   * Create a new button with its own logic
   *
   * @param {string} options.caption The text in the button.
   * @param {Object} options.action The function defining what will happen on click.
   * @param {boolean} options.hideOnClick Whether or not the Toaster will hide on click.
   */
  createButton(options) {
    let btn = createElement("button", options.caption);
    btn.addEventListener("click", options.action);
    if (options.hideOnClick)
      btn.addEventListener("click", (x) => this.disableVisibility());
    return btn;
  }
  createButtonGroup(options) {
    let btnGroup = createElement("div", "", ["jom-custombtn"]);
    for (const [key, value] of Object.entries(options)) {
      btnGroup.appendChild(
        this.createButton({
          caption: key,
          action: value.action,
          hideOnClick: value.hideOnClick,
        })
      );
      this.findAnchor().appendChild(btnGroup);
    }
  }
  enableVisibility() {
    this.findAnchor().classList.add("visible");
  }
  disableVisibility() {
    this.findAnchor().classList.remove("visible");
  }
  cleanToaster() {
    removeAllChildElement(this.findAnchor());
  }
  show(message, options = {}) {
    // update signature / calls of show()

    let showOptions = { ...this.default_options, ...options };
    this.cleanToaster();
    this.createBody();
    this.addMessage(message.message || message);
    this.enableVisibility();
    if (showOptions.buttonGroup)
      this.createButtonGroup(showOptions.buttonGroup);

    if (showOptions.closeTimeOut > 0)
      setTimeout((x) => this.disableVisibility(), showOptions.closeTimeOut);
  }
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
let currentLocale = null;

function initLocales() {
  let langs = navigator.languages;
  let lang = langs[langs.length - 1];
  if (locales[lang]) {
    currentLocale = lang;
  }
  //currentLocale = 'fr'; // to test a locale
}

function getTranslation(text) {
  if (currentLocale === null) return text;
  let r = locales[currentLocale][text];
  if (r) return r;
  console.debug(`No translation found for "${text}" using ${currentLocale}`);
  return text;
  //return "/!\\ E: " + text; // to debug english
}

function removeValueFromArray(value, myarray) {
  if (myarray == undefined)
    throw "array is not defined. Provide a proper arguments";
  for (let index = 0; index < myarray.length; index++) {
    if (myarray[index] === value) {
      myarray.splice(index, 1);
      index--;
    }
  }
}
function removeAllChildElement(elm) {
  while (elm.lastChild) {
    elm.removeChild(elm.lastChild);
  }
}
function createElement(type = "div", innerHtml = null, classList = []) {
  let elm = document.createElement(type);
  elm.innerHTML = innerHtml;
  classList.map((x) => elm.classList.add(x));
  return elm;
}

async function kickPlayerVote(app, player, validate = "true") {
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

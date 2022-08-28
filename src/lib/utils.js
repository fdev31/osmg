import { locales } from "./locales.js";

export function delay(duration = 1000) {
  return new Promise((res) => {
    setTimeout(res, duration);
  });
}

export function extractJsonFromCookie() {
  for (let chunk of document.cookie.split("; ")) {
    if (chunk.startsWith("JS=")) {
      return JSON.parse(chunk.substr(3));
    }
  }
}
export function setCookie(data) {
  document.cookie = "JS=" + JSON.stringify(data) + "; SameSite=Strict";
  return document.cookie;
}

function _setEventStreamHandler(handler, query) {
  if (typeof query.topic == "undefined" || typeof query.uid == "undefined")
    throw new Error("parameter missing");
  const evtSource = new WebSocket(
    `ws://${document.location.host}/c/stream?topic=${query.topic}&uid=${query.uid}`
  );
  evtSource.addEventListener("message", (event) => {
    handler(JSON.parse(event.data));
  });
}
export function copyURL(inputId) {
  let w = document.getElementById(inputId);
  w.select();
  w.setSelectionRange(0, 999);
  document.execCommand("copy");
}
export function setupStreamEventHandler(query, handlers) {
  _setEventStreamHandler((data) => {
    let logO = { ...data };
    let cat = logO.cat;
    delete logO.cat;
    console.debug(
      `${(handlers[cat] && "Handled") || "Unhandled"} Event ${cat}: `,
      logO
    );
    if (handlers[cat]) {
      handlers[cat](logO);
    }
  }, query);
}

export async function getJson(url) {
  const req = await fetch(url);
  const data = await req.json();
  return data;
}
export async function post(url, body) {
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

// TODO: move the Toaster class to a separate file

export class Toaster {
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
    if (options.action) btn.addEventListener("click", options.action);
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
          action: value.action || null,
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
let currentLocale = null;

export function initLocales() {
  let langs = navigator.languages;
  for (let lang of langs) {
    lang = lang.slice(0, 2);
    if (locales[lang]) {
      currentLocale = lang;
    }
  }
  //currentLocale = 'fr'; // to test a locale
}

const _transWarnings = new Set();

export function getTranslation(text) {
  if (currentLocale === null) return text;
  let r = locales[currentLocale][text];
  if (r) return r;
  if (!_transWarnings.has(text)) {
    console.debug(`No translation found for "${text}" using ${currentLocale}`);
    _transWarnings.add(text);
  }
  return text;
  //return "/!\\ E: " + text; // to debug english
}

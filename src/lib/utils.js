import { locales } from "./locales.js";

export const client_host = document.location.href.slice(
  0,
  -document.location.pathname.length,
);

export const host = import.meta.env.DEV
  ? "http://localhost:5000"
  : document.location.href.slice(0, -document.location.pathname.length);

class Logger {
  constructor(name, baseObj) {
    this.name = name;
    this.obj = baseObj;
    this.enabled = import.meta.env.DEV;
  }
  error(...args) {
    this.enabled && this.obj.error(this.name, ...args);
  }
  warn(...args) {
    this.enabled && this.obj.warn(this.name, ...args);
  }
  debug(...args) {
    this.enabled && this.obj.debug(this.name, ...args);
  }
  print(...args) {
    if (this.enabled) {
      this.obj.log(...args);
    }
  }
  table(title, obj) {
    if (this.obj) {
      console.group(title);
      this.obj.table(obj);
      console.groupEnd();
    }
  }
}

export function isDarkMode() {
  return !!(
    window.matchMedia &&
    window.matchMedia("(prefers-color-scheme: dark)").matches
  );
}

export function getLogger(name) {
  return new Logger(`${name}::`, import.meta.env.DEV ? console : false);
}

const log = getLogger("utils");

export function delay(duration = 1000) {
  return new Promise((res) => {
    setTimeout(res, duration);
  });
}
export function randomChoice(collection) {
  const idx = Math.floor(Math.random() * collection.length);
  return collection[idx];
}

const cookie_name = "S";

export function extractJsonFromCookie() {
  for (let chunk of document.cookie.split("; ")) {
    if (chunk.startsWith(cookie_name)) {
      return JSON.parse(chunk.substr(cookie_name.length + 1));
    }
  }
}
export function setCookie(data) {
  document.cookie = `${cookie_name}=${JSON.stringify(
    data,
  )}; SameSite=Strict; path=/;`;
}

function _setEventStreamHandler(handler, query) {
  if (typeof query.topic == "undefined" || typeof query.uid == "undefined")
    throw new Error("parameter missing");
  const proto = document.location.href.startsWith("https") ? "wss" : "ws";
  const evtSource = new WebSocket(
    `${proto}://${host.split("//")[1]}/c/stream?topic=${query.topic}&uid=${
      query.uid
    }`,
  );
  evtSource.addEventListener("message", (event) => {
    handler(JSON.parse(event.data));
  });
  return evtSource;
}
export function copyURL(inputId) {
  let w = document.getElementById(inputId);
  w.select();
  w.setSelectionRange(0, 999);
  document.execCommand("copy");
}
export function setupStreamEventHandler(query, handlers) {
  return _setEventStreamHandler((data) => {
    let logO = { ...data };
    let cat = logO.cat;
    delete logO.cat;
    log.debug(
      `${(handlers[cat] && "Handled") || "Unhandled"} Event ${cat}: `,
      logO,
    );
    if (handlers[cat]) {
      handlers[cat](logO);
    }
  }, query);
}

export function getPlayerFromSession(sess) {
  return {
    id: sess.myId,
    sessionName: sess.name,
    secret: sess.secret,
  };
}

export async function getJson(url) {
  const req = await fetch(host + url);
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

  var response = await fetch(host + url, requestOptions);
  const result = await response.json();
  return result;
}

let currentLocale = null;

export function initLocales() {
  if (currentLocale) return;
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
    log.debug(`No translation found for "${text}" using ${currentLocale}`);
    _transWarnings.add(text);
  }
  return text;
  //return "/!\\ E: " + text; // to debug english
}

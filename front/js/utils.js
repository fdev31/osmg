async function getJson(url) {
  const req = await fetch(url);
  const data = await req.json();
  return data;
}
function extractJsonFromCookie() {
  for (let chunk of document.cookie.split('; ')) {
    if (chunk.startsWith("JS=")) {
      return JSON.parse(chunk.substr(3));
    }
  }
}

function setCookie(data) {
  document.cookie = "JS=" + JSON.stringify(data) + '; SameSite=Strict';
  return document.cookie;
}

function setEventStreamHandler(handler , query ) {
  if (typeof query.topic == "undefined" || typeof query.uid == "undefined") throw "paramater missing"
  const evtSource = new EventSource(`/stream?topic=${query.topic}&uid=${query.uid}`);
  evtSource.addEventListener("update", (event) => handler(JSON.parse(event.data)) );
}

function Vue2Obj(vueApp) {
  const r = {};
  for (let k of Object.keys(vueApp._data)) {
    r[k] = JSON.parse(JSON.stringify(vueApp[k]));
  }
  return r;
}
function extractObj(o) {
    if (o.charAt || typeof o == "number") return o; // Plain
    if (o.length) return extractList(o); // list
    return Object.fromEntries(Object.keys(o).map( (x) => [x, extractObj(o[x])] ));
}
function extractList(l) {
    let r = [];
    for (let i=0; i<l.length; i++)
        r.push(extractObj(l[i]));
    return r;
}

function setupStreamEventHandler(query, handlers) {
    setEventStreamHandler((data) => {
        if(handlers[data.cat]) {
            handlers[data.cat](data)
        } else {
            console.error("No handler for "+data.cat);
            console.log(data);
        }
    }, query);
}

async function post(url , body) {
  var myHeaders = new Headers();
  myHeaders.append("Content-Type", "application/json");

  var raw = JSON.stringify(body);

  var requestOptions = {
    method: 'POST',
    headers: myHeaders,
    body: raw,
    redirect: 'follow'
  };


  var response = await fetch(url, requestOptions);
  const result = await response.json();
  return result;
}

function setAttr(e, name, val) {
    e.forEach( x => x.setAttribute(name, val) );
}
function show(e) {
    e.forEach( x => x.style.visibility = "visible" );
}
function hide(e) {
    e.forEach( x => x.style.visibility = "hidden" );
}


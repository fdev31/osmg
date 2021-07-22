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
  const evtSource = new EventSource(`/c/stream?topic=${query.topic}&uid=${query.uid}`);
  evtSource.addEventListener("update", (event) => handler(JSON.parse(event.data)) );
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
            console.warn("No handler for "+data.cat);
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

function arrayEquals(arr1 , arr2) {
    if (!Array.isArray(arr1) || !Array.isArray(arr2)) throw `arguments must be Array objects , ${typeof arr1} and ${typeof arr2} given`;
    if (arr1.length != arr2.length) return false;
    arr1.sort();
    arr2.sort();
    isEquals = true;
    arr1.every(function(element, index) {
        if (element !== arr2[index]) isEquals = false
    })
    return isEquals
}

function findPlayer(data , pid) {
  for (const player of data.players) {
    if (player.id == pid) {
      return player;
    }
  }
}
class Toaster {
  constructor(frameId = "toaster"){
    this.frame = document.getElementById(frameId);
    this.pending = [];
    this.displayed = false;
    this.defaultOptions = {
      message:"",
      time:1000,
      type:"",
      expanded:false,
      vote:false,
      votequery: null,
      app : null,
    }
  }
  setOptions(options) {
    let res = this.defaultOptions;
    Object.keys(options).map((k) => {
      res[k] = options[k];
    });
    return res;
  }
  createToaster(options) {
    let frame = document.createElement("div");
    if (options.type != "" && !options.type) {
      options.type.split(' ').map((x)=> {
        frame.classList.add(x)});      
    }
    frame.id = "toast-frame";
    let message = document.createElement("div");
    message.innerHTML = options.message;
    frame.appendChild(message);
    if (options.expanded) {
      let buttongroup = document.createElement("div");
      let button = document.createElement("button");
      button.innerHTML = "Close";
      button.onclick = function() {document.getElementById('toaster').classList.remove('visible');}
      frame.appendChild(button);
    }
    if (options.vote) {
      let buttongroup = document.createElement("div");
      let buttonyes = document.createElement("button");
      let buttonno = document.createElement("button");
      buttonyes.innerHTML = "Yes";
      buttonno.innerHTML = "No";
      console.log(options);
      buttonyes.onclick = function(){
        options.app.kickPlayerVote(options.votequery.kicked, "true");
        document.getElementById('toaster').classList.remove('visible');}
      buttonno.onclick = function(){
        options.app.kickPlayerVote(options.votequery.kicked, "true");
        document.getElementById('toaster').classList.remove('visible');}
      buttongroup.appendChild(buttonyes).appendChild(buttonno);
      frame.appendChild(buttongroup);
      
    }
    return frame;
  }
  display(){
    this.displayed = false;
    if (this.pending.length) {
        let val = this.pending.pop();
        return this.show(val.message, val);
    } else {
        this.frame.classList.remove('visible');
    }    
  }
  show(options){
    options = this.setOptions(options);
    if (this.displayed) {
        this.pending.push({message : options.message, time :  options.time, type : options.expanded});
    } else {
        this.displayed = true;
        let toaster = this.createToaster(options);
        this.frame.appendChild(toaster);
        if (options.expanded || options.vote) {
          this.display();
        } 
        else {
          setTimeout(() => {
            this.display()
          },options.time)
        }
        this.frame.classList.add('visible');
    }
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
async function vote (query) {
  let url = `http://${document.location.host}/c/session/vote?name=kick_${query.kicked.id}&validate=${query.validate}&description=${query.description}`;
  let action = await post(url, {
      "id":parseInt(query.kicker.id),
      "secret": parseInt(query.app.secret),
      "sessionName":query.app.name
  });
}
let currentLocale = null;

function initLocales() {
  let langs = navigator.languages;
  let lang = langs[langs.length-1];
  if (locales[lang]) {
    currentLocale = lang;
  }
  //currentLocale = 'fr'; // to test a locale
}

function getTranslation(text) {
  if (currentLocale === null) return text;
  let r = locales[currentLocale][text];
  if (r) return r;
  console.warn(`No translation found for "${text}" using ${currentLocale}`);
  return text;
  //return "/!\\ E: " + text; // to debug english
}

function removeValueFromArray(value, myarray) {
  if (myarray == undefined ) throw "array is not defined. Provide a proper arguments"
  for (let index = 0; index < myarray.length; index++) {
    if (myarray[index] === value) {      
    myarray.splice(index,1)
    index--;
    }   
  }
}

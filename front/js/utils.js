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
      let button1 = document.createElement("button");
      let button2 = document.createElement("button");
      button1.innerHTML = "Yes";
      button2.innerHTML = "No";
      button1.onclick = function(){options.app.voteYes();document.getElementById('toaster').classList.remove('visible');}
      button2.onclick = function(){options.app.voteNo();document.getElementById('toaster').classList.remove('visible');}
      buttongroup.appendChild(button1).appendChild(button2);
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
        console.log(toaster);
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

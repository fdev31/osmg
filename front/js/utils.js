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

function setEventStreamHandler(handler , topicName) {
  const evtSource = new EventSource(`/stream?topic=${topicName}`);
  evtSource.addEventListener("update", (event) => handler(JSON.parse(event.data)) );
}

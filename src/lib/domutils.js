function removeAllChildElement(elm) {
  while (elm.lastChild) {
    elm.removeChild(elm.lastChild);
  }
}
function createElement(type = "div", innerHtml = null, classList = []) {
  let elm = document.createElement(type);
  elm.innerHTML = innerHtml;
  classList.forEach((x) => elm.classList.add(x));
  return elm;
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

function runOnEnter(code) {
  if (event.key == "Enter") eval(code);
}

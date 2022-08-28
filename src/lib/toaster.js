// TODO: replace with a component
export class Toaster {
  // # Initialiser
  // # function pour créer toast
  // # function pour définir les options
  constructor(id = "toaster") {
    //this.anchor = document.getElementById(id);
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
    console.log(message);
    return;
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

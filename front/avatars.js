const accessories = ['earphones', 'earring1', 'earring2', 'earring3', 'none', 'none', 'none', 'none'];
const clothes = ['blazer', 'hoodie', 'overall', 'sweater', 'vneck'];
const eyebrows = ['angry', 'angry2', 'default', 'default2', 'raised', 'sad', 'sad2', 'unibrow', 'updown', 'updown2'];
const eyes = ['close', 'cry', 'default', 'dizzy', 'evil', 'eyeroll', 'happy', 'hearts', 'side', 'squint', 'surprised', 'wink', 'winkwacky'];
const facialhair = ['fancy', 'light', 'magestic', 'magnum'];
const glasses = ['fancy', 'fancy2', 'harry', 'nerd', 'none', 'none', 'none', 'none', 'none', 'none', 'old', 'rambo'];
const hairstyles = ['hairbun', 'longhair', 'longhairbob', 'longhaircurly', 'longhaircurvy', 'longhairdread', 'longhairstraight', 'longhairstraight2', 'miawallace', 'none', 'nottoolong', 'shorthaircurly', 'shorthairdreads', 'shorthairdreads2', 'shorthairflat', 'shorthairround', 'shorthairshaggy', 'shorthairsides', 'shorthairwaved'];
const mouths = ['concerned', 'default', 'disbelief', 'eating', 'grimace', 'sad', 'scream', 'serious', 'smile', 'tongue', 'twinkle', 'vomit'];
const tattoos = ['airbender', 'front', 'harry', 'krilin', 'none', 'none', 'none', 'none', 'none', 'none', 'throat', 'tribal2'];
const skincolors = ["ffdbb4","edb98a","fd9841","fcee93","d08b5b","ae5d29","614335"];
const fabriccolors = ["545454","65c9ff","5199e4","25557c","e6e6e6","929598","a7ffc4","ffdeb5","ffafb9","ffffb1","ff5c5c","e3adff"];
const haircolors = ["bb7748_9a4f2b_6f2912","404040_262626_101010","c79d63_ab733e_844713","e1c68e_d0a964_b88339","906253_663d32_3b1d16","f8afaf_f48a8a_ed5e5e","f1e6cf_e9d8b6_dec393","d75324_c13215_a31608","59a0ff_3777ff_194bff"];
function isInvariant(text) {
    return (text[text.length-1] == 's' || text == 'facialhair')
}

function getMagicIndex(propname, db) {
    let collectionname = isInvariant(propname) ? propname : (propname + 's');
    return Math.floor(Math.random()*db[collectionname].length);
}

class Avatar {
    constructor(domRef) {
        this._ref = domRef;
        this.db = {skincolors, fabriccolors, haircolors, accessories,
            clothes , eyebrows , eyes , facialhair , glasses , hairstyles ,
            mouths , tattoos};
        this.random();
    }
    getKeys() {
        return [ 'skincolor', 'eyes', 'eyebrows', 'mouth', 'hairstyle', 'haircolor', 'facialhair',
            'clothes', 'glasses', 'glassopacity', 'tattoo', 'accessories', 'fabriccolor'];
    }
    asObject() {
        let r = {};
        for (let k of this.getKeys())
            r[k] = this.getValue(k);
        return r;
    }
    asArray() {
        return this.getKeys().map( (k) => this.getIndex(k))
    }
    asString() {
        return this.asArray().join(':');
    }
    fromName(name) {
        if (name == '') name = 'ouf';
        let vals = [];
        let src_idx = 0;
        for (let k of this.getKeys()) {
            let v = name.charCodeAt(src_idx);
            src_idx++;
            if (src_idx >= name.length) src_idx = 0;
            vals.push(v);
        }
        let total = Array.from(name).map((c) => c.charCodeAt(0)-60).reduce((a,b)=>a+b);
        for (let i=0; i<vals.length; i++) vals[i] += (total - i);
        let i=0;
        for (let k of this.getKeys()) {
            this[k] = vals[i++];
        }
        this.update();
    }
    getIndexValue(attrName) {
        if (attrName == 'glassopacity') return [this[attrName]%10, (this[attrName]%10)*0.1];
        let choiceName = isInvariant(attrName) ? attrName : (attrName + 's');
        let values = this.db[choiceName];
        let i = this[attrName]%values.length
        return [i, values[i]];
    }
    getIndex(attrName) {
        return this.getIndexValue(attrName)[0];
    }
    getValue(attrName) {
        return this.getIndexValue(attrName)[1];
    }
    debug() {
        let o = this.asObject();
        for (let k of Object.keys(o)) {
            console.log(k, this[k], this.getValue(k));
        }
    }
    random() {
        for (let k of this.getKeys())
            if (k != 'glassopacity')
                this[k] = getMagicIndex(k, this.db)
        this.glassopacity = Math.floor(Math.random() * 10);
        this.update();
        return this;
    }
    asCode() {
        return parseInt(this.asArray().join('')).toString(36);
    }
    fromCode(code) {
        code = parseInt(code, 36);
        let keys = this.getKeys();
        let i =0;
        for (let c of code.toString()) {
            this[keys[i]] = parseInt(c);
            i++;
        }
        this.update();
    }
    update() {
        let o = document.querySelector(this._ref);
        let d = this.asObject();
        setAttr(o.querySelectorAll(".skin #body"), "fill",`#${d.skincolor}`);
        hide(o.querySelectorAll("g.eyes g"));
        show(o.querySelectorAll(`g.eyes g.${d.eyes}`));
        hide(o.querySelectorAll("g.eyebrows g"));
        show(o.querySelectorAll(`g.eyebrows .${d.eyebrows}`));
        hide(o.querySelectorAll("g.mouths g"));
        show(o.querySelectorAll(`g.mouths g.${d.mouth}`));
        hide(o.querySelectorAll("g.hair_front g"));
        hide(o.querySelectorAll("g.hair_back g"));
        show(o.querySelectorAll(`g.hair_front g.${d.hairstyle}`));
        show(o.querySelectorAll(`g.hair_back g.${d.hairstyle}`));
        let color = d.haircolor.split('_');
        setAttr( o.querySelectorAll(`g.hair_front .${d.hairstyle} .tinted`), "fill","#"+color[0]);
        setAttr( o.querySelectorAll(`g.hair_back .${d.hairstyle} .tinted`), "fill","#"+color[1]);
        setAttr( o.querySelectorAll("g.facialhair g .tinted"), "fill","#"+color[2]);
        hide(o.querySelectorAll("g.facialhair g"));
        show(o.querySelectorAll(`g.facialhair g.${d.facialhair}`));
        hide(o.querySelectorAll("g.clothes g"));
        show(o.querySelectorAll(`g.clothes g.${d.clothes}`));
        hide(o.querySelectorAll("g.glasses g"));
        show(o.querySelectorAll(`g.glasses g.${d.glasses}`));
        setAttr(o.querySelectorAll(".glass"), "fill-opacity", d.glassopacity);
        setAttr(o.querySelectorAll("g.clothes .tinted"), "fill",`#${d.fabriccolor}`);
        hide(o.querySelectorAll("g.tattoos g"));
        show(o.querySelectorAll("g.tattoos g."+d.tattoo));
        hide(o.querySelectorAll("g.accessories g"));
        show(o.querySelectorAll("g.accessories g."+d.accessories));
    }
}


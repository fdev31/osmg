const accesories = ['earphones', 'earring1', 'earring2', 'earring3', 'none', 'none', 'none', 'none'];
const clothes = ['blazer', 'hoodie', 'overall', 'sweater', 'vneck'];
const eyebrows = ['angry', 'angry2', 'default', 'default2', 'raised', 'sad', 'sad2', 'unibrow', 'updown', 'updown2'];
const eyes = ['close', 'cry', 'default', 'dizzy', 'evil', 'eyeroll', 'happy', 'hearts', 'side', 'squint', 'surprised', 'wink', 'winkwacky'];
const facialhair = ['fancy', 'light', 'magestic', 'magnum'];
const glasses = ['fancy', 'fancy2', 'harry', 'nerd', 'none', 'none', 'none', 'none', 'none', 'none', 'old', 'rambo'];
const hairstyles = ['hairbun', 'longhair', 'longhairbob', 'longhaircurly', 'longhaircurvy', 'longhairdread', 'longhairstraight', 'longhairstraight2', 'miawallace', 'nottoolong', 'shorthaircurly', 'shorthairdreads', 'shorthairdreads2', 'shorthairflat', 'shorthairround', 'shorthairshaggy', 'shorthairsides', 'shorthairwaved'];
const mouths = ['concerned', 'default', 'disbelief', 'eating', 'grimace', 'sad', 'scream', 'serious', 'smile', 'tongue', 'twinkle', 'vomit'];
const tattoos = ['airbender', 'front', 'harry', 'krilin', 'none', 'none', 'none', 'none', 'none', 'none', 'throat', 'tribal2'];
const skins = ["ffdbb4","edb98a","fd9841","fcee93","d08b5b","ae5d29","614335"];
const fabriccolors = ["545454","65c9ff","5199e4","25557c","e6e6e6","929598","a7ffc4","ffdeb5","ffafb9","ffffb1","ff5c5c","e3adff"];
const haircolors = ["bb7748_9a4f2b_6f2912","404040_262626_101010","c79d63_ab733e_844713","e1c68e_d0a964_b88339","906253_663d32_3b1d16","f8afaf_f48a8a_ed5e5e","f1e6cf_e9d8b6_dec393","d75324_c13215_a31608","59a0ff_3777ff_194bff"];
function serieMaker(seed) {
    if (!seed) seed = 42;
    if (seed < 1000) {
        seed *= 1000;
    }
    r = [];
    r.push(seed + Math.floor(seed * 0.5) );
    r.push(Math.floor(seed * 0.5) );
    let s = Math.floor(Math.sqrt(seed));
    r.push(s);
    let strseed = seed.toString();
    let v = parseInt(strseed.substr(strseed.length/2) + strseed.substr(null, strseed.length/2));
    let x = parseInt(strseed.charCodeAt(3) + seed + strseed.charCodeAt(0));
    let z = Math.floor(seed + seed/0.33 + seed*seed);
    r.push(v);
    r.push(x);
    r.push(x+v);
    r.push(Math.floor(x/2)+v);
    r.push(x+s);
    r.push(v+s);
    r.push(Math.floor(seed/s));
    r.push(z);
    r.push(z-s);
    r.push(z-x);
    r.push(z+x+s);
    r.push(z+x+s+v);
    return r;
}

function getMagicIndex(array) {
    return array[Math.floor(Math.random()*array.length)];
}

class Avatar {
    constructor(domRef) {
        this._ref = domRef;
        this.random();
    }
    asObject() {
        let r = {};
        for (let k of Object.keys(this)) {
            if (k[0] != '_') r[k] = this[k];
        }
        return r;
    }
    asArray() {
        return Object.values(this.asObject())
    }
    asString() {
        return this.asArray().join(':');
    }
    fromName(name) {
        let seed = [];
        for (let i=0; i<name.length; i++)
            seed.push(name.charCodeAt(i));
        seed = parseInt(seed.join(''));
        let serie = serieMaker(seed);

        this.skincolor        = skins[serie[0]%(skins.length)];
        this.eyes             = eyes[serie[1]%(eyes.length)];
        this.eyebrows         = eyebrows[serie[2]%(eyebrows.length)];
        this.mouth            = mouths[serie[3]%(mouths.length)];
        this.hairstyle        = hairstyles[serie[4]%(hairstyles.length)];
        this.haircolor        = haircolors[serie[5]%(haircolors.length)];
        this.facialhair       = facialhair[serie[6]%(facialhair.length)];
        this.clothes          = clothes[serie[7]%(clothes.length)];
        this.glasses          = glasses[serie[9]%(glasses.length)];
        this.glassopacity     = 0.1*(serie[10]%10);
        this.tatoos           = tattoos[serie[11]%(tattoos.length)];
        this.accesories       = accesories[serie[12]%(accesories.length)];
        this.fabriccolors     = fabriccolors[serie[13]%(fabriccolors.length)];
        this.update();
    }
    debug() {
       console.log('skins',  this.skincolor );
       console.log('eyes',  this.eyes );
       console.log('eyebrows',  this.eyebrows );
       console.log('mouths',  this.mouth );
       console.log('hairstyles',  this.hairstyle );
       console.log('haircolors',  this.haircolor );
       console.log('facialhair',  this.facialhair );
       console.log('clothes',  this.clothes );
       console.log('glasses',  this.glasses );
       console.log('glassOp', this.glassopacity);
       console.log('tattoos',  this.tatoos );
       console.log('accesories',  this.accesories );
       console.log('fabriccolors',  this.fabriccolors );
    }
    random() {
        this.skincolor = getMagicIndex(skins);
        this.eyes = getMagicIndex(eyes);
        this.eyebrows = getMagicIndex(eyebrows);
        this.mouth = getMagicIndex(mouths);
        this.hairstyle = getMagicIndex(hairstyles);
        this.haircolor = getMagicIndex(haircolors);
        this.facialhair = getMagicIndex(facialhair);
        this.clothes = getMagicIndex(clothes);
        this.glasses = getMagicIndex(glasses);
        this.glassopacity = Math.random();
        this.tatoos = getMagicIndex(tattoos);
        this.accesories = getMagicIndex(accesories);
        this.fabriccolors = getMagicIndex(fabriccolors);
        this.update();
        return this;
    }
    update() {
        let o = document.querySelector(this._ref);
        setAttr(o.querySelectorAll(".skin #body"), "fill","#"+this.skincolor);
        hide(o.querySelectorAll("#eyes g"));
        show(o.querySelectorAll("#eyes .e_"+this.eyes));
        hide(o.querySelectorAll("#eyebrows g"));
        show(o.querySelectorAll("#eyebrows .eb_"+this.eyebrows));
        hide(o.querySelectorAll("#mouths g"));
        show(o.querySelectorAll("#mouths .m_"+this.mouth));
        hide(o.querySelectorAll("#hair_front g"));
        hide(o.querySelectorAll("#hair_back g"));
        show(o.querySelectorAll("#hair_front .h_"+this.hairstyle));
        show(o.querySelectorAll("#hair_back .h_"+this.hairstyle));
        let color = this.haircolor.split('_');
        setAttr( o.querySelectorAll("#hair_front .h_"+this.hairstyle+" .tinted"), "fill","#"+color[0]);
        setAttr( o.querySelectorAll("#hair_back .h_"+this.hairstyle+" .tinted"), "fill","#"+color[1]);
        setAttr( o.querySelectorAll("#facialhair g .tinted"), "fill","#"+color[2]);
        hide(o.querySelectorAll("#facialhair g"));
        show(o.querySelectorAll("#facialhair .f_"+this.facialhair));
        hide(o.querySelectorAll("#clothes g"));
        show(o.querySelectorAll("#clothes .c_"+this.clothes));
        hide(o.querySelectorAll("#glasses g"));
        show(o.querySelectorAll("#glasses .g_"+this.glasses));
        setAttr(o.querySelectorAll(".glass"), "fill-opacity",this.glassopacity);
        setAttr(o.querySelectorAll("#clothes g .tinted", "fill","#"+this.fabriccolors));
        hide(o.querySelectorAll("#tattoos g"));
        show(o.querySelectorAll("#tattoos .t_"+this.tatoos));
        hide(o.querySelectorAll("#accesories g"));
        show(o.querySelectorAll("#accesories .a_"+this.accessories));
    }
}


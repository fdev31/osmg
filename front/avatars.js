const skins = ["ffdbb4","edb98a","fd9841","fcee93","d08b5b","ae5d29","614335"];
const eyes = ["default","dizzy","eyeroll","happy","close","hearts","side","wink","squint","surprised","winkwacky","cry"];
const eyebrows = ["default","default2","raised","sad","sad2","unibrow","updown","updown2","angry","angry2"];
const mouths = ["default","twinkle","tongue","smile","serious","scream","sad","grimace","eating","disbelief","concerned","vomit"];
const hairstyles = ["bold","longhair","longhairbob","hairbun","longhaircurly","longhaircurvy","longhairdread","nottoolong","miawallace","longhairstraight","longhairstraight2","shorthairdreads","shorthairdreads2","shorthairfrizzle","shorthairshaggy","shorthaircurly","shorthairflat","shorthairround","shorthairwaved","shorthairsides"];
const haircolors = ["bb7748_9a4f2b_6f2912","404040_262626_101010","c79d63_ab733e_844713","e1c68e_d0a964_b88339","906253_663d32_3b1d16","f8afaf_f48a8a_ed5e5e","f1e6cf_e9d8b6_dec393","d75324_c13215_a31608","59a0ff_3777ff_194bff"];
const facialhairs = ["none","magnum","fancy","magestic","light"];
const clothes = ["vneck","sweater","hoodie","overall","blazer"];
const fabriccolors = ["545454","65c9ff","5199e4","25557c","e6e6e6","929598","a7ffc4","ffdeb5","ffafb9","ffffb1","ff5c5c","e3adff"];
const backgroundcolors = ["ffffff","f5f6eb","e5fde2","d5effd","d1d0fc","f7d0fc","d0d0d0"];
const glasses = ["none","rambo","fancy","old","nerd","fancy2","harry"];
//const glassopacities = ["10","25","50","75","100"];
const tattoos = ["non","harry","airbender","krilin","front","tribal","tribal2","throat"];
const accesories = ["none","earphones","earring1","earring2","earring3"];

function setAttr(e, name, val) {
    e.forEach( x => x.setAttribute(name, val) );
}
function show(e) {
    e.forEach( x => x.style.visibility = "visible" );
}
function hide(e) {
    e.forEach( x => x.style.visibility = "hidden" );
}

function getMagicIndex(array) {
    return array[Math.floor(Math.random()*array.length)];
}

class Avatar {
    constructor(domRef) {
        this.ref = domRef;
        this.skincolor = "edb98a";
        this.hairstyle = "longhair";
        this.haircolor = "bb7748_9a4f2b_6f2912";
        this.fabriccolors = "545454";
        this.backgroundcolors = "ffffff";
        this.glassopacity = 0.5;
    }
    random() {
        this.skincolor = getMagicIndex(skins);
        this.eyes = getMagicIndex(eyes);
        this.eyebrows = getMagicIndex(eyebrows);
        this.mouth = getMagicIndex(mouths);
        this.hairstyle = getMagicIndex(hairstyles);
        this.haircolor = getMagicIndex(haircolors);
        this.facialhair = getMagicIndex(facialhairs);
        this.clothes = getMagicIndex(clothes);
        this.backgroundcolors = getMagicIndex(backgroundcolors);
        this.glasses = getMagicIndex(glasses);
        this.glassopacity = Math.random();
        this.tatoos = getMagicIndex(tattoos);
        this.accesories = getMagicIndex(accesories);
        this.fabriccolors = getMagicIndex(fabriccolors);
        this.backgroundcolors = getMagicIndex(backgroundcolors);
        this.update();
        return this;
    }
    update() {
        let o = document.querySelector(this.ref);
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
        setAttr(o.querySelectorAll("#background"), "fill","#"+this.backgroundcolors);
        hide(o.querySelectorAll("#tattoos g"));
        show(o.querySelectorAll("#tattoos .t_"+this.tatoos));
        hide(o.querySelectorAll("#accesories g"));
        show(o.querySelectorAll("#accesories .a_"+this.accessories));
    }
}


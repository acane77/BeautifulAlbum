import zh_CN from "@/i18n/zh-CN.js"
import en_US from "@/i18n/en-US"

let translations = {
    "zh-CN": zh_CN,
    "en-US": en_US,
};

function GetCurrentLanguage() {
    let lan =  navigator.language;
    if (window.localStorage) {
        let user_set_lan = window.localStorage.getItem("language");
        if (typeof user_set_lan !== "undefined" && user_set_lan != null && user_set_lan.length) {
            lan = user_set_lan;
        }
    }
    if (lan.startsWith("en"))
        return "en-US";
    else
        return lan;
}

let _current_language = GetCurrentLanguage();
console.log("Current language is", _current_language);

function I18nTextF(text, ...args) {
    if (args.length === 0)
        return text;
    return text.replace(/\{(\d+)\}/g, function (match, index) {
        return typeof args[index] != "undefined" ? args[index] : match;
    });
}

function I18nTranslate(text, ...args) {
    let lan = _current_language;
    if (typeof translations[lan] == "undefined")
        _current_language = "en-US"; // Use en-US for unknown language
    let translated = translations[lan][text];
    if (typeof translated == "undefined")
        return I18nTextF(text, ...args);
    return I18nTextF(translated, ...args);
}

export default {
    i18n_translate: I18nTranslate
}

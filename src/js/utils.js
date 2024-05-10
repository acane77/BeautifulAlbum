///////// NETWORK

function get_secured_json(url) {
    let password = ".";
    if (window.enabled_password)
        password = window.miyuki_password;
    return new Promise((resolve, reject) => {
        fetch(`/api/${password}/${url}.json`).then(function(response) {
            if(response.ok) {
                return resolve(response.json())
            }
            throw new Error('Network response was not ok: url');
        }).catch(function (x) {
            console.error('HTTP Request: /GET ' + url + ' [FAILED]', x);
            reject(x);
        });
    })
}

function get_json(url) {
    return new Promise((resolve, reject) => {
        fetch(`/api/${url}.json`).then(function(response) {
            if(response.ok) {
                return resolve(response.json())
            }
            throw new Error('Network response was not ok: url');
        }).catch(function (x) {
            console.error('HTTP Request: /GET ' + url + ' [FAILED]', x);
            reject(x);
        });
    })
}

function md5_transform(a, b) {
    if (a.length !== 32 || b.length !== 32) {
        throw new Error('Both MD5 strings must be 32 characters long.');
    }

    var c = Array(32).fill(0);
    for (let i=0; i<32; i++) {
        let _a = Number.parseInt(a[i], 16);
        let _b = Number.parseInt(b[i], 16);
        c[i] = (_a ^ _b).toString(16);
    }
    return c.join('');
}

export default {
    get_secured_json: get_secured_json,
    get_json: get_json,
    md5_transform: md5_transform,
}
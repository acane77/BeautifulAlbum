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


export default {
    get_secured_json: get_secured_json,
    get_json: get_json
}
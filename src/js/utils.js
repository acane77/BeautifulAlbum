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

function DownloadTextAsFile(content, filename) {
    // 动态生成文本内容
    // 创建一个 Blob 对象，包含生成的文本内容
    const blob = new Blob([content], { type: 'text/plain' });

    // 创建一个 a 标签，用于下载 Blob 对象
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename; // 设置下载文件的名称
    a.style.display = 'none'; // 隐藏 a 标签
    document.body.appendChild(a); // 将 a 标签添加到文档中
    a.click(); // 模拟点击 a 标签，触发下载操作
    document.body.removeChild(a); // 下载完成后移除 a 标签
}

function GetCurrentTimeFormatted() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0'); // 月份是从0开始的，所以需要+1，并且用0填充到两位数
    const date = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');

    return `${year}${month}${date}_${hours}${minutes}${seconds}`;
}

export default {
    get_secured_json: get_secured_json,
    get_json: get_json,
    md5_transform: md5_transform,
    download_text_as_file: DownloadTextAsFile,
    get_current_time_f: GetCurrentTimeFormatted,
}
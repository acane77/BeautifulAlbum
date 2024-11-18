import i18n from "@/i18n/index.js"

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

function GetFileContent(ext='.txt') {
    return new Promise((resolve, reject) => {
        // 创建一个新的input元素
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = ext; // 可以根据需要更改接受的文件类型

        // 设置文件选择后的事件处理
        fileInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const text = e.target.result; // 文件内容
                    resolve(text); // 调用回调函数并传递文件内容
                };
                reader.onerror = function(e) {
                    reject(e.target.error); // 调用回调函数并传递错误信息
                };
                reader.readAsText(file); // 读取文件内容
            } else {
                reject(new Error('No file selected.')); // 如果没有选择文件，则返回错误
            }
        });

        // 触发点击事件（必须由用户手动触发，不能模拟）
        fileInput.click();

        // 如果需要，可以将fileInput添加到DOM中，但这通常不是必需的，因为我们只关心文件内容
        // document.body.appendChild(fileInput);
    });
}

function CalculateCenterFaceBackgroundPosition(photo) {
    // 如果没有开启人脸居中功能，即没有在生成API的时候做人脸检测，直接返回默认值
    if (typeof photo.faces == "undefined") {
        return '0px 0px';
    }
    let faces = photo.faces;
    // 如果没有检测到人脸
    if (faces.length == 0)
        return '0px 0px';

    // 根据所有的人脸框，求出人脸框平均值最大的位置
    let avg_x = faces.map(e => e[0]).reduce((a, b)=>a+b, 0) / faces.length;
    let avg_y = faces.map(e => e[1]).reduce((a, b)=>a+b, 0) / faces.length;
    let avg_w = faces.map(e => e[2]).reduce((a, b)=>a+b, 0) / faces.length;
    let avg_h = faces.map(e => e[3]).reduce((a, b)=>a+b, 0) / faces.length;

    // 图片平均中心点的位置
    let center_x = avg_x + avg_w / 2;
    let center_y = avg_y + avg_h / 2;

    let image_w = photo.w;
    let image_h = photo.h;

    /*
                 Preview Window
      +---------+-------------+---+
      |         |   +-----+   |   |
      |         |   |Face |   |   |  Image
      |         |   +-----+   |   |
      |         |             |   |
      +---------+-------------+---+

       其中预览框是正方形。
     */

    // 判断是否是竖图
    let is_vertical = image_w < image_h;
    if (is_vertical) {
        // 交换长短边，保证长边短边就是物理意义的长短，w必然大于h
        [image_h, image_w] = [image_w, image_h];
        [center_x, center_y] = [center_y, center_x];
    }

    // 计算人脸框中点位于整体宽度的比例
    let relative_pos_ratio = center_x / image_w;
    // 长边相对短边更长的比例（实际在background position偏移100%的时候，是以这个比例在原图的size上偏移）
    let actual_offset_ratio = (image_w - image_h) / image_w;
    // 短边占长边的比例，即，预览框的半长比例
    let wh_ratio = image_h / image_w;
    // 计算偏移到图片的100%需要在background position设置的偏移量
    let full_offset_ratio = 1 / actual_offset_ratio;
    // 计算偏移到人脸框的位置需要的实际图片偏移量
    let offset_ratio = full_offset_ratio * (relative_pos_ratio - wh_ratio / 2);
    // 防止超过图片最大的偏移量（100%）或最小偏移量(0%)
    offset_ratio = Math.max(0, Math.min(1, offset_ratio));

    // 竖图
    if (is_vertical) {
        return `0 ${offset_ratio * 100}%`;
    }
    // 横图
    else {
        return `${offset_ratio * 100}% 0`;
    }
}

export default {
    get_secured_json: get_secured_json,
    get_json: get_json,
    md5_transform: md5_transform,
    download_text_as_file: DownloadTextAsFile,
    get_current_time_f: GetCurrentTimeFormatted,
    get_file_content: GetFileContent,
    calc_center_face_bg_pos: CalculateCenterFaceBackgroundPosition,
    translate: i18n.i18n_translate,
}
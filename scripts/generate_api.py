import sys

import numpy as np
import os
from PIL import Image
import json
import pathlib
import math
import hashlib
import argparse
import face_detect
import cv2
import time
import pickle
import face_clustering

PASSWORD_ENABLED = False
PASSWORD_IN_MD5 = ''
CENTER_FACE = False
ENABLE_SHARED = True
FACE_CLUSTERING = False

_g_face_detector = None

HASH2ALBUM = {}

ENUM_API_TYPE_NORMAL = "normal"
ENUM_API_TYPE_ALIAS = "alias"

FACE_CLUSTERING_RESULTS = []

def split_array(arr, N=50):
    result = []
    for i in range(0, len(arr), N):
        result.append(arr[i:i + N])
    return result

def get_album_path(album_name=''):
    if album_name != '':
        album_name = album_name + '/'
    return './album/{}'.format(album_name)

def get_album_thumbnail_path(album_name=''):
    if album_name != '':
        album_name = album_name + '/'
    return './album-cache/{}'.format(album_name)

def is_album_path_existed(album_name=''):
    return os.path.isdir(get_album_path(album_name))

def is_album_cache_path_existed(album_name=''):
    return os.path.isdir(get_album_thumbnail_path(album_name))

def create_cache_dir(album_name=''):
    if is_album_cache_path_existed(album_name):
        return
    os.mkdir(get_album_thumbnail_path(album_name))

def write_json_file(path, obj):
    global PASSWORD_ENABLED, PASSWORD_IN_MD5
    if PASSWORD_ENABLED:
        path = "{}/{}".format(PASSWORD_IN_MD5, path)
    print('-- Generating album API: {}'.format(path))
    with open(path, 'w', encoding='utf8') as file:
        file.write(json.dumps(obj))

def write_shared_json_file(path, obj):
    if not ENABLE_SHARED:
        return
    shared_filename = "shared/" + path  # path can be "xxx/zzz.json"
    shared_base_dir = os.path.dirname(shared_filename)
    if not os.path.exists(shared_base_dir):
        os.mkdir(shared_base_dir)
    print('-- Generating shared album API: {}'.format(shared_filename))
    with open(shared_filename, 'w') as fp:
        fp.write(json.dumps(obj))


def read_file(path):
    try:
        with open(path, 'r', encoding='utf8') as file:
            return file.read()
    except:
        return None

# 获取相册列表,并创建缓存目录
def get_album_list():
    if not is_album_path_existed():
        raise Exception('Album directory {} does not exist'.format(get_album_path()))
    create_cache_dir()
    files = os.listdir(get_album_path())
    album_names = []
    for f in files:
        if os.path.isdir(get_album_path(f)):
            album_names.append(f)
            create_cache_dir(f)
    return album_names


def create_hash_name_from_album_name(album_name):
    time_str = time.strftime("%Y%m%d%H%M%S")
    return MD5(album_name + time_str)


## 生成 /api/get-album.json
def generate_json__get_album():
    def get_metadata_filename(album_name):
        return '{}{}.txt'.format(get_album_path(), album_name)
    album_names = get_album_list()
    jsonobj = []

    for aname in album_names:
        preview_name = ""
        # get preview
        files = os.listdir(get_album_path(aname))
        if len(files) > 0:
            preview_name = files[0]
        metafile = get_metadata_filename(aname)
        if os.path.isfile(metafile):
            jsonobj.append({"name": aname, "friendly_name": read_file(metafile), "preview": preview_name})
        else:
            jsonobj.append({"name": aname, "friendly_name": aname, "preview": preview_name})
    write_json_file('get-album.json', jsonobj)
    return album_names

## 生成图片的缩略图并返回图片信息
def make_thumbnail(album_name, image_file_name):
    cf = '{}{}'.format(get_album_thumbnail_path(album_name), image_file_name)
    im = ""
    try:
        im = Image.open('{}{}'.format(get_album_path(album_name), image_file_name))
    except:
        print(" -- warning: cannot open: {}/{}".format(album_name, image_file_name))
        return 0, 0
    width, height = im.size
    if (os.path.isfile(cf)):
        im.close()
        return width, height
    dst_width = 256
    dst_height = int(dst_width*height/width)
    im.thumbnail((dst_width, dst_height))
    print('-- Generating thumbnail for: {}/{}'.format(album_name, image_file_name))
    try:
        im.save(cf)
    except:
        print("   warning: cannot save: {}/{}".format(album_name, image_file_name))
    im.close()
    return width, height

def generate_photo_by_page(image_data, filename_callback):
    photo_for_each_page = 50
    page_count = math.ceil(len(image_data) / 50)
    for page in range(page_count):
        ph_obj = []
        for i in range(page*photo_for_each_page, min(len(image_data), (page+1)*photo_for_each_page)):
            ph_obj.append(image_data[i])
        #write_json_file("{}-get-photo-page-{}.json".format(album_name, page), ph_obj)
        def __run_filename_callback(cb):
            filename = cb(page)
            if type(filename) is list or type(filename) is tuple:
                filename, api_type = filename[0], filename[1]
            else:
                # Default ENUM_API_TYPE_NORMAL
                filename, api_type = filename, ENUM_API_TYPE_NORMAL

            if api_type == ENUM_API_TYPE_NORMAL:
                write_json_file(filename, ph_obj)
            elif api_type == ENUM_API_TYPE_ALIAS:
                write_shared_json_file(filename, ph_obj)
            else:
                raise RuntimeError("Not supported api type: {}".format(api_type))

        if type(filename_callback) is not list:
            filename_callback = [filename_callback]

        for cb in filename_callback:
            __run_filename_callback(cb)
        # filename = filename_callback(page)
        # write_json_file(filename, ph_obj)

# 相片
    ##  /api/{album_name}-get-photo-count.json  相片数量
    ##  /api/{album_name}-get-photo-page-{num}.json  生成缩略图并获取每一页的相片列表
    ##  /api/get-photo-count.json  相片数量
    ##  /api/get-photo-page-{num}.json  生成缩略图并获取每一页的相片列表
    ##  /api/get-recent-photo-count.json  相片数量
    ##  /api/get-recent-photo-page-{num}.json  生成缩略图并获取每一页的相片列表
def generate_json_album_related(album_name=''):
    global CENTER_FACE
    if album_name == '':
        album_names = get_album_list()
        image_objs = []
        for aname in album_names:
            image_objs = image_objs + generate_json_album_related(aname)
        write_json_file("get-photo-count.json", { "count": len(image_objs) })
        generate_photo_by_page(image_objs, lambda page: "get-photo-page-{}.json".format(page))
        ## 最近
        write_json_file("get-recent-photo-count.json", {"count": len(image_objs)})
        image_objs.sort(key=lambda e: e["ct"], reverse=True)
        generate_photo_by_page(image_objs, lambda page: "get-recent-photo-page-{}.json".format(page))
        return
    # 保存每一个相册的照片信息
    photos = os.listdir(get_album_path(album_name))
    image_data = []
    for pf in photos:
        pfl = pf.lower()
        if os.path.isfile('{}{}'.format(get_album_path(album_name), pf)) and (pfl[-4:] in ['.png', '.jpg', '.gif'] or pfl[-5:] in ['.jpeg', '.tiff']):
            ## 生成缩略图
            width, height = make_thumbnail(album_name, pf)
            if width == 0:
                continue
            fd = pathlib.Path('{}{}'.format(get_album_path(album_name), pf))
            ctime = fd.stat().st_ctime
            image_meta = {
                "al": album_name,
                "name": pf,
                "h": height,
                "w": width,
                "ct": ctime
            }
            if CENTER_FACE:
                img_src = '{}{}'.format(get_album_path(album_name), pf)
                print("-- Perform face detection for: ", img_src)
                faces = face_detect.face_detection(detector=_g_face_detector, image_path=img_src)
                image_meta["faces"] = [ [ int(el) for el in rect[:4] ] for rect in faces ]
                print("-- Detected faces: ", image_meta["faces"])
            if FACE_CLUSTERING:
                print("-- Performing embedding extraction for: ", pf)
                img_src = '{}{}'.format(get_album_path(album_name), pf)
                faces = _g_face_detector.get_face_embedding(image_path = img_src)
                print("-- Detected faces: ", len(faces))
                if len(faces):
                    FACE_CLUSTERING_RESULTS.append({
                        "image": image_meta,
                        "faces": faces,
                    })
            image_data.append(image_meta)
    # 生成相片数量
    album_name_hash = create_hash_name_from_album_name(album_name)
    count_obj = { "count": len(image_data), "hash": album_name_hash, "name": album_name }
    write_json_file("{}-get-photo-count.json".format(album_name), count_obj)
    write_shared_json_file("{}-get-photo-count.json".format(album_name_hash), count_obj)
    HASH2ALBUM[album_name_hash] = album_name

    def _generate_shared_album_name(page):
        return "{}-get-photo-page-{}.json".format(album_name_hash, page), ENUM_API_TYPE_ALIAS

    generate_photo_by_page(image_data,
                           [
                               lambda page: "{}-get-photo-page-{}.json".format(album_name, page),
                               _generate_shared_album_name
                           ])

    return image_data

def MD5(str):
    hl = hashlib.md5()
    hl.update(str.encode(encoding='utf-8'))
    return hl.hexdigest()

def check_for_password(password):
    global PASSWORD_ENABLED, PASSWORD_IN_MD5
    if password != "":
        print('-- Password is enabled')
        write_json_file("password.json", {"enabled": True, "share_enabled": ENABLE_SHARED})
        PASSWORD_ENABLED = True
        PASSWORD_IN_MD5 = MD5(password)
        print('-- Password hash value is {}'.format(PASSWORD_IN_MD5))
        # 创建具有密码的目录
        if not os.path.isdir("./{}".format(PASSWORD_IN_MD5)):
            os.mkdir("./{}".format(PASSWORD_IN_MD5))
    else:
        write_json_file("password.json", {"enabled": False})


# 人物分类API
##  /api/people/catagories.json  不同的人的数量
##  /api/people/catagory-{catagory_id}-get-photo-count.json  相片数量
##  /api/people/catagory-{catagory_id}-get-photo-page-{page}.json  生成缩略图并获取每一页的相片列表
def generate_people_collection():
    print("-- Generate people collection APIs")
    if not os.path.isdir("./{}/people".format(PASSWORD_IN_MD5)):
        os.mkdir("./{}/people".format(PASSWORD_IN_MD5))
    print("-- Perform face clustering...")
    face_embedding_test_data = FACE_CLUSTERING_RESULTS
    print("-- Clusering: Count of images:", len(face_embedding_test_data))
    embeds = []
    embeds2images = []
    for image_idx, data in enumerate(face_embedding_test_data):
        if len(data["faces"]):
            embeds += ([face["embedding"] for face in data["faces"]])
            embeds2images += ([image_idx]*len(data["faces"]))
    assert len(embeds) == len(embeds2images)
    print("-- Count of faces:", len(embeds))
    embeds = np.array(embeds)
    print("-- Embedding shape: ", embeds.shape)
    embeds = embeds / np.linalg.norm(embeds, axis=1)[:, np.newaxis]
    # clustering
    labels = face_clustering.clustering(embeds, "dbscan", eps=0.5, min_samples=4)
    # print("-- Labels:", labels)
    categories = set(labels)
    categories = [ c for c in categories if c != -1 ]
    print("Number of categories:", len(categories))
    write_json_file("people/catagories.json", {"count": len(categories)})
    categories2image = {}
    for label_idx, label in enumerate(labels):
        if label == -1:
            continue
        if label not in categories2image.keys():
            categories2image[label] = []
        image_idx = embeds2images[label_idx]
        categories2image[label].append(face_embedding_test_data[image_idx]["image"])
    for catagory_id, cata in categories2image.items():
        print("-- Catagory #{}: {} Images".format(catagory_id, len(cata)))
        write_json_file(f"people/catagory-{catagory_id}-get-photo-count.json", {"count": len(cata)})
        cata = split_array(cata)
        for page, cata_per_page in enumerate(cata):
            write_json_file(f"people/catagory-{catagory_id}-get-photo-page-{page}.json", cata_per_page)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate JSON APIs")
    parser.add_argument("--center_face", action='count',
                        help="Run face detection to make faces always in center in preview mode")
    parser.add_argument("--face_clustering", action='count',
                        help="Run face clustering to generate collections for people")
    parser.add_argument("--disable_share", action='count',
                        help="Disable share album with others")
    parser.add_argument("--password", type=str, default="",
                        help="Specify a password for API")
    parser.add_argument("--face_detector", type=str, default="opencv",
                        help="Specify face detector engine")
    parser.add_argument("--face_detector_model", type=str, default="",
                        help="Specify face detector model")
    args = parser.parse_args()

    CENTER_FACE = args.center_face
    FACE_CLUSTERING = args.face_clustering
    ENABLE_SHARED = not args.disable_share

    print("-- Face detection: ", 'ON' if CENTER_FACE else 'OFF')
    print('-- Password for API: ', 'ON' if args.password != "" else 'OFF')
    print('-- Share enabled: ', ENABLE_SHARED)

    if CENTER_FACE:
        print("-- Face detector: ", args.face_detector)
        print("-- Face detector model: ", "<Use default>" if args.face_detector_model == "" else args.face_detector_model)
        try:
            _g_face_detector = face_detect.create_detector(args.face_detector, args.face_detector_model)
        except Exception as ex:
            print("error: invalid face detector: {}, model: {}, err: {}".format(args.face_detector, args.face_detector_model, str(ex)))
            sys.exit(1)

    print("-- Face clustering: ", 'ON' if FACE_CLUSTERING else 'OFF')

    # remove previous shared directory
    import shutil
    if os.path.exists("shared"):
        shutil.rmtree('shared')

    check_for_password(args.password)

    # 生成相册列表  /api/get-album.json
    generate_json__get_album()

    # 相片
    ##  /api/{album_name}-get-photo-count.json  相片数量
    ##  /api/{album_name}-get-photo-page-{num}.json  生成缩略图并获取每一页的相片列表
    generate_json_album_related()

    # Temp file
    if ENABLE_SHARED:
        with open("hash2album.txt", "w") as h2a_file:
            h2a_file.write("\n".join([ "{}:{}".format(k, v) for k, v in HASH2ALBUM.items() ]))

    if FACE_CLUSTERING:
        # print("-- Saving face embedding data for further use")
        # np.save("face_embedding_test_data.npy", FACE_CLUSTERING_RESULTS)
        generate_people_collection()

    print('-- Generate API Finished!')




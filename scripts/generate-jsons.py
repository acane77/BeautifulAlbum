import numpy as np
import os
from PIL import Image
import json
import pathlib
import math
import hashlib

PASSWORD_ENABLED = False
PASSWORD_IN_MD5 = ''

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
    with open(path, 'w', encoding='utf8') as file:
        file.write(json.dumps(obj))

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
    print('Generating thumbnail for: {}/{}'.format(album_name, image_file_name))
    try:
        im.save(cf)
    except:
        print(" -- warning: cannot save: {}/{}".format(album_name, image_file_name))
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
        filename = filename_callback(page)
        write_json_file(filename, ph_obj)

# 相片
    ##  /api/{album_name}-get-photo-count.json  相片数量
    ##  /api/{album_name}-get-photo-page-{num}.json  生成缩略图并获取每一页的相片列表
    ##  /api/get-photo-count.json  相片数量
    ##  /api/get-photo-page-{num}.json  生成缩略图并获取每一页的相片列表
    ##  /api/get-recent-photo-count.json  相片数量
    ##  /api/get-recent-photo-page-{num}.json  生成缩略图并获取每一页的相片列表
def generate_json_album_related(album_name=''):
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
            image_data.append({ "al": album_name, "name": pf, "h": height, "w": width, "ct": ctime })
    # 生成相片数量
    count_obj = { "count": len(image_data) }
    write_json_file("{}-get-photo-count.json".format(album_name), count_obj)
    generate_photo_by_page(image_data, lambda page: "{}-get-photo-page-{}.json".format(album_name, page))

    return image_data

def MD5(str):
    hl = hashlib.md5()
    hl.update(str.encode(encoding='utf-8'))
    return hl.hexdigest()

def check_for_password():
    global PASSWORD_ENABLED, PASSWORD_IN_MD5
    if os.path.isfile("password.txt"):
        password = read_file("password.txt")
        write_json_file("password.json", {"enabled": True})
        PASSWORD_ENABLED = True
        PASSWORD_IN_MD5 = MD5(password)
        print('Password enabled: hash value is {}'.format(PASSWORD_IN_MD5))
        # 创建具有密码的目录
        if not os.path.isdir("./{}".format(PASSWORD_IN_MD5)):
            os.mkdir("./{}".format(PASSWORD_IN_MD5))
    else
        write_json_file("password.json", {"enabled": False})

if __name__ == '__main__':
    check_for_password()

    # 生成相册列表  /api/get-album.json
    generate_json__get_album()

    # 相片
    ##  /api/{album_name}-get-photo-count.json  相片数量
    ##  /api/{album_name}-get-photo-page-{num}.json  生成缩略图并获取每一页的相片列表
    generate_json_album_related()


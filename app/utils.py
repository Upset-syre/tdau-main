import os
import secrets
import shutil

from flask import current_app


def save_upper_picture(form_picture, id):
    random_hex = secrets.token_hex(16)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    full_path = os.path.join(current_app.root_path, 'static', str(id), 'upper_img')
    if os.path.exists(full_path):
        shutil.rmtree(full_path)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        picture_path = os.path.join(full_path, picture_fn)
        form_picture.save(picture_path)
        return picture_fn
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    picture_path = os.path.join(full_path, picture_fn)
    form_picture.save(picture_path)
    return picture_fn


def save_bottom_picture(form_picture, id):
    random_hex = secrets.token_hex(16)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    full_path = os.path.join(current_app.root_path, 'static', str(id), 'bottom_img')
    if os.path.exists(full_path):
        shutil.rmtree(full_path)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        picture_path = os.path.join(full_path, picture_fn)
        form_picture.save(picture_path)
        return picture_fn
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    picture_path = os.path.join(full_path, picture_fn)
    form_picture.save(picture_path)
    return picture_fn


def save_page_picture(form_picture, id):
    random_hex = secrets.token_hex(16)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    full_path = os.path.join(current_app.root_path, 'news_page', str(id), 'upper_img')
    if os.path.exists(full_path):
        shutil.rmtree(full_path)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        picture_path = os.path.join(full_path, picture_fn)
        form_picture.save(picture_path)
        return picture_fn
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    picture_path = os.path.join(full_path, picture_fn)
    form_picture.save(picture_path)
    return picture_fn

def save_upper_picture2(form_picture, id):
    random_hex = secrets.token_hex(16)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    full_path = os.path.join(current_app.root_path, 'card', str(id), 'upper_img')
    if os.path.exists(full_path):
        shutil.rmtree(full_path)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        picture_path = os.path.join(full_path, picture_fn)
        form_picture.save(picture_path)
        return picture_fn
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    picture_path = os.path.join(full_path, picture_fn)
    form_picture.save(picture_path)
    return picture_fn


def save_bottom_picture2(form_picture, id):
    random_hex = secrets.token_hex(16)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    full_path = os.path.join(current_app.root_path, 'card', str(id), 'bottom_img')
    if os.path.exists(full_path):
        shutil.rmtree(full_path)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        picture_path = os.path.join(full_path, picture_fn)
        form_picture.save(picture_path)
        return picture_fn
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    picture_path = os.path.join(full_path, picture_fn)
    form_picture.save(picture_path)
    return picture_fn




ALLOWED_PICTURE = {'jpg', 'jpeg', 'gif', 'png', 'svg', 'webp', 'bmp'}
def allowed_pic(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_PICTURE
import os
import secrets
import shutil

from flask import current_app


def save_picture(form_picture, id, dir):
    random_hex = secrets.token_hex(16)
    _, f_ext = os.path.splitext(form_picture.filename)
    print(f_ext)
    print(form_picture)
    picture_fn = random_hex + f_ext
    if dir == 'upper_img_page':
        full_path = os.path.join(current_app.root_path, 'static', 'degrees', str(id), 'upper_img')
    if dir == 'bottom_img_page':
        full_path = os.path.join(current_app.root_path, 'static', 'degrees', str(id), 'bottom_img')
    if dir == 'news_page':
        full_path = os.path.join(current_app.root_path, 'static', 'news_page', str(id), 'upper_img')
    if dir == 'upper_card_page':
        full_path = os.path.join(current_app.root_path, 'static', 'card', str(id), 'upper_img')
    if dir == 'bottom_card_page':
        full_path = os.path.join(current_app.root_path, 'static', 'card', str(id), 'bottom_img')
    if dir == 'university_foreign_logo':
        full_path = os.path.join(current_app.root_path, 'static', 'university_foreign', str(id), 'logo')
    if dir == 'university_foreign_picture':
        full_path = os.path.join(current_app.root_path, 'static', 'university_foreign', str(id), 'picture')
    if dir == 'university_foreign_picture_desc':
        full_path = os.path.join(current_app.root_path, 'static', 'university_foreign', str(id), 'picture_desc')
    if dir == 'video':
        full_path = os.path.join(current_app.root_path, 'static', 'university_foreign', str(id), 'video')
    if dir == 'news_img_1':
        full_path = os.path.join(current_app.root_path, 'static', 'news', str(id), 'news_img_1')
    if dir == 'news_img_2':
        full_path = os.path.join(current_app.root_path, 'static', 'news', str(id), 'news_img_2')
    if dir == 'news_video':
        full_path = os.path.join(current_app.root_path, 'static', 'news', str(id), 'news_video')
    if dir == 'news_file':
        full_path = os.path.join(current_app.root_path, 'static', 'news', str(id), 'news_file')
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


ALLOWED_PICTURE = {'jpg', 'jpeg', 'gif', 'png', 'svg', 'webp', 'bmp', 'mp4', '3gp', 'avi'}


def allowed_pic(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_PICTURE

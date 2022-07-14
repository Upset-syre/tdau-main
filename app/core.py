from functools import wraps
from flask import *
import hashlib
import jwt, requests
from numpy import void
from .config import SECRET_KEY
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from hashlib import sha256
from .models import User
import random
import uuid

import qrcode
import qrcode.image.svg

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({
                'message' : "Token is missing !!"
            }), 401
        try:
            print(token)
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            print(data)
            current_user = User.query\
                .filter_by(id=data['public_id'])\
                .first()
        except Exception as E:
            return jsonify({
                'message' : str(E)
            }), 401
        return  f(current_user, *args, **kwargs)
  
    return decorated


def Hash_File(filename, type_id):
    ext = filename.rsplit('.', 1)[1].lower()
    filename = filename.rsplit('.', 1)[0]
    filename = filename + "_" + str(datetime.now())
    return str(type_id) + "_" + sha256(filename.encode('utf-8')).hexdigest() + "." + ext
from werkzeug.datastructures import FileStorage

def hash_and_save(attach: FileStorage, folder : str) -> void:
    
    ext = attach.filename.split(".")[-1]
    
    # print(attach.read())
    # with open("test.docx", "wb") as f:
    #     f.write(attach.read())
    bytes_f = attach.read()
    ret_data = hashlib.md5(bytes_f).hexdigest() + "_." + ext
    with open(os.path.join('uploads', folder, ret_data), "wb") as f:
        f.write(bytes_f)
    return "uploads\\" + folder + "\\" + ret_data
    

def Exist_username(username):
    if not username:
        return True
    d = User.query.filter(User.username == username).all()
    if len(d) != 0:
        return True
    return False
def Create_Username(faculty_id):
    name = None # 1 xxxx yy zz
    faculty_id = str(faculty_id)
    if len(faculty_id) != 3:
        faculty_id = "0"*(3-len(faculty_id)) + faculty_id
    d = str(datetime.now().year)[2:]
    while Exist_username(name):
        rand_id = str(random.randint(1,9999))
        if len(rand_id) != 4:
            rand_id = "0"*(4-len(rand_id)) + rand_id
        name = "S" + rand_id + faculty_id + d
    return name
def Create_Password(id):
    return str(id) + str(random.randint(100,999))

def qr_code_generator(hash, id):

    # hash = sha256(_str.encode()).hexdigest()
    factory = qrcode.image.svg.SvgPathImage
    # img = qrcode.make(hash, image_factory=factory)
    # b = img.to_string().decode()

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=100,
        border=4,
    )

    qr.add_data('http://edm.agro.uz/orders/'+str(id))

    qr.make(fit=True)

    img = qr.make_image(image_factory=factory, fill_color="black", back_color="white")
    b = img.to_string().decode()

    return b


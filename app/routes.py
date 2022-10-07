import secrets
import shutil
from fileinput import filename
import uuid
import requests
from flask import *
from sqlalchemy import null
from .config import SECRET_KEY
from .core import Create_Username, hash_and_save, token_required, Hash_File
from .models import *
import jwt

from werkzeug.utils import secure_filename
import os
from datetime import date, timedelta
import random
import pandas as pd
from . import db
import sys

tdau = Blueprint('tdau', __name__, url_prefix='/tdau')


@tdau.route("/registration", methods=['POST'])
def registration():
    if request.method == 'POST':
        phone = request.form.get("phone")
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        user = User.query.filter_by(phone=phone).first()
        user_u = User.query.filter_by(username=username).first()

        if user or user_u:
            return jsonify({'msg': 'error user with this phone or username already exist'}), 400
        else:

            t_us = User(
                phone=phone,
                username=username,
                email=email,
            )
            t_us.set_password(password)
            db.session.add(t_us)
            db.session.commit()

            adm = Admission(
                user_id=t_us.id,
                email=email,
                phone=phone,
                status=4,
            )

            db.session.add(adm)
            db.session.commit()

            role_m = Role_meta(

                user_id=t_us.id,
                role_id=2

            )
            db.session.add(role_m)
            db.session.commit()

            code = random.randint(1000, 9999)

            session = requests.Session()
            session.auth = ('eijara', "S5Qzy$B$")
            p = {
                'messages': {
                    'recipient': phone,
                    'message-id': 1,
                    'sms': {
                        'originator': '3700',
                        'content': {
                            'text': 'Hi! Your registration code is ' + str(
                                code) + ' . Please enter it to complete your registration.',
                        }
                    }
                }
            }
            auth = session.post('http://91.204.239.44/broker-api/send', json=p)

            t_us.verify_code = code
            db.session.commit()
            print("Code : %s" % code)
            return jsonify({'msg': 'ok'}), 200

    else:
        return jsonify({"message": "Method not allowed"}), 405


@tdau.route("/registration/code", methods=['POST'])
def registration_code():
    if request.method == 'POST':
        phone = request.form.get("phone")
        code = request.form.get("code")
        user = User.query.filter_by(phone=phone).first()
        if user:
            if user.verify_code == code:
                user.verify_code = None
                db.session.commit()
                token = jwt.encode({
                    'public_id': user.id,
                    'exp': datetime.datetime.now() + timedelta(days=100)

                }, SECRET_KEY, algorithm="HS256")
                return jsonify(
                    {
                        "token": token,
                        'msg': 'ok'
                    }
                ), 200
            else:
                return jsonify({'msg': 'error code'}), 400
        else:
            return jsonify({'msg': 'error user with this phone not exist'}), 400
    else:
        return jsonify({"message": "Method not allowed"}), 405


@tdau.route("/login", methods=['POST'])
def login_a():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if user:
        ch = user.check_password(password)
        if ch:
            token = jwt.encode({
                'public_id': user.id,
                'exp': datetime.datetime.now() + + timedelta(days=100)
            }, SECRET_KEY, algorithm="HS256")
            print(token)
            user.last_login = datetime.datetime.now()
            db.session.commit()
            return jsonify({
                'token': token,
                # 'role': [x.format() for x in user.role_metas][0].get("role_name"),
                'msg': "ok"
            }), 200
        return jsonify({
            'msg': "incorrect"
        }), 401
    print('CHORT')
    return jsonify({
        'msg': "not found"
    }), 404


@tdau.route("/admission", methods=['GET'])
@token_required
def admission(u):
    if request.method == 'GET':
        adm = Admission.query.filter_by(user_id=u.id).first()

        if adm:
            return jsonify({
                'msg': "ok",
                'admission': adm.format()
            }), 200
        return jsonify({
            'msg': "not found"
        }), 404


@tdau.route("/nationalities", methods=['GET'])
def nationalities():
    if request.method == 'GET':
        sts = [x.format() for x in Nationality.query.all()]
        return jsonify(sts)


@tdau.route("/genders", methods=['GET'])
def genders():
    if request.method == 'GET':
        sts = [x.format() for x in Gender.query.all()]
        return jsonify(sts)


@tdau.route("/countries", methods=['GET'])
def countries():
    if request.method == 'GET':
        sts = [x.format() for x in Country.query.all()]
        return jsonify(sts)


@tdau.route("/regions", methods=['GET'])
@token_required
def regions(u):
    adm = Admission.query.filter_by(user_id=u.id).first()
    if adm:
        if adm.current_country == "O'zbekiston":
            print(adm.current_country)
            sts = [x.format() for x in Region.query.all()]
            return jsonify(sts)

        return jsonify([x.format() for x in Region.query.all()])

    return jsonify([x.format() for x in Region.query.all()])


@tdau.route("/districts", methods=['GET'])
def districts():
    if request.method == 'GET':
        reg_id = request.args.get("reg_id")
        sts = [x.format()
               for x in District.query.filter_by(reg_id=reg_id).all()]
        return jsonify(sts)


@tdau.route("/education_form", methods=['GET'])
def education_form():
    if request.method == 'GET':
        sts = [x.format() for x in Education_form.query.all()]
        return jsonify(sts)


@tdau.route("/education_type", methods=['GET'])
def education_type():
    if request.method == 'GET':
        sts = [x.format() for x in Education_type.query.all()]
        return jsonify(sts)


@tdau.route("/qualifications", methods=['GET'])
def qualification():
    if request.method == 'GET':
        sts = [x.format() for x in Qualification.query.all()]
        return jsonify(sts)


@tdau.route("/faculties", methods=['GET'])
def read_faculties():
    if request.method == 'GET':
        sts = [x.format() for x in Faculty.query.all()]
        return jsonify(sts)


@tdau.route("/profile", methods=['GET'])
@token_required
def read_profile(u):
    if request.method == 'GET':
        adm_u = Admission.query.filter_by(user_id=u.id).first()
        if adm_u:
            if adm_u.status == 3:
                sts = adm_u.notification_3()
                return jsonify(sts)
            elif adm_u.status == 2:
                sts = adm_u.notification_2()
                return jsonify(sts)
            elif adm_u.status == 1:
                sts = adm_u.notification_1()
                return jsonify(sts)

        return jsonify({
            'msg': "not found"
        }), 400


@tdau.route("/profile_foreign", methods=['GET'])
@token_required
def read_profile_foreign(u):
    adm_u = Admission_Foreign.query.filter_by(user_id=u.id).first()
    print("adm_u.status is ", adm_u.status)
    if adm_u:
        if adm_u.status == 3:
            sts = adm_u.notification_3()
            return jsonify(sts)
        elif adm_u.status == 2:
            sts = adm_u.notification_2()
            return jsonify(sts)
        else:
            sts = adm_u.notification_1()
            return jsonify(sts)
    return jsonify({"msg": "not found admission"}), 400


@tdau.route("/admission_form", methods=['POST', "GET"])
@token_required
def admission_form(u):
    if request.method == 'GET':
        _user_id = u.id
        adm = Admission.query.filter_by(user_id=_user_id).first()
        if adm:
            return jsonify(adm.format()), 200
        else:
            return jsonify({
                'msg': "not found"
            }), 404
    name = request.form.get('name')
    surname = request.form.get('surname')
    middle_name = request.form.get('middle_name')
    birthdate = request.form.get('birthdate')
    passport_number = request.form.get('passport_number')
    passport_expiry = request.form.get('passport_expiry')
    gender_id = request.form.get("gender_id")
    nationality = request.form.get("nationality")
    country_birth = request.form.get("country_birth")
    country_permanent = request.form.get("country_permanent")
    current_country = request.form.get("current_country")
    accept_deadline = request.form.get("accept_deadline")
    aplication_type = request.form.get("aplication_type")
    education_type_id = request.form.get("education_type_id")
    education_form_id = request.form.get("education_form_id")
    adress1 = request.form.get("adress1")
    adress2 = request.form.get("adress2")
    region = request.form.get("region")
    district = request.form.get("district")
    post_index = request.form.get("post_index")
    post_address1 = request.form.get("post_address1")
    post_address2 = request.form.get("post_address2")
    print(post_address1)
    post_region = request.form.get("post_region")
    post_district = request.form.get("post_district")
    post_index2 = request.form.get("post_index2")
    school = request.form.get("school")
    qualification = request.form.get("qualification")
    qualification2 = request.form.get("qualification2")
    qualification_start = request.form.get("qualification_start")
    qualification_end = request.form.get("qualification_end")
    gpa = request.form.get("GPA")
    comment = request.form.get("comment")
    register_step = request.form.get("register_step")
    phone = request.form.get("phone")
    phone_a = request.form.get("phone_a")
    email = request.form.get("email")
    faculty_id = request.form.get("faculty_id")
    qualification_info = None
    if 'qualification_info' in request.files:
        print("qualification_info got")
        qualification_info = request.files["qualification_info"]
    print(request.files)
    qualification_diploma = None
    if 'qualification_diploma' in request.files:
        qualification_diploma = request.files["qualification_diploma"]
    essay = None
    if 'essay' in request.files:
        essay = request.files["essay"]
    resume = None
    if 'resume' in request.files:
        resume = request.files["resume"]
    recommendation = None
    if 'recommendation' in request.files:
        recommendation = request.files["recommendation"]

    recommendation_second = None
    if 'recommendation_second' in request.files:
        recommendation_second = request.files["recommendation_second"]

    adm = Admission.query.filter_by(user_id=u.id).first()

    if adm:
        if faculty_id:
            adm.faculty_id = faculty_id
        if name:
            adm.name = name
        if qualification_end:
            adm.qualification_end = qualification_end

        if qualification_start:
            adm.qualification_start = qualification_start
        if surname:
            adm.surname = surname
        if middle_name:
            adm.middle_name = middle_name
        if birthdate:
            adm.birthdate = birthdate
        if passport_number:
            adm.passport_number = passport_number
        if passport_expiry:
            adm.passport_expiry = passport_expiry
        if gender_id:
            adm.gender_id = gender_id
        if nationality:
            adm.nationality = nationality
        if country_birth:
            adm.country_birth = country_birth
        if aplication_type:
            adm.aplication_type = aplication_type
        if education_type_id:
            adm.education_type_id = education_type_id
        if education_form_id:
            adm.education_form_id = education_form_id
        if adress1:
            adm.adress1 = adress1
        if adress2:
            adm.adress2 = adress2
        if region:
            adm.region = region
        if district:
            adm.district = district
        if post_index:
            adm.post_index = post_index
        if post_address1:
            adm.post_adress1 = post_address1
        if post_address2:
            adm.post_adress2 = post_address2
        if post_region:
            adm.post_region = post_region
        if post_district:
            adm.post_district = post_district
        if post_index2:
            adm.post_index2 = post_index2
        if school:
            adm.school = school
        if qualification:
            adm.qualification = qualification
        if qualification2:
            adm.qualification2 = qualification2
        if gpa:
            adm.gpa = gpa
        if comment:
            adm.comment = comment
        if country_permanent:
            adm.country_permanent = country_permanent

        if current_country:
            adm.current_country = current_country

        if accept_deadline:
            adm.accept_deadline = accept_deadline

        if register_step:
            adm.registrater_step = register_step

        if phone:
            adm_p = Admission.query.filter_by(phone=phone).first()
            if adm_p:
                return jsonify({
                    'msg': "phone is already token"
                }), 400
            else:
                adm.phone = phone

        if phone_a:
            adm.phone_a = phone_a

        if email:
            adm_e = Admission.query.filter_by(email=email).first()
            if adm_e:
                return jsonify({
                    'msg': "email is already token"
                }), 400
            else:
                adm.email = email

        if qualification_info:
            adm_att = Adm_Attach(
                admission_id=adm.id,
                info="qualification info",
                path=hash_and_save(qualification_info, 'admission'),
            )
            db.session.add(adm_att)
            db.session.commit()
            print("qualification_info saved")
            print(adm_att.format())

        if qualification_diploma:
            adm_att = Adm_Attach(
                admission_id=adm.id,
                info="qualification diploma",
                path=hash_and_save(qualification_diploma, 'admission'),
            )
            db.session.add(adm_att)
            db.session.commit()

        if essay:
            adm_att = Adm_Attach(
                admission_id=adm.id,
                info="essay",
                path=hash_and_save(essay, 'admission'),
            )
            db.session.add(adm_att)
            db.session.commit()

        if resume:
            adm_att = Adm_Attach(
                admission_id=adm.id,
                info="resume",
                path=hash_and_save(resume, 'admission'),
            )
            db.session.add(adm_att)
            db.session.commit()

        if recommendation:
            adm_att = Adm_Attach(
                admission_id=adm.id,
                info="recommendation",
                path=hash_and_save(recommendation, 'admission'),
            )
            db.session.add(adm_att)
            db.session.commit()
        if recommendation_second:
            adm_att = Adm_Attach(
                admission_id=adm.id,
                info="recommendation second",
                path=hash_and_save(recommendation_second, 'admission'),
            )
            db.session.add(adm_att)
            db.session.commit()

        db.session.commit()
        return jsonify({'msg': "ok"}), 200
    else:
        return jsonify({
            'msg': "not found"
        }), 404


@tdau.route("/admission_confirm", methods=['POST'])
@token_required
def admission_confirm(u):
    if request.method == 'POST':
        print("I am here 1")
        adm_id = request.form.get("adm_id")
        if adm_id:
            print("I am here 2")
            adm = Admission.query.get(adm_id)

            if adm:
                print("I am here 3")
                if adm.name != null and adm.name != null and adm.surname != null and adm.middle_name != null and adm.birthdate != null and adm.passport_number != null and adm.passport_expiry != null and adm.gender_id != null and adm.nationality != null and adm.country_birth != null and adm.aplication_type != null and adm.education_type_id != null and adm.education_form_id != null and adm.adress1 != null and adm.region != null and adm.district != null and adm.post_index != null and adm.post_adress1 != null and adm.post_region != null and adm.post_district != null and adm.school != null and adm.qualification != null and adm.country_permanent != null and adm.current_country != null and adm.accept_deadline != null:
                    print("I am here 4")
                    adm.status = 1
                    adm.register_step = 9
                    db.session.commit()
                    return jsonify({'msg': "ok"}), 200
                else:
                    return jsonify({
                        'msg': "empty_field error"
                    }), 401
            else:
                return jsonify({
                    'msg': "not found"
                }), 404

        else:
            return jsonify({
                'msg': "adm_id missing"
            }), 400


@tdau.route('/main')
def main():
    lang = request.args.get('lang')
    if lang == 'uz':
        content = [x.format_uz() for x in News.query.all()], \
                  [x.format()for x in University_foreign.query.all()], [x.format_uz() for x in Billboard.query.all()]
    #  \[x.format() for x in Billboard.query.all()]
    if lang == 'ru':
        content = [x.format_ru() for x in News.query.all()], \
                  [x.format() for x in University_foreign.query.all()], [x.format_ru() for x in Billboard.query.all()]

    if lang == 'en':
        content = [x.format_en() for x in News.query.all()], \
                  [x.format() for x in University_foreign.query.all()], [x.format_en() for x in Billboard.query.all()]

    if lang == None:
        content = [x.format() for x in News.query.all()], \
                  [x.format() for x in University_foreign.query.all()], [x.format() for x in Billboard.query.all()]

    return jsonify(content)

def pic_save(model, pic):
    # Grab Image name
    pic_filename = secure_filename(model.filename)

    # Set UUID
    pic_name = str(uuid.uuid1()) + "_" + pic_filename

    # Save That Image
    saver = pic

    # Change it to a string to save to db
    model = pic_name

    full_path = os.path.join(current_app.root_path, 'static', 'uploads', 'images')
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    saver.save(os.path.join(full_path, pic_name))
    return model


@tdau.route('/add_news', methods=['POST', 'GET'])
@token_required
def add_news(с):
    if request.method == 'POST':
        picture1 = request.files.get('picture_1')
        picture2 = request.files.get('picture_2')
        video = request.files.get('video')
        file = request.files.get('file')
        video_link = request.form.get('video')
        content = News(title_news_ru=request.form.get('title_ru'), title_news_uz=request.form.get('title_uz'),
                       title_news_en=request.form.get('title_en'),
                       about_uz_2=request.form.get('about_uz'), about_ru_2=request.form.get('about_ru'),
                       about_en_2=request.form.get('about_en'), picture_news='pic')

        db.session.add(content)
        db.session.flush()

        if picture1 and allowed_pic(picture1.filename):
            content.picture_news = save_picture(picture1, content.id, 'news_img_1')

        if picture2 and allowed_pic(picture2.filename):
            content.picture_news_555 = save_picture(picture2, content.id, 'news_img_2')
        if video and allowed_pic(video.filename):
            content.video = save_picture(video, content.id, 'news_video')
        if video_link:
         content.video = video_link

        if file:
            content.file = save_picture(file, content.id, 'news_file')


        db.session.commit()

        titles = request.form.get('titles_uz')
        titles = eval(titles)
        for i in titles:
            t = Text_ForNews_Uz(title_or_info=i["title"],
                               text=i["text"], fordegree_id=content.id)
            db.session.add(t)
            db.session.commit()

        titles = request.form.get('titles_ru')
        titles = eval(titles)
        for i in titles:
            t = Text_ForNews_Ru(title_or_info=i["title"],
                               text=i["text"], fordegree_id=content.id)
            db.session.add(t)
            db.session.commit()

        titles = request.form.get('titles_en')
        titles = eval(titles)
        for i in titles:
            t = Text_ForNews_En(title_or_info=i["title"],
                               text=i["text"], fordegree_id=content.id)
            db.session.add(t)
            db.session.commit()
        return jsonify({'msg': 'added!'})




@tdau.route('/delete_news')
@token_required
def delete_news(c):
    id = request.args.get('id')
    post_to_delete = News.query.get_or_404(id)

    if post_to_delete.picture_news != None and post_to_delete.picture_news_555 != None:
        db.session.delete(post_to_delete)
        full_path = os.path.join(current_app.root_path, 'static', 'news', str(post_to_delete.id))
        shutil.rmtree(full_path)
        db.session.commit()
        return jsonify({'msg': 'deleted!'}, 200)

    db.session.delete(post_to_delete)
    db.session.commit()

    return jsonify({"msg": "Done"})


@tdau.route('/delete_admission')
@token_required
def delete_admission_foreign(c):
    id = request.args.get('id')
    adm = Admission_Foreign.query.get_or_404(id)

    db.session.delete(adm)
    db.session.commit()

    return jsonify({"msg": "Done"})


@tdau.route('/update_news', methods=['POST', 'GET'])
@token_required
def update_newspic(с):
    if request.method == 'POST':

        id = request.form.get('id')
        pic_edit = News.query.get_or_404(id)

        pic_edit.title_news_uz = request.form.get('title_uz')
        pic_edit.title_news_ru = request.form.get('title_ru')
        pic_edit.title_news_en = request.form.get('title_en')
        pic_edit.about_uz_2 = request.form.get('about_uz')
        pic_edit.about_en_2 = request.form.get('about_en')
        pic_edit.about_ru_2 = request.form.get('about_ru')
        picture1 = request.files.get('picture_1')
        picture2 = request.files.get('picture_2')
        video = request.files.get('videos')
        file = request.files.get('file')
        video_link = request.form.get('videos')

        if picture1 and allowed_pic(picture1.filename):
            pic_edit.picture_news = save_picture(picture1, pic_edit.id, 'news_img_1')

        if picture2 and allowed_pic(picture2.filename):
            pic_edit.picture_news_555 = save_picture(picture2, pic_edit.id, 'news_img_2')
        if video and allowed_pic(video.filename):
            pic_edit.video = save_picture(video, pic_edit.id, 'news_video')
        if video_link:
            pic_edit.video = video_link

        if file:
            pic_edit.file = save_picture(file, pic_edit.id, 'news_file')

        db.session.commit()

        if request.form.get("titles_uz"):
            titles = request.form.get("titles_uz")

            titles = eval(titles)
            if len(titles) > 0:
                for j in Text_ForNews_Uz.query.filter_by(fordegree_id=id).all():
                    db.session.delete(j)
                    db.session.commit()
                for i in titles:
                    db.session.add(Text_ForNews_Uz(
                        fordegree_id=pic_edit.id, title_or_info=i['title'], text=i['text']))
                    db.session.commit()
        if request.form.get("titles_ru"):
            titles = request.form.get("titles_ru")

            titles = eval(titles)
            if len(titles) > 0:
                for j in Text_ForNews_Ru.query.filter_by(fordegree_id=id).all():
                    db.session.delete(j)
                    db.session.commit()
                for i in titles:
                    db.session.add(Text_ForNews_Ru(
                        fordegree_id=pic_edit.id, title_or_info=i['title'], text=i['text']))
                    db.session.commit()

                if request.form.get("titles_en"):
                    titles = request.form.get("titles_en")

                    titles = eval(titles)
                    if len(titles) > 0:
                        for j in Text_ForNews_En.query.filter_by(fordegree_id=id).all():
                            db.session.delete(j)
                            db.session.commit()
                        for i in titles:
                            db.session.add(Text_ForNews_En(
                                fordegree_id=pic_edit.id, title_or_info=i['title'], text=i['text']))
                            db.session.commit()
        return jsonify({'msg': 'updated'})


@tdau.route("/list_admissions", methods=['GET'])
def select_universities():
    univer_id = request.args.get('university_id')
    if univer_id:
        univer = Admission_Foreign.query.filter(
            Admission_Foreign.university_id == univer_id).all()
        print(univer, flush=True)
        res = [x.format2() for x in Admission_Foreign.query.filter(
            Admission_Foreign.university_id == univer_id).all()]
    else:
        res = [x.format2() for x in University_foreign.query.all()]
    return jsonify(res)


@tdau.route("/admission_by_id")
@token_required
def admission_read(с):
    adm_id = request.args.get('adm_id')
    adm = Admission_Foreign.query.get_or_404(adm_id)
    data = adm.format()
    data['adm_status'] = data['status']
    print("adm.attaches is ", adm.attaches)
    for i in adm.attaches:
        if i.info == 'recommendation_second':
            data['recommendation_second'] = i.path
        elif i.info == 'recommendation':
            data['recommendation'] = i.path
        elif i.info == 'resume':
            data['resume'] = i.path
        elif i.info == 'essay':
            data['essay'] = i.path
        elif i.info == 'recommendation':
            data['recommendation'] = i.path
        elif i.info == 'qualification_diploma':
            data['qualification_diploma'] = i.path
        elif i.info == 'qualification_info':
            data['qualification_info'] = i.path
        elif i.info == 'personal image':
            data['personal_image'] = i.path
    print('data is ', data)
    return jsonify(data)


@tdau.route("/accept_reject_admission", methods=['POST'])
@token_required
def accept_reject_admission(с):
    adm_id = request.form.get('adm_id')
    accept = int(request.form.get('accept_or_reject'))
    adm = Admission_Foreign.query.get_or_404(adm_id)
    if accept:
        adm.status = 2
    elif not accept:
        adm.status = 3
        adm.comment = request.form.get('comment')
    db.session.commit()
    return jsonify({"msg": "ok"})


@tdau.route("/admission_form_foreign", methods=['POST', "GET"])
@token_required
def admission_form_foreign(u):
    if request.method == 'GET':
        _user_id = u.id
        adm = Admission_Foreign.query.filter_by(user_id=_user_id).first()
        if adm:
            return jsonify(adm.format()), 200
        else:
            return jsonify({
                'msg': "not found"
            }), 404

    name = request.form.get('name')
    surname = request.form.get('surname')
    middle_name = request.form.get('middle_name')
    birthdate = request.form.get('birthdate')
    gender_id = request.form.get('gender_id')
    passport_number = request.form.get('passport_number')
    passport_expiry = request.form.get('passport_expiry')
    nationality = request.form.get("nationality")
    country_birth = request.form.get("country_birth")
    country_permanent = request.form.get("country_permanent")
    current_country = request.form.get("current_country")
    accept_deadline = request.form.get("accept_deadline")
    aplication_type = request.form.get("aplication_type")
    education_type_id = request.form.get("education_type_id")
    adress1 = request.form.get("adress1")
    adress2 = request.form.get("adress2")
    region = request.form.get("region")
    district = request.form.get("district")
    post_index = request.form.get("post_index")
    post_address1 = request.form.get("post_address1")
    post_address2 = request.form.get("post_address2")

    post_region = request.form.get("post_region")
    post_district = request.form.get("post_district")
    post_index2 = request.form.get("post_index2")
    school = request.form.get("school")
    qualification = request.form.get("qualification")
    qualification2 = request.form.get("qualification2")
    qualification_start = request.form.get("qualification_start")
    qualification_end = request.form.get("qualification_end")
    gpa = request.form.get("GPA")
    comment = request.form.get("comment")
    register_step = request.form.get("register_step")
    phone = request.form.get("phone")
    phone_a = request.form.get("phone_a")
    email = request.form.get("email")
    faculty_id = request.form.get("faculty_id")
    qualification_info = None
    university_id = request.form.get("university_id")
    personal_image = request.files.get("personal_image")
    if not Admission_Foreign.query.filter_by(user_id=u.id).first():
        adm = Admission_Foreign(
            user_id=u.id,
            email=u.email,
            phone=u.phone,
            status=4,
            university_id=university_id
        )
        db.session.add(adm)
        db.session.commit()
    if 'qualification_info' in request.files:
        qualification_info = request.files["qualification_info"]
    print(request.files)
    qualification_diploma = None
    if 'language_certificate' in request.files:
        qualification_diploma = request.files["language_certificate"]

    # passport = None
    # if 'passport' in request.files:
    #     passport = request.files["passport"]

    # print(passport, flush = True)

    resume = None
    if 'passport' in request.files:
        resume = request.files["passport"]

    print(resume, flush=True)

    recommendation = None
    if 'recommendation' in request.files:
        recommendation = request.files["recommendation"]

    recommendation_second = None
    if 'recommendation_second' in request.files:
        recommendation_second = request.files["recommendation_second"]

    adm = Admission_Foreign.query.filter_by(user_id=u.id).first()

    if adm:
        print("I am in admission inside", flush=True)
        if faculty_id:
            adm.faculty_id = faculty_id
        if name:
            adm.name = name
        if qualification_end:
            adm.qualification_end = qualification_end
        if gender_id:
            adm.gender_id = gender_id
        if qualification_start:
            adm.qualification_start = qualification_start
        if surname:
            adm.surname = surname
        if middle_name:
            adm.middle_name = middle_name
        if birthdate:
            adm.birthdate = birthdate
        if passport_number:
            if Admission_Foreign.query.filter_by(passport_number=passport_number).first():
                return jsonify({"msg": "passport number already exists"}), 409
            adm.passport_number = passport_number
        if university_id:
            adm.university_id = university_id
        if passport_expiry:
            adm.passport_expiry = passport_expiry
        if nationality:
            adm.nationality = nationality
        if country_birth:
            adm.country_birth = country_birth
        if aplication_type:
            adm.aplication_type = aplication_type
        if education_type_id and (education_type_id != 'null' and education_type_id != 'undefined'):
            adm.education_type_id = education_type_id
        if adress1:
            adm.adress1 = adress1
        if adress2:
            adm.adress2 = adress2
        if region:
            adm.region = region
        if district:
            adm.district = district
        if post_index:
            adm.post_index = post_index
        if post_address1:
            adm.post_adress1 = post_address1
        if post_address2:
            adm.post_adress2 = post_address2
        if post_region:
            adm.post_region = post_region
        if post_district:
            adm.post_district = post_district
        if post_index2:
            adm.post_index_2 = post_index2
        if school:
            adm.school = school
        if qualification:
            adm.qualification = qualification
        if qualification2:
            adm.qualification2 = qualification2
        if gpa:
            adm.gpa = gpa
        if comment:
            adm.comment = comment
        if country_permanent:
            adm.country_permanent = country_permanent

        if current_country:
            adm.current_country = current_country

        if accept_deadline:
            adm.accept_deadline = accept_deadline

        if register_step:
            adm.registrater_step = register_step

        if phone:
            adm_p = Admission_Foreign.query.filter_by(phone=phone).first()
            if adm_p:
                return jsonify({
                    'msg': "phone is already token"
                }), 400
            else:
                adm.phone = phone

        if phone_a:
            adm.phone_a = phone_a

        if email:

            adm_e = Admission_Foreign.query.filter_by(email=email).first()
            if adm_e:
                return jsonify({
                    'msg': "email is already token"

                }), 400
            else:
                adm.email = email

        if qualification_info:
            if Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id,
                                                  info="qualification info").first():
                os.remove((Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id,
                                                              university_foreign_id=adm.university_id,
                                                              info="qualification info").first().path).replace('\\',
                                                                                                               '/'))
                Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id,
                                                   info="qualification info").delete()
                db.session.commit()
            adm_att = Adm_Attach_Foreign(
                admission_foreign_id=adm.id,
                university_foreign_id=adm.university_id,
                info="qualification info",
                path=hash_and_save(qualification_info, 'admission'),
            )
            db.session.add(adm_att)
            db.session.commit()
            print("qualification_info saved")
            print(adm_att.format())

        if qualification_diploma:
            if Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id,
                                                  info="language certificate").first():
                os.remove((Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id,
                                                              university_foreign_id=adm.university_id,
                                                              info="language certificate").first().path).remove('\\',
                                                                                                                '/'))
                Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id,
                                                   info="language certificate").delete()
                db.session.commit()
            adm_att = Adm_Attach_Foreign(

                admission_foreign_id=adm.id,
                university_foreign_id=adm.university_id,
                info="language certificate",
                path=hash_and_save(qualification_diploma, 'admission'),

            )
            db.session.add(adm_att)
            db.session.commit()

        # if passport:
        #     print('Asadbek1', flush= True)
        #     if Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="passport").first():
        #         os.remove((Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="passport").first().path).replace('\\','/'))
        #         Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="passport").delete()
        #         db.session.commit()
        #     adm_att = Adm_Attach_Foreign(

        #         admission_foreign_id=adm.id,
        #         university_foreign_id=adm.university_id,
        #         info="passport",
        #         path=hash_and_save(passport, 'admission'),
        #     )
        #     print('Asadbek', flush= True)
        #     db.session.add(adm_att)
        #     db.session.commit()
        print("SSSSSSSSS", flush=True)
        if resume:
            print('Oneni blat', flush=True)
            if Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id,
                                                  info="passport").first():
                print(Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id,
                                                         university_foreign_id=adm.university_id,
                                                         info="passport").first().path, flush=True)
                os.remove(Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id,
                                                             university_foreign_id=adm.university_id,
                                                             info="passport").first().path.replace('\\', '/'))
                Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id,
                                                   info="passport").delete()
                db.session.commit()
            adm_att = Adm_Attach_Foreign(
                admission_foreign_id=adm.id,
                university_foreign_id=adm.university_id,
                info="passport",
                path=hash_and_save(resume, 'admission'),
            )
            db.session.add(adm_att)
            db.session.commit()
        else:
            print('aeweaweaweaweawe', flush=True)

        if recommendation:
            if Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id,
                                                  info="recommendation").first():
                os.remove(Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id,
                                                             university_foreign_id=adm.university_id,
                                                             info="recommendation").first().path.replace('\\', '/'))
                Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id,
                                                   info="recommendation").delete()
                db.session.commit()
            adm_att = Adm_Attach_Foreign(
                admission_foreign_id=adm.id,
                university_foreign_id=adm.university_id,
                info="recommendation",
                path=hash_and_save(recommendation, 'admission'),

            )
            db.session.add(adm_att)
            db.session.commit()
        if recommendation_second:
            if Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id,
                                                  info="recommendation second").first():
                os.remove(Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id,
                                                             university_foreign_id=adm.university_id,
                                                             info="recommendation second").first().path.replace('\\',
                                                                                                                '/'))
                Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id,
                                                   info="recommendation second").delete()
                db.session.commit()

            adm_att = Adm_Attach_Foreign(
                admission_foreign_id=adm.id,
                university_foreign_id=adm.university_id,
                info="recommendation second",
                path=hash_and_save(recommendation_second, 'admission'),
            )
            db.session.add(adm_att)
            db.session.commit()
        if personal_image:
            if Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id,
                                                  info="personal image").first():
                pp = Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id,
                                                        university_foreign_id=adm.university_id,
                                                        info="personal image").first().path.replace('\\', '/')
                try:
                    with open(pp, 'rb') as f:
                        pass
                    os.remove(pp)
                except:
                    pass
                # os.remove(pp)
                # os.remove("%s"%Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="personal image").first().path)
                Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id,
                                                   info="personal image").delete()
                db.session.commit()

            adm_att = Adm_Attach_Foreign(
                admission_foreign_id=adm.id,
                university_foreign_id=adm.university_id,
                info="personal image",
                path=hash_and_save(personal_image, 'admission'),
            )
            db.session.add(adm_att)
            db.session.commit()

        db.session.commit()
        return jsonify({'msg': "ok"}), 200
    else:
        print("wewew")
        return jsonify({
            'msg': "not found"
        }), 404


@tdau.route("/admission_confirm_foreign", methods=['POST'])
@token_required
def admission_confirm_foreign(u):
    if request.method == 'POST':
        print("I am here 1")
        adm_id = request.form.get("adm_id")
        if adm_id:
            print("I am here 2")
            adm = Admission_Foreign.query.get(adm_id)

            if adm:
                print("I am here 3")
                if adm.name != null and adm.name != null and adm.surname != null and adm.middle_name != null and adm.birthdate != null and adm.passport_number != null and adm.passport_expiry != null and adm.gender_id != null and adm.nationality != null and adm.country_birth != null and adm.aplication_type != null and adm.education_type_id != null and adm.adress1 != null and adm.region != null and adm.district != null and adm.school != null and adm.qualification != null and adm.country_permanent != null and adm.current_country != null and adm.accept_deadline != null:
                    print("I am here 4")

                    adm.status = 1

                    adm.register_step = 9
                    db.session.commit()
                    return jsonify({'msg': "ok"}), 200
                else:
                    return jsonify({

                        'msg': "empty_field error"
                    }), 401

            else:
                return jsonify({
                    'msg': "not found"
                }), 404

        else:
            return jsonify({
                'msg': "adm_id missing"
            }), 400


@tdau.route("/education_type_foreign", methods=['GET'])
def education_type_foreign():
    if request.method == 'GET':
        sts = [x.format() for x in Education_type_foreign.query.all()]
        return jsonify(sts)


@tdau.route("/faculties_foreign", methods=['GET'])
def read_faculties_foreign():
    if request.method == 'GET':
        sts = [x.format() for x in Faculty_foreign.query.all()]
        return jsonify(sts)


@tdau.route("/faculties_foreign_by_id", methods=['POST'])
def faculties_foreign_by_id():
    id = request.form.get("id")
    print(id)
    sts = University_foreign.query.get_or_404(id).format()
    return jsonify(sts)


@tdau.route("/admission_foreign", methods=['GET'])
@token_required
def admission_foreign(u):
    if request.method == 'GET':
        adm = Admission_Foreign.query.filter_by(user_id=u.id).first()

        if adm:
            return jsonify({
                'msg': "ok",
                'admission': adm.format()
            }), 200
        return jsonify({
            'msg': "not found"
        }), 404


@tdau.route("/get_foreign_universities")
def get_foreign_universities():
    lang = request.args.get('lang')

    if lang == 'uz':
        return jsonify({"all": [x.format_uz() for x in University_foreign.query.all()]})
    if lang == 'ru':
        return jsonify({"all": [x.format_ru() for x in University_foreign.query.all()]})
    if lang == 'en':
        return jsonify({"all": [x.format_en() for x in University_foreign.query.all()]})

    return jsonify({"all": [x.format() for x in University_foreign.query.all()]})


@tdau.route("/add/faculty_foreign")
@token_required
def add_faculty_foreign(c):
    f = Faculty_foreign()
    f.name = request.form.get('name')
    f.code = request.form.get('code')
    f.university_id = request.form.get('university_id')
    db.session.add(f)
    db.session.commit()
    return jsonify({"msg": "ok"}), 200


@tdau.route("/add/edu_types_foreign")
@token_required
def add_edu_types_foreign(c):
    f = Education_type_foreign()
    f.name = request.form.get('name')
    db.session.add(f)
    db.session.commit()
    return jsonify({"msg": "ok"}), 200


# @tdau.route("/add/university_foreign", methods=['POST'])
# @token_required
# def add_university_foreign(с):
#     u = University_foreign()
#     u.title_uz = request.form.get('title_uz')
#     u.title_ru = request.form.get('title_ru')
#     u.title_en = request.form.get('title_en')
#     u.description_uz = request.form.get('description_uz')
#     u.description_en = request.form.get('description_en')
#     u.description_ru = request.form.get('description_ru')
#     u.logo = 'none'
#     u.picture = 'none'
#     u.picture_desc = 'none'
#     u.video = 'none'
#     db.session.add(u)
#     db.session.commit()
#     logos = request.files.get('picture_logo')
#     picture = request.files.get('picture')
#     picture_desc = request.files.get('picture_desc')
#     if request.files.get('videos'):
#         video = request.files.get('videos')
#         full_path = os.path.join(current_app.root_path, 'static', 'uploads','videos')
#
#         if not os.path.exists(full_path):
#             os.makedirs(full_path)
#         video.save(os.path.join(full_path,
#                                 "university_foreign_id" + str(u.id) + secure_filename(str(video.filename))))
#         u.video =  str(f'static/uploads/images/university_foreign_id' + str(u.id) + secure_filename(str(video.filename)))
#     elif request.form.get('videos'):
#         video_str = request.form.get("videos")
#         u.video = video_str
#
#     full_path = os.path.join(current_app.root_path, 'static', 'uploads', 'images', 'university_foreign_id')
#
#     if not os.path.exists(full_path):
#         os.makedirs(full_path)
#     saved_logo = str(u.id) + secure_filename(str(logos.filename))
#     logos.save(os.path.join(full_path,
#                            "university_foreign_id" + str(u.id) + saved_logo))
#     saved_picture = str(u.id) + secure_filename(str(picture.filename))
#     picture.save(os.path.join(full_path,
#                               "university_foreign_id" + saved_picture))
#     saved_picture_desc = secure_filename(str(picture_desc.filename))
#     picture_desc.save(os.path.join(full_path, "university_foreign_id" +
#                                    str(u.id) + saved_picture_desc))
#
#     u.logo = str(f'static/uploads/images/university_foreign_id' + saved_logo)
#     u.picture =  str(f'static/uploads/images/university_foreign_id' + saved_picture)
#     u.picture_desc =  str(f'static/uploads/images/university_foreign_id' + saved_picture_desc)
#
#     db.session.add(u)
#     db.session.commit()
#     ed_t = Education_type_foreign(name="Bachelor", university_id=u.id)
#     ed_t2 = Education_type_foreign(name="Master", university_id=u.id)
#     db.session.add(ed_t)
#     db.session.add(ed_t2)
#     db.session.commit()
#     titles_uz = request.form.get('titles_uz')
#     # titles = json.loads(titles)
#     titles_uz = eval(titles_uz)
#     for i in titles_uz:
#         t = Text_foreign_uz(title_or_info=i["title"],
#                          text=i["text"], university_id=u.id)
#         db.session.add(t)
#         db.session.commit()
#
#     titles_ru = request.form.get('titles_ru')
#     # titles = json.loads(titles)
#     titles_ru = eval(titles_ru)
#     for i in titles_ru:
#         t = Text_foreign_ru(title_or_info=i["title"],
#                             text=i["text"], university_id=u.id)
#         db.session.add(t)
#         db.session.commit()
#
#     titles_en = request.form.get('titles_en')
#     # titles = json.loads(titles)
#     titles_en = eval(titles_en)
#     for i in titles_en:
#         t = Text_foreign_en(title_or_info=i["title"],
#                             text=i["text"], university_id=u.id)
#         db.session.add(t)
#         db.session.commit()
#
#     return jsonify({"msg": "ok"}), 200


@tdau.route("/add_un_for", methods=['POST'])
@token_required
def add_university_foreign(с):
    uf = University_foreign(title_uz=request.form.get('title_uz'), title_ru=request.form.get('title_ru'),
                            title_en=request.form.get('title_en'), description_uz=request.form.get('description_uz'),
                            description_ru=request.form.get('description_ru'), description_en=request.form.get('description_en'))

    db.session.add(uf)
    db.session.flush()

    logo = request.files.get('logo')
    picture_desc = request.files.get('picture_desc')
    picture = request.files.get('picture')
    video_link = request.form.get('videos')
    video_file = request.files.get('videos')

    if logo and allowed_pic(logo.filename):
        uf.logo = save_picture(logo,  str(uf.id), 'university_foreign_logo')
    if picture_desc and allowed_pic(picture_desc.filename):
        uf.picture_desc = save_picture(picture_desc,  str(uf.id), 'university_foreign_picture_desc')
    if picture and allowed_pic(picture.filename):
        uf.picture = save_picture(picture, str(uf.id), 'university_foreign_picture')
    if video_link:
        uf.video = video_link
    if video_file and allowed_pic(video_file.filename):
        uf.video = save_picture(video_file, str(uf.id), 'video')

    db.session.commit()

    ed_t = Education_type_foreign(name="Bachelor", university_id=uf.id)
    ed_t2 = Education_type_foreign(name="Master", university_id=uf.id)
    db.session.add(ed_t)
    db.session.add(ed_t2)
    db.session.commit()
    titles_uz = request.form.get('titles_uz')
    # titles = json.loads(titles)
    titles_uz = eval(titles_uz)
    for i in titles_uz:
        t = Text_foreign_uz(title_or_info=i["title"],
                         text=i["text"], university_id=uf.id)
        db.session.add(t)
        db.session.commit()

    titles_ru = request.form.get('titles_ru')
    # titles = json.loads(titles)
    titles_ru = eval(titles_ru)
    for i in titles_ru:
        t = Text_foreign_ru(title_or_info=i["title"],
                            text=i["text"], university_id=uf.id)
        db.session.add(t)
        db.session.commit()

    titles_en = request.form.get('titles_en')
    # titles = json.loads(titles)
    titles_en = eval(titles_en)
    for i in titles_en:
        t = Text_foreign_en(title_or_info=i["title"],
                            text=i["text"], university_id=uf.id)
        db.session.add(t)
        db.session.commit()

    return jsonify({"msg": "ok"}), 200


@tdau.route("/edit_un_for", methods=['GET', 'POST'])
@token_required
def edit_university_foreign(c):
    if request.method == 'POST':
        id = request.form.get("id")
        uni = University_foreign.query.get_or_404(id)

        uni.title_uz = request.form.get('title_uz')
        uni.title_ru = request.form.get('title_ru')
        uni.title_en = request.form.get('title_en')
        uni.description_uz = request.form.get('description_uz')
        uni.description_ru = request.form.get('description_ru')
        uni.description_en = request.form.get('description_en')
        uni.video = request.form.get('videos')
        logo = request.files.get('logo')
        video_file = request.files.get('videos')
        picture = request.files.get('picture')
        picture_desc = request.files.get('picture_desc')
        if request.form.get("titles_uz"):
            titles = request.form.get("titles_uz")
            titles = eval(titles)
            if len(titles) > 0:
                for j in Text_foreign_uz.query.filter_by(university_id=id).all():
                    db.session.delete(j)
                    db.session.commit()
                for i in titles:
                    db.session.add(Text_foreign_uz(
                        university_id=uni.id, title_or_info=i['title'], text=i['text']))
                    db.session.commit()
            if request.form.get("titles_ru"):
                titles = request.form.get("titles_ru")
                print("titles in /edit/university_foreign is " + titles)
                titles =eval(titles)
                if len(titles) > 0:
                    for j in Text_foreign_ru.query.filter_by(university_id=id).all():
                        db.session.delete(j)
                        db.session.commit()
                    for i in titles:
                        db.session.add(Text_foreign_ru(
                            university_id=uni.id, title_or_info=i['title'], text=i['text']))
                        db.session.commit()
            if request.form.get("titles_en"):
                titles = request.form.get("titles_en")
                print("titles in /edit/university_foreign is " + titles)
                titles = eval(titles)
                if len(titles) > 0:
                    for j in Text_foreign_en.query.filter_by(university_id=id).all():
                        db.session.delete(j)
                        db.session.commit()
                    for i in titles:
                        db.session.add(Text_foreign_en(
                            university_id=uni.id, title_or_info=i['title'], text=i['text']))
                        db.session.commit()

            if logo and allowed_pic(logo.filename):
                uni.logo = save_picture(logo,  str(uni.id), 'university_foreign_logo')

            if picture and allowed_pic(picture.filename):
                uni.picture = save_picture(picture,  str(uni.id), 'university_foreign_picture')
            if picture and allowed_pic(picture_desc.filename):
                uni.picture_desc = save_picture(picture_desc, str(uni.id), 'university_foreign_picture_desc')
            if video_file and allowed_pic(video_file.filename):
                uni.video = save_picture(video_file, str(uni.id), 'video')
            db.session.commit()

        return jsonify({"msg": "ok"})
    id = request.args.get('id')
    uni = University_foreign.query.get_or_404(id)
    return jsonify(uni.format())


@tdau.route('/delete/university_foreign', methods=['GET'])
@token_required
def delete_university_foreign(c):
    id = request.args.get("id")
    uni = University_foreign.query.get_or_404(id)
    if uni.logo != None and uni.picture != None and uni.picture_desc !=None:
        db.session.delete(uni)
        full_path = os.path.join(current_app.root_path, 'static', 'university_foreign', str(uni.id))
        shutil.rmtree(full_path)
        db.session.commit()
        return jsonify({'msg': 'deleted!'}, 200)
    db.session.delete(uni)
    db.session.commit()
    return jsonify({"msg": "deleted"}, 200)


@tdau.route('/add_billboard', methods=['POST'])
@token_required
def add_billboard(c):
    if request.method == 'POST':
        content = Billboard(title_uz=request.form.get('title_uz'), title_ru=request.form.get('title_ru'), title_en=request.form.get('title_en'), picture=request.files.get(
            'picture'), desc_uz=request.form.get('desc_uz'), desc_en=request.form.get('desc_en'), desc_ru=request.form.get('desc_ru'), date=request.form.get('date'), time=request.form.get('time'))

        # Grab Image name
        pic_filename = secure_filename(content.picture.filename)

        # Set UUID
        pic_name = str(uuid.uuid1()) + "_" + pic_filename

        # Save That Image
        saver = request.files.get('picture')

        # Change it to a string to save to db
        content.picture = pic_name

        db.session.add(content)
        db.session.commit()
        full_path = os.path.join(current_app.root_path, 'static', 'uploads', 'images')
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        saver.save(os.path.join(full_path, pic_name))

        return jsonify({"msg": "ok"})


@tdau.route('/test_billboard', methods=['GET'])
def test_billboard():
    for u in University_foreign.query.all():
        u.logo = u.logo.replace("app/", "", 1)
        u.picture = u.picture.replace("app/", "", 1)
        u.picture_desc = u.picture_desc.replace("app/", "", 1)
        u.video = u.video.replace("app/", "", 1)
        print("ya")
        db.session.commit()
    return jsonify("ya")


@tdau.route('/edit_bill')
def edit_bill():
    id = request.args.get('id')

    bill = Billboard.query.get(id)

    jsonf = {
        'id': bill.id,
        'title_bill_uz': bill.title_uz,
        'title_bill_ru': bill.title_ru,
        'title_bill_en': bill.title_en,
        'date_bill': bill.date,
        'time_bill': bill.time,
        'bill_desc_uz': bill.desc_uz,
        'bill_desc_en': bill.desc_en,
        'bill_desc_ru': bill.desc_ru,
        'picture_bill': f'static/uploads/images/{bill.picture}',

    }

    return jsonify(jsonf)


@tdau.route('/update_billboard', methods=['POST', 'GET'])
def update_billboard():
    if request.method == 'POST':
        id = request.form.get('id')
        bill_edit = Billboard.query.get(id)
        print(bill_edit.id)
        title = request.form.get('title')
        desc = request.form.get('desc')
        date = request.form.get('date')
        time = request.form.get('time')

        bill_edit.title_uz = request.form.get('title_uz')
        bill_edit.title_ru = request.form.get('title_ru')
        bill_edit.title_en = request.form.get('title_en')
        bill_edit.desc_uz = request.form.get('desc_uz')
        bill_edit.desc_ru = request.form.get('desc_ru')
        bill_edit.desc_en = request.form.get('desc_en')
        if date:
            bill_edit.date = request.form.get('date')
        if time:
            bill_edit.time = request.form.get('time')
        if request.files.get('picture'):
            bill_edit.picture = request.files.get('picture')

            # Grab Image name
            pic_filename = secure_filename(bill_edit.picture.filename)

            # Set UUID
            pic_name = str(uuid.uuid1()) + "_" + pic_filename

            # Save That Image
            saver = request.files['picture']

            # Change it to a string to save to db
            bill_edit.picture = pic_name

            db.session.add(bill_edit)
            db.session.commit()
            full_path = os.path.join(current_app.root_path, 'static', 'uploads', 'images')
            if not os.path.exists(full_path):
                os.makedirs(full_path)
            saver.save(os.path.join(full_path, pic_name))

        db.session.add(bill_edit)
        db.session.commit()

        return jsonify({"msg": "Done"})

    return jsonify({"msg": "AddVideo"})


@tdau.route('/delete_bill')
def delete_bill():
    id = request.args.get('id')
    bill_to_delete = Billboard.query.get_or_404(id)

    db.session.delete(bill_to_delete)
    db.session.commit()

    return jsonify({"msg": "Done"})


@tdau.route('/api/stats', methods=['GET'])
def stats():
    # args to dict
    args = request.args.to_dict()
    data = {}
    if "user" in args or "all" in args:
        data['user'] = User.query.all()
    if 'admission_foreign' in args or "all" in args:
        data['admission_foreign'] = Admission_Foreign.query.all()
    if 'university_foreign' in args or "all" in args:
        data['university_foreign'] = University_foreign.query.all()
    if 'billboard' in args or "all" in args:
        data['billboard'] = Billboard.query.all()
    if 'news' in args or "all" in args:
        data['news'] = News.query.all()
    return jsonify(data)


@tdau.route('/excel', methods=['GET'])
def excel():
    uid = request.args.get('uid')

    adm = Admission_Foreign.query.filter_by(university_id=uid, register_step=9).all()

    data = []
    for a in adm:
        data.append(a.excel())
    df = pd.DataFrame(data=data)
    direc = 'uploads'
    path = 'admissions_excel'
    filename = "admissions%s.xlsx" % (uid)
    full = direc + "/" + path + "/" + filename
    df.to_excel(full, index=False)
    return full


@tdau.route("/add_rector_msg", methods=['POST'])
@token_required
def add_rector_msg(c):
    print('I AM HERE')

    # exist = Post.query.first()
    #
    # if exist != None:
    #     db.session.delete(exist)
    #     db.session.commit()

    rector_name = request.form.get('rector_name')
    description = request.form.get('description')
    add_infos = request.form.get('add_infos')
    work_acts = request.form.get('work_acts')
    # add_infos = json.loads(add_infos)
    # work_acts = json.loads(work_acts)
    post = Post(
        rector_name=rector_name,
        description_uz=request.form.get('desc_uz'),
        description_ru=request.form.get('desc_ru'),
        description_en=request.form.get('desc_en')
    )
    db.session.add(post)

    if 'rector_photo' in request.files:
        rector_photo = request.files['rector_photo']
        post.rector_photo = hash_and_save(rector_photo, 'admission')
    if 'photo' in request.files:
        photo = request.files['photo']
        post.photo = hash_and_save(photo, 'admission')

    db.session.commit()

    title_uz = request.form.get('title_uz')
    title_uz = eval(title_uz)
    for add_info in title_uz:
        post_add_info = Additional_Info_Meta_Uz(
            post_id=post.id,
            key=add_info['title'],
            value=add_info['text']
        )
        db.session.add(post_add_info)
        db.session.commit()

    title_ru = request.form.get('title_ru')
    title_ru = eval(title_ru)
    for add_info in title_ru:
        post_add_info = Additional_Info_Meta_Ru(
            post_id=post.id,
            key=add_info['title'],
            value=add_info['text']
        )
        db.session.add(post_add_info)
        db.session.commit()

    title_en = request.form.get('title_en')
    title_en = eval(title_en)
    for add_info in title_en:
        post_add_info = Additional_Info_Meta_En(
            post_id=post.id,
            key=add_info['title'],
            value=add_info['text']
        )
        db.session.add(post_add_info)
        db.session.commit()

    work_uz = request.form.get('work_uz')
    work_uz = eval(work_uz)
    for work_act in work_uz:
        post_work_act = Work_Activity_Meta_Uz(
            post_id=post.id,
            key=work_act['title'],
            value=work_act['text']
        )
        db.session.add(post_work_act)
        db.session.commit()

    work_en = request.form.get('work_en')
    work_en = eval(work_en)
    for work_act in work_en:
        post_work_act = Work_Activity_Meta_Ru(
            post_id=post.id,
            key=work_act['title'],
            value=work_act['text']
        )
        db.session.add(post_work_act)
        db.session.commit()

    work_en = request.form.get('work_en')
    work_en = eval(work_en)
    for work_act in work_en:
        post_work_act = Work_Activity_Meta_En(
            post_id=post.id,
            key=work_act['title'],
            value=work_act['text']
        )
        db.session.add(post_work_act)
        db.session.commit()

    return jsonify({"msg": "ok"})


@tdau.route("/get_rector_msg", methods=['GET'])
def get_rector_msg():
    lang = request.args.get('lang')

    if lang == 'uz':
        last_id = Post.query.order_by(Post.id.desc()).first().id
        post = Post.query.get(last_id).format_uz()
        return jsonify([post])
    if lang == 'ru':
        last_id = Post.query.order_by(Post.id.desc()).first().id
        post = Post.query.get(last_id).format_ru()
        return jsonify([post])
    if lang == 'en':
        last_id = Post.query.order_by(Post.id.desc()).first().id
        post = Post.query.get(last_id).format_en()
        return jsonify([post])
    if lang == None:
        exist = Post.query.order_by(Post.id.desc()).first()
        if exist == None:
            return jsonify([{'msg': 'empty'}])
        last_id = Post.query.order_by(Post.id.desc()).first().id
        post = Post.query.get(last_id).format()
        return jsonify([post])





@tdau.route('/get_faculty', methods=['POST'])
def get_faculty():
    name = request.form.get('type')
    print(name, flush=True)
    facs = [x.syre_format() for x in Faculty_foreign.query.filter_by(code=name).all()]
    return jsonify(facs)


@tdau.route("/add_structure", methods=['POST'])
@token_required
def add_structure(c):
    fullname_uz = request.form.get('fullname')
    # fullname_ru = request.form.get('fullname_ru')
    # fullname_en = request.form.get('fullname_en')
    description_uz = request.form.get('description_uz')
    description_en = request.form.get('description_en')
    description_ru = request.form.get('description_ru')
    role = request.form.get('role')
    email = request.form.get('email')
    phone = request.form.get('phone')
    reception_time = request.form.get('reception_time')

    st = Structure(
        role=role,
        fullname_uz=fullname_uz,
        desc_uz=description_uz,
        desc_ru=description_ru,
        desc_en=description_en,
        email=email,
        phone=phone,
        reception_time=reception_time
    )
    db.session.add(st)

    if 'photo' in request.files:
        photo = request.files['photo']
        st.photo = hash_and_save(photo, 'structure')

    db.session.commit()

    return jsonify({"msg": "ok"})


@tdau.route("/add_rect_structure", methods=['POST'])
@token_required
def add_rect_structure(c):
    fullname_uz = request.form.get('fullname')
    description_uz = request.form.get('description_uz')
    description_en = request.form.get('description_en')
    description_ru = request.form.get('description_ru')
    email = request.form.get('email')
    phone = request.form.get('phone')
    reception_time = request.form.get('reception_time')

    st = Structure(
        role='rector',
        fullname_uz=fullname_uz,
        desc_uz=description_uz,
        desc_ru=description_ru,
        desc_en=description_en,
        email=email,
        phone=phone,
        reception_time=reception_time
    )
    db.session.add(st)

    if 'photo' in request.files:
        photo = request.files['photo']
        st.photo = hash_and_save(photo, 'structure')

    db.session.commit()

    return jsonify({"msg": "ok"})


@tdau.route("/get_structure", methods=['GET'])
def get_structure():
    lang = request.args.get('lang')

    if lang == 'uz':
        st = Structure.query.filter(Structure.role != 'rector').all()
        st = [x.format_uz() for x in st]

        return jsonify(st)

    if lang == 'ru':
        st = Structure.query.filter(Structure.role != 'rector').all()
        st = [x.format_ru() for x in st]
        return jsonify(st)

    if lang == 'en':
        st = Structure.query.filter(Structure.role != 'rector').all()
        st = [x.format_en() for x in st]
        return jsonify(st)

    if lang == None:

        st = Structure.query.filter(Structure.role != 'rector').all()
        st = [x.format() for x in st]

        return jsonify(st)


@tdau.route("/get_rect_structure", methods=['GET'])
def get_rect_structure():


    lang = request.args.get('lang')

    if lang == 'uz':
        last_id = Structure.query.filter_by(role='rector').order_by(Structure.id.desc()).first().id
        st = Structure.query.get(last_id).format_uz()

        return jsonify(st)

    if lang == 'ru':
        last_id = Structure.query.filter_by(role='rector').order_by(Structure.id.desc()).first().id
        st = Structure.query.get(last_id).format_ru()

        return jsonify(st)

    if lang == 'en':
        last_id = Structure.query.filter_by(role='rector').order_by(Structure.id.desc()).first().id
        st = Structure.query.get(last_id).format_en()

        return jsonify(st)

    if lang == None:
        exist = Structure.query.filter_by(role='rector').order_by(Structure.id.desc()).first()
        if  exist == None:
            return jsonify({'msg': 'empty'})

        last_id = Structure.query.filter_by(role='rector').order_by(Structure.id.desc()).first().id

        st = Structure.query.get(last_id).format()

        return jsonify(st)



@tdau.route("/edit_structure", methods=['GET', 'POST'])
@token_required
def edit_structure(c):
    id = int(request.args.get('id'))
    st = Structure.query.get(id)
    if request.method == 'POST':
        if st:
            if st.photo:
                if 'photo' in request.files:
                    photo = request.files['photo']
                    st.photo = hash_and_save(photo, 'structure')

            if st.fullname_uz:
                fullname = request.form.get('fullname')
                st.fullname_uz = fullname

            # if st.fullname_ru:
            #     fullname = request.form.get('fullname_ru')
            #     st.fullname_ru = fullname
            #
            # if st.fullname_en:
            #     fullname = request.form.get('fullname_en')
            #     st.fullname_en = fullname

            if st.desc_uz:
                description = request.form.get('description_uz')
                st.desc_uz = description

            if st.desc_ru:
                description = request.form.get('description_ru')
                st.desc_ru = description

            if st.desc_en:
                description = request.form.get('description_en')
                st.desc_en = description

            if st.email:
                email = request.form.get('email')
                st.email = email

            if st.phone:
                phone = request.form.get('phone')
                st.phone = phone

            if st.reception_time:
                reception_time = request.form.get('reception_time')
                st.reception_time = reception_time

            db.session.commit()

    st = st.format()

    return jsonify(st)


@tdau.route("/delete_structure", methods=['GET'])
@token_required
def delete_structure(c):
    id = int(request.args.get('id'))
    st = Structure.query.filter_by(id=id).delete()

    db.session.commit()

    return jsonify({'msg': 'ok'})


@tdau.route("/write_about_us", methods=['POST'])
@token_required
def write_about_us(c):
    desc1_uz = request.form.get('desc1_uz')
    desc1_ru = request.form.get('desc1_ru')
    desc1_en = request.form.get('desc1_en')
    desc2_uz = request.form.get('desc2_uz')
    desc2_ru = request.form.get('desc2_ru')
    desc2_en = request.form.get('desc2_en')
    title_uz = request.form.get('title_uz')
    title_en = request.form.get('title_en')
    title_ru = request.form.get('title_ru')
    link = request.form.get('link')

    if not About_Page.query.all():
        ap = About_Page(
            desc1_uz=desc1_uz,
            desc1_ru=desc1_ru,
            desc1_en=desc1_en,
            desc2_uz=desc2_uz,
            desc2_en=desc2_en,
            desc2_ru=desc2_ru,
            title_uz=title_uz,
            title_ru=title_ru,
            title_en=title_en,
            link=link
        )
        db.session.add(ap)

    else:
        ap = About_Page.query.first()

        if ap.desc1_uz:
            ap.desc1_uz = desc1_uz

        if ap.desc1_ru:
            ap.desc1_ru = desc1_ru

        if ap.desc1_en:
            ap.desc1_en = desc1_en

        if ap.desc2_uz:
            ap.desc2_uz = desc2_uz

        if ap.desc2_ru:
            ap.desc2_ru = desc2_ru

        if ap.desc2_en:
            ap.desc2_en = desc2_en

        if ap.title_uz:
            ap.title_uz = title_uz

        if ap.title_ru:
            ap.title_ru = title_ru

        if ap.title_en:
            ap.title_en = title_en

        if ap.link:
            ap.link = link

    if 'photo1' in request.files:
        photo = request.files['photo1']
        ap.photo1 = hash_and_save(photo, 'structure')

    if 'photo2' in request.files:
        photo = request.files['photo2']
        ap.photo2 = hash_and_save(photo, 'structure')

    db.session.commit()

    return jsonify({"msg": "ok"})


@tdau.route("/add_branch", methods=['POST'])
@token_required
def add_branch(c):
    name = request.form.get('name')
    desc_uz = request.form.get('desc_uz')
    desc_ru = request.form.get('desc_ru')
    desc_en = request.form.get('desc_en')
    rector_name = request.form.get('rector_name')
    rector_reception_uz = request.form.get('rector_reception_uz')
    rector_reception_ru = request.form.get('rector_reception_ru')
    rector_reception_en = request.form.get('rector_reception_en')
    rector_address_uz = request.form.get('rector_address_uz')
    rector_address_ru = request.form.get('rector_address_ru')
    rector_address_en = request.form.get('rector_address_en')
    rector_phone = request.form.get('rector_phone')
    rector_email = request.form.get('rector_email')

    br = Branch(
        name=name,
        desc_uz=desc_uz,
        desc_ru=desc_ru,
        desc_en=desc_en,
        rector_name=rector_name,
        rector_reception_uz=rector_reception_uz,
        rector_reception_ru=rector_reception_ru,
        rector_reception_en=rector_reception_en,
        rector_address_uz=rector_address_uz,
        rector_address_en=rector_address_en,
        rector_address_ru=rector_address_ru,
        rector_phone=rector_phone,
        rector_email=rector_email
    )
    db.session.add(br)

    if 'photo1' in request.files:
        photo = request.files['photo1']
        br.photo1 = hash_and_save(photo, 'structure')

    if 'photo2' in request.files:
        photo = request.files['photo2']
        br.photo2 = hash_and_save(photo, 'structure')

    if 'logo' in request.files:
        photo = request.files['logo']
        br.logo = hash_and_save(photo, 'structure')

    if 'rector_photo' in request.files:
        photo = request.files['rector_photo']
        br.rector_photo = hash_and_save(photo, 'structure')

    db.session.commit()

    return jsonify({"msg": "ok"})


@tdau.route("/add_prog", methods=['POST'])
@token_required
def add_prog(c):
    name_uz = request.form.get('name_uz')
    name_ru = request.form.get('name_ru')
    name_en = request.form.get('name_en')
    desc_uz = request.form.get('desc_uz')
    desc_en = request.form.get('desc_en')
    desc_ru = request.form.get('desc_ru')

    pr = Programme(
        name_uz=name_uz,
        name_ru=name_ru,
        name_en=name_en,
        desc_ru=desc_ru,
        desc_uz=desc_uz,
        desc_en=desc_en,
    )
    db.session.add(pr)

    if 'photo' in request.files:
        photo = request.files['photo']
        pr.photo = hash_and_save(photo, 'structure')

    db.session.commit()

    return jsonify({"msg": "ok"})


@tdau.route("/add_fac", methods=['POST'])
@token_required
def add_fac(c):
    name_uz = request.form.get('name_uz')
    name_ru = request.form.get('name_ru')
    name_en = request.form.get('name_en')
    desc_uz = request.form.get('desc_uz')
    desc_ru = request.form.get('desc_ru')
    desc_en = request.form.get('desc_en')
    link = request.form.get('link')
    pr_id = request.form.get('pr_id')
    metas_uz = request.form.get('metas_uz')
    metas_uz = eval(metas_uz)
    metas_en = request.form.get('metas_en')
    metas_en = eval(metas_en)
    metas_ru = request.form.get('metas_ru')
    metas_ru = eval(metas_ru)

    fc = Faculty_Data(
        name_uz=name_uz,
        name_ru=name_ru,
        name_en=name_en,
        desc_uz=desc_uz,
        desc_en=desc_en,
        desc_ru=desc_ru,
        link=link,
        programme_id=pr_id
    )
    db.session.add(fc)

    if 'photo' in request.files:
        photo = request.files['photo']
        fc.photo = hash_and_save(photo, 'structure')
        print('FC PHOTO', fc.photo, flush=True)

    db.session.commit()

    for meta in metas_uz:
        fc_meta = Faculty_Data_Meta_Uz(
            faculty_data_id=fc.id,
            key=meta['title'],
            value=meta['text']
        )
        db.session.add(fc_meta)
        db.session.commit()

    for meta in metas_ru:
        fc_meta = Faculty_Data_Meta_Ru(
            faculty_data_id=fc.id,
            key=meta['title'],
            value=meta['text']
        )
        db.session.add(fc_meta)
        db.session.commit()

    for meta in metas_en:
        fc_meta = Faculty_Data_Meta_En(
            faculty_data_id=fc.id,
            key=meta['title'],
            value=meta['text']
        )
        db.session.add(fc_meta)
        db.session.commit()

    db.session.commit()

    return jsonify({"msg": "ok"})


@tdau.route("/about_us", methods=['GET'])
def about_us():
    lang = request.args.get('lang')
    au = About_Page.query.first()

    if lang == 'ru':
        return au.format_ru()

    if lang == 'uz':
        return au.format_uz()

    if lang == 'en':
        return au.format_en()

    if lang == None:
        if au:
            return jsonify(au.format())
    return jsonify({'msg': 'empty'}, 200)


@tdau.route("/all_branches", methods=['GET'])
def all_branches():
    br = Branch.query.all()
    data = []
    for b in br:
        data.append(b.format())

    return jsonify(data)


@tdau.route("/get_branch", methods=['GET'])
def get_branch():
    id = request.args.get('id')
    lang = request.args.get('lang')

    if lang == 'uz':
        br = Branch.query.get(int(id)).format_uz()
        return jsonify(br)
    if lang == 'ru':
        br = Branch.query.get(int(id)).format_ru()
        return jsonify(br)
    if lang == 'en':
        br = Branch.query.get(int(id)).format_en()
        return jsonify(br)
    br = Branch.query.get(int(id)).format()

    return jsonify(br)


@tdau.route("/all_progs", methods=['GET'])
def all_progs():
    pr = Programme.query.all()
    data = []
    for p in pr:
        data.append(p.format())

    return jsonify(data)


@tdau.route("/get_prog", methods=['GET'])
def get_prog():
    id = request.args.get('id')
    lang = request.args.get('lang')
    if lang == 'ru':
        return Programme.query.get(int(id)).format_ru()

    if lang == 'uz':
        return Programme.query.get(int(id)).format_uz()

    if lang == 'en':
        return Programme.query.get(int(id)).format_en()

    pr = Programme.query.get(int(id)).format()

    return jsonify(pr)


@tdau.route("/all_facs", methods=['GET'])
def all_facs():
    lang = request.args.get('lang')
    fc = Faculty_Data.query.all()

    # data = []
    if lang == 'uz':
        # for f in fc:
        #     data.append(f.format_uz())
        return jsonify([ x.format_uz() for x in fc])
    if lang == 'ru':
        # for f in fc:
        #     data.append(f.format_ru())
        return jsonify([x.format_ru() for x in fc])
    if lang == 'en':
        # for f in fc:
        #     data.append(f.format_en())
        return jsonify([x.format_en() for x in fc])
    # for f in fc:
    #     data.append(f.format())

    return jsonify([ x.format() for x in fc])


@tdau.route("/get_fac", methods=['GET'])
def get_fac():
    id = request.args.get('id')
    lang = request.args.get('lang')

    if lang == 'ru':
        fc = Faculty_Data.query.get(int(id)).format_ru()
        return jsonify(fc)

    if lang == 'uz':
        fc = Faculty_Data.query.get(int(id)).format_uz()
        return jsonify(fc)

    if lang == 'en':
        fc = Faculty_Data.query.get(int(id)).format_en()
        return jsonify(fc)

    fc = Faculty_Data.query.get(int(id)).format()

    return jsonify(fc)


@tdau.route("/edit_branch", methods=['POST'])
@token_required
def edit_branch(c):
    id = request.form.get('id')
    rector_email = request.form.get('rector_email')

    br = Branch.query.get(int(id))

    if br.name:
        name = request.form.get('name')
        br.name = name

    if br.desc_uz:
        desc = request.form.get('desc_uz')
        br.desc_uz = desc

    if br.desc_ru:
        desc = request.form.get('desc_ru')
        br.desc_ru = desc

    if br.desc_en:
        desc = request.form.get('desc_en')
        br.desc_en = desc

    if br.rector_name:
        rector_name = request.form.get('rector_name')
        br.rector_name = rector_name

    if br.rector_reception_uz:
        rector_reception = request.form.get('rector_reception_uz')
        br.rector_reception_uz = rector_reception

    if br.rector_reception_ru:
        rector_reception = request.form.get('rector_reception_ru')
        br.rector_reception_ru = rector_reception

    if br.rector_reception_en:
        rector_reception = request.form.get('rector_reception_en')
        br.rector_reception_en = rector_reception

    if br.rector_address_uz:
        rector_address = request.form.get('rector_address_uz')
        br.rector_address_uz = rector_address

    if br.rector_address_ru:
        rector_address = request.form.get('rector_address_ru')
        br.rector_address_ru = rector_address

    if br.rector_address_en:
        rector_address = request.form.get('rector_address_en')
        br.rector_address_en = rector_address

    if br.rector_phone:
        rector_phone = request.form.get('rector_phone')
        br.rector_phone = rector_phone

    if br.rector_email:
        rector_email = request.form.get('rector_email')
        br.rector_email = rector_email

    if br.photo1:
        if 'photo1' in request.files:
            photo = request.files['photo1']
            br.photo1 = hash_and_save(photo, 'structure')

    if br.photo2:
        if 'photo2' in request.files:
            photo = request.files['photo2']
            br.photo2 = hash_and_save(photo, 'structure')

    if br.logo:
        if 'logo' in request.files:
            photo = request.files['logo']
            br.logo = hash_and_save(photo, 'structure')

    if br.rector_photo:
        if 'rector_photo' in request.files:
            photo = request.files['rector_photo']
            br.rector_photo = hash_and_save(photo, 'structure')

    db.session.commit()

    return jsonify({"msg": "ok"})


@tdau.route("/delete_branch", methods=['GET'])
@token_required
def delete_branch(c):
    id = int(request.args.get('id'))
    br = Branch.query.filter_by(id=id).delete()

    db.session.commit()

    return jsonify({'msg': 'ok'})


@tdau.route("/edit_prog", methods=['POST'])
@token_required
def edit_prog(c):
    id = request.form.get('id')
    print(id)
    pr = Programme.query.get(id)

    print(pr.id)

    if pr.name_uz:
        name = request.form.get('name_uz')
        pr.name_uz = name

    if pr.name_ru:
        name = request.form.get('name_ru')
        pr.name_ru = name

    if pr.name_en:
        name = request.form.get('name_en')
        pr.name_en = name

    if pr.desc_uz:
        desc = request.form.get('desc_uz')
        pr.desc_uz = desc

    if pr.desc_ru:
        desc = request.form.get('desc_ru')
        pr.desc_ru = desc

    if pr.desc_en:
        desc = request.form.get('desc_en')
        pr.desc_en = desc

    if pr.photo:
        if 'photo' in request.files:
            photo = request.files['photo']
            pr.photo = hash_and_save(photo, 'structure')

    db.session.commit()

    return jsonify({"msg": "ok"})


@tdau.route("/delete_prog", methods=['GET'])
@token_required
def delete_prog(c):
    id = int(request.args.get('id'))
    pr = Programme.query.filter_by(id=id).delete()

    db.session.commit()

    return jsonify({'msg': 'ok'})


@tdau.route("/edit_fac", methods=['POST'])
@token_required
def edit_fac(c):
    id = request.form.get('id')
    pr_id = request.form.get('pr_id')
    metas_uz = request.form.get('metas_uz')
    metas_uz = eval(metas_uz)
    metas_en = request.form.get('metas_en')
    metas_en = eval(metas_en)
    metas_ru = request.form.get('metas_ru')
    metas_ru = eval(metas_ru)

    fc = Faculty_Data.query.get(int(id))

    if fc.name_uz:
        name = request.form.get('name_uz')
        fc.name_uz = name

    if fc.name_ru:
        name = request.form.get('name_ru')
        fc.name_ru = name

    if fc.name_en:
        name = request.form.get('name_en')
        fc.name_en = name

    if fc.desc_uz:
        desc = request.form.get('desc_uz')
        fc.desc_uz = desc

    if fc.desc_en:
        desc = request.form.get('desc_en')
        fc.desc_en = desc

    if fc.desc_ru:
        desc = request.form.get('desc_ru')
        fc.desc_ru = desc

    if fc.link:
        link = request.form.get('link')
        fc.link = link

    if fc.programme_id:
        pr_id = request.form.get('pr_id')
        fc.programme_id = pr_id

    if fc.photo:
        if 'photo' in request.files:
            photo = request.files.get('photo')
            fc.photo = hash_and_save(photo, 'structure')

    if fc.faculty_data_metas_uz:
        for j in Faculty_Data_Meta_Uz.query.filter_by(faculty_data_id=id).all():
            db.session.delete(j)
            db.session.commit()
        for meta in metas_uz:
            fc_meta = Faculty_Data_Meta_Uz(
                faculty_data_id=fc.id,
                key=meta['title'],
                value=meta['text']
            )
            db.session.add(fc_meta)
            db.session.commit()

    if fc.faculty_data_metas_ru:
        for j in Faculty_Data_Meta_Ru.query.filter_by(faculty_data_id=id).all():
            db.session.delete(j)
            db.session.commit()
        for meta in metas_ru:
            fc_meta = Faculty_Data_Meta_Ru(
                faculty_data_id=fc.id,
                key=meta['title'],
                value=meta['text']
            )
            db.session.add(fc_meta)
            db.session.commit()

    if fc.faculty_data_metas_en:
        for j in Faculty_Data_Meta_En.query.filter_by(faculty_data_id=id).all():
            db.session.delete(j)
            db.session.commit()
        for meta in metas_en:
            fc_meta = Faculty_Data_Meta_En(
                faculty_data_id=fc.id,
                key=meta['title'],
                value=meta['text']
            )
            db.session.add(fc_meta)
            db.session.commit()

    db.session.commit()

    return jsonify({"msg": "ok"})


@tdau.route("/delete_fac", methods=['GET'])
@token_required
def delete_fac(c):
    id = int(request.args.get('id'))
    pr = Faculty_Data.query.filter_by(id=id).delete()

    db.session.commit()

    return jsonify({'msg': 'ok'})


@tdau.route('admin_spawn', methods=['GET'])
def spawn_the_daun():
    username = 'admin'
    pswrd = '6569321John0604'
    admin = User(
        username=username,
        phone='1111',
        email='1111',
        passport_number='1111',
        pnfl='1111'
    )
    admin.set_password(pswrd)
    db.session.add(admin)
    db.session.commit()
    return jsonify('when i was king')


@tdau.route('/send_code', methods=['POST'])
def send_code():
    number = request.form.get('phone')

    usr = User.query.filter_by(phone=number).first()
    if usr:
        session = requests.Session()
        session.auth = ('eijara', "S5Qzy$B$")
        code = random.randint(1000, 9999)
        p = {
            'messages': {
                'recipient': number,
                'message-id': 1,
                'sms': {
                    'originator': '3700',
                    'content': {
                        'text': 'Hi! Your code is ' + str(code) + ' . Please enter it to reset your password.',
                    }
                }
            }
        }
        session.post('http://91.204.239.44/broker-api/send', json=p)
        usr.verify_code = code
        db.session.commit()

        return jsonify({"msg": "success"})

    return jsonify({"msg": "user not found"}), 400


@tdau.route("/reset_password/code", methods=['POST'])
def reset_password_code():
    if request.method == 'POST':
        phone = request.form.get("phone")
        code = request.form.get("code")
        user = User.query.filter_by(phone=phone).first()
        if user:
            if user.verify_code == code:
                user.verify_code = None
                db.session.commit()
                token = jwt.encode({
                    'public_id': user.id,
                    'exp': datetime.datetime.now() + timedelta(days=100)

                }, SECRET_KEY, algorithm="HS256")
                return jsonify(
                    {
                        "token": token,
                        'msg': 'ok'
                    }
                ), 200
            else:
                return jsonify({'msg': 'error code'}), 400
        else:
            return jsonify({'msg': 'error user with this phone not exist'}), 400
    else:
        return jsonify({"message": "Method not allowed"}), 405


@tdau.route("/reset_password", methods=['POST'])
@token_required
def reset_password(c):
    password = request.form.get("password")

    c.set_password(password)
    db.session.commit()

    return jsonify({"msg": "success"})


from .utils import *


@tdau.route('/add_d', methods=['POST'])
@token_required
def addDeegres(c):
    if request.method == 'POST':
        upper_img = request.files.get('upper_img')
        bottom_img = request.files.get('bottom_img')
        req_degree = request.form.get('degree')
        lang = request.form.get('lang')
        exist_degree = Degrees.query.filter_by(degree=req_degree)
        print(lang)
        list_d = []
        for i in exist_degree:
            list_d.append(i)
        print(list_d)

        if len(list_d) > 0:

            exist_degrees = Degrees.query.filter_by(degree=req_degree, language=lang).first()

            if exist_degrees == None:

                exist_degrees = Degrees.query.filter_by(degree=req_degree).first()

            if exist_degrees.degree == 'bachelor' and exist_degrees.language == lang:

                db.session.delete(exist_degrees)
                full_path = os.path.join(current_app.root_path, 'static', 'degrees', str(exist_degrees.id))
                shutil.rmtree(full_path)
                db.session.commit()
            if exist_degrees.degree == 'master'and exist_degrees.language == lang:
                db.session.delete(exist_degrees)
                db.session.delete(exist_degrees)
                full_path = os.path.join(current_app.root_path, 'static', 'degrees', str(exist_degrees.id))
                shutil.rmtree(full_path)
                db.session.commit()
            if exist_degrees.degree == 'phd' and exist_degrees.language == lang:
                db.session.delete(exist_degrees)
                db.session.delete(exist_degrees)
                full_path = os.path.join(current_app.root_path, 'static', 'degrees', str(exist_degrees.id))
                shutil.rmtree(full_path)
                db.session.commit()
        degree = Degrees(
            about=request.form.get('about'), university_name=request.form.get('name'),
            video_link=request.form.get('video'),
            degree=req_degree, language=lang)
        db.session.add(degree)
        db.session.flush()

        if request.files.get('upper_img') and allowed_pic(upper_img.filename):
            degree.upper_img = save_picture(upper_img, degree.id, 'upper_img_page')

        if request.files.get('bottom_img') and allowed_pic(bottom_img.filename):
            degree.bottom_img = save_picture(bottom_img, degree.id, 'bottom_img_page')

        db.session.commit()
        titles = request.form.get('title')
        titles = eval(titles)
        for i in titles:
            t = Text_Fordegrees(title_or_info=i["title"],
                                text=i["text"], fordegree_id=degree.id)
            db.session.add(t)
            db.session.commit()

        return jsonify({'msg': 'Added!'}, 200)


@tdau.route('/get_bl')
def getBL():
    lang = request.args.get('lang')
    bach = Degrees.query.filter_by(degree='bachelor', language=lang).all()

    return jsonify([x.format() for x in bach])


@tdau.route('/get_ml')
def getML():
    lang = request.args.get('lang')
    bach = Degrees.query.filter_by(degree='master', language=lang).all()

    return jsonify([x.format() for x in bach])


@tdau.route('/get_pl')
def getPL():
    lang = request.args.get('lang')
    bach = Degrees.query.filter_by(degree='phd', language=lang).all()

    return jsonify([x.format() for x in bach])


@tdau.route('/get_b')
def getB():


    bach = Degrees.query.filter_by(degree='bachelor').all()

    return jsonify([x.format() for x in bach])


@tdau.route('/get_m')
def getM():
    bach = Degrees.query.filter_by(degree='master').all()

    return jsonify([x.format() for x in bach])


@tdau.route('/get_p')
def getP():
    bach = Degrees.query.filter_by(degree='phd').all()

    return jsonify([x.format() for x in bach])

@tdau.route('/delete_d')
@token_required
def deleteDegree(c):
    id = request.args.get('id')
    degree = Degrees.query.get_or_404(id)
    if degree.bottom_img != None and degree.upper_img != None:
        db.session.delete(degree)
        full_path = os.path.join(current_app.root_path, 'static', 'degrees', str(degree.id))
        shutil.rmtree(full_path)
        db.session.commit()
        return jsonify({'msg': 'deleted'}, 200)
    db.session.delete(degree)
    db.session.commit()
    return jsonify({'msg': 'deleted'}, 200)


@tdau.route('/update_d', methods=['POST', 'GET'])
@token_required
def updateDegree(c):
    upper_img = request.files.get('upper_img')
    bottom_img = request.files.get('bottom_img')

    if request.method == 'POST':
        id = request.form.get('id')
        degree_post = Degrees.query.get_or_404(id)
        # degree.title = request.form.getlist('title')
        # degree.description = request.form.getlist('desc')
        degree_post.about = request.form.get('about')
        degree_post.university_name = request.form.get('name')
        degree_post.video_link = request.form.get('video')
        degree_post.degree = request.form.get('degree')
        degree_post.language = request.form.get('lang')
        if request.files.get('upper_img') and allowed_pic(upper_img.filename):
            degree_post.upper_img = save_picture(upper_img, degree_post.id, 'upper_img_page')

        if request.files.get('bottom_img') and allowed_pic(bottom_img.filename):
            degree_post.bottom_img = save_picture(bottom_img, degree_post.id, 'bottom_img_page')
        db.session.commit()
        if request.form.get("title"):
            titles = request.form.get("title")

            titles = eval(titles)
            if len(titles) > 0:
                for j in Text_Fordegrees.query.filter_by(fordegree_id=id).all():
                    db.session.delete(j)
                    db.session.commit()
                for i in titles:
                    db.session.add(Text_Fordegrees(
                        fordegree_id=degree_post.id, title_or_info=i['title'], text=i['text']))
                    db.session.commit()
        return jsonify({'msg': 'updated'})


@tdau.route('/update_d_get', methods=['POST', 'GET'])
def updateDegree_get():
    id = request.args.get('id')
    degree = Degrees.query.get_or_404(id)
    return degree.format()


@tdau.route('/add_newspage', methods=['POST'])
@token_required
def addNewspage(c):
    img = request.files.get('img')
    # old_page = NewsPage.query.filter_by(id=1).first()
    # if old_page:
    #     db.session.delete(old_page)
    #     db.session.commit()
    news_page = NewsPage(title_uz=request.form.get('title_uz'), title_ru=request.form.get('title_ru'), title_en=request.form.get('title_en'),
                         desc_uz=request.form.get('desc_uz'), desc_ru=request.form.get('desc_ru'), desc_en=request.form.get('desc_en'),
                         page=request.form.get('page'), language=request.form.get('lang'))
    db.session.add(news_page)
    db.session.flush()

    if img and allowed_pic(img.filename):
        news_page.img = save_picture(img, news_page.id, 'news_page')
    db.session.commit()
    return jsonify({'msg': 'added'}, 200)


@tdau.route('/get_newspage')
def getNewspage():
    type = request.args.get('type')
    news_page = NewsPage.query.all()
    card = News2.query.all()
    print(type)
    if str(type) == 'page':
        return jsonify([x.format2() for x in news_page])
    return jsonify([x.format2() for x in card])


@tdau.route('/update_newspage', methods=['POST'])
@token_required
def updateNewsPage(c):
    id = request.form.get('id')
    img = request.files.get('img')
    news_page = NewsPage.query.get(id)

    news_page.title_uz = request.form.get('title_uz')
    news_page.title_ru = request.form.get('title_ru')
    news_page.title_en = request.form.get('title_en')

    news_page.desc_uz = request.form.get('desc_uz')
    news_page.desc_ru = request.form.get('desc_ru')
    news_page.desc_en = request.form.get('desc_en')
    news_page.page = request.form.get('page')
    # news_page.language = request.form.get('lang')
    if img and allowed_pic(img.filename):
        news_page.img = save_picture(img, news_page.id, 'news_page')
    db.session.commit()
    return jsonify({'msg': 'updated!'}, 200)

@tdau.route('/update_np_get')
def UpdateNpGet():
    id = request.args.get('id')
    page = NewsPage.query.get(id)

    return page.updateGet()

@tdau.route('/delete_newspage')
@token_required
def delete_newspage(c):
    id = request.args.get('id')
    news_page = NewsPage.query.get(id)
    if news_page.img != None:
        db.session.delete(news_page)
        full_path = os.path.join(current_app.root_path, 'static', 'news_page', str(news_page.id))
        shutil.rmtree(full_path)
        db.session.commit()
        return jsonify({'msg': 'deleted!'}, 200)
    db.session.delete(news_page)
    db.session.commit()
    return jsonify({'msg': 'deleted!'}, 200)


# def inputFilter(filter_name):
#     return filter_name


@tdau.route('/conferences', methods=['GET'])
def conferences():
    lang = request.args.get('lang')
    pages = NewsPage.query.filter_by(page='conference').all()
    list_pages = []
    print(list_pages)
    for page in pages:
        list_pages.append(page.id)
    print(list_pages)
    last_page = list_pages[-1]
    print(last_page)
    new_page = NewsPage.query.get(last_page)
    if lang == 'uz':
        return new_page.format_uz(new_page.page, lang)
    if lang == 'ru':
        return new_page.format_ru(new_page.page, lang)
    if lang == 'en':
        return new_page.format_en(new_page.page, lang)
    if lang == None:
        return new_page.format(new_page.page, lang)

@tdau.route('/science', methods=['GET'])
def science():
    lang = request.args.get('lang')
    pages = NewsPage.query.filter_by(page='science').all()
    list_pages = []
    for page in pages:
        list_pages.append(page.id)
    print(list_pages)
    last_page = list_pages[-1]
    print(last_page)
    new_page = NewsPage.query.get(last_page)
    if lang == 'uz':
        return new_page.format_uz(new_page.page, lang)
    if lang == 'ru':
        return new_page.format_ru(new_page.page, lang)
    if lang == 'en':
        return new_page.format_en(new_page.page, lang)
    if lang == None:
        return new_page.format(new_page.page, lang)


@tdau.route('/scientific', methods=['GET'])
def scientific():
    lang = request.args.get('lang')
    pages = NewsPage.query.filter_by(page='scientific').all()
    list_pages = []
    for page in pages:
        list_pages.append(page.id)
    print(list_pages)
    last_page = list_pages[-1]
    print(last_page)
    new_page = NewsPage.query.get(last_page)
    if lang == 'uz':
        return new_page.format_uz(new_page.page, lang)
    if lang == 'ru':
        return new_page.format_ru(new_page.page, lang)
    if lang == 'en':
        return new_page.format_en(new_page.page, lang)
    if lang == None:
        return new_page.format(new_page.page, lang)


@tdau.route('/innovation', methods=['GET'])
def innovation():
    lang = request.args.get('lang')
    pages = NewsPage.query.filter_by(page='innovation').all()
    list_pages = []
    for page in pages:
        list_pages.append(page.id)
    print(list_pages)
    last_page = list_pages[-1]
    print(last_page)
    new_page = NewsPage.query.get(last_page)
    if lang == 'uz':
        return new_page.format_uz(new_page.page, lang)
    if lang == 'ru':
        return new_page.format_ru(new_page.page, lang)
    if lang == 'en':
        return new_page.format_en(new_page.page, lang)
    if lang == None:
        return new_page.format(new_page.page, lang)


@tdau.route('/dev', methods=['GET'])
def dev():
    lang = request.args.get('lang')
    pages = NewsPage.query.filter_by(page='dev').all()
    list_pages = []
    for page in pages:
        list_pages.append(page.id)
    print(list_pages)
    last_page = list_pages[-1]
    print(last_page)
    new_page = NewsPage.query.get(last_page)
    if lang == 'uz':
        return new_page.format_uz(new_page.page, lang)
    if lang == 'ru':
        return new_page.format_ru(new_page.page, lang)
    if lang == 'en':
        return new_page.format_en(new_page.page, lang)
    if lang == None:
        return new_page.format(new_page.page, lang)


@tdau.route('/add_card', methods=['POST'])
@token_required
def addCard(c):
    upper_img = request.files.get('upper_img')
    bottom_img = request.files.get('bottom_img')
    card = News2(about_uz=request.form.get('about_uz'), about_ru=request.form.get('about_ru'), about_en=request.form.get('about_en'), video_link=request.form.get('video'),
                 name_uz=request.form.get('name_uz'), name_ru=request.form.get('name_ru'), name_en=request.form.get('name_en'),
                 for_page=request.form.get('page'),
                 desc_uz=request.form.get('desc_uz'), desc_ru=request.form.get('desc_ru'), desc_en=request.form.get('desc_en'), language=request.form.get('lang'))

    db.session.add(card)
    db.session.flush()

    if upper_img and allowed_pic(upper_img.filename):
        card.upper_img = save_picture(upper_img, card.id, 'upper_card_page')

    if bottom_img and allowed_pic(bottom_img.filename):
        card.bottom_img = save_picture(bottom_img, card.id, 'bottom_card_page')

    db.session.commit()
    titles = request.form.get('title_uz')
    titles = eval(titles)
    for i in titles:
        t = Text_ForNewsUz(title_or_info=i["title"],
                         text=i["text"], fordegree_id=card.id)
        db.session.add(t)
        db.session.commit()

    titles = request.form.get('title_ru')
    titles = eval(titles)
    for i in titles:
        t = Text_ForNewsRu(title_or_info=i["title"],
                           text=i["text"], fordegree_id=card.id)
        db.session.add(t)
        db.session.commit()

    titles = request.form.get('title_en')
    titles = eval(titles)
    for i in titles:
        t = Text_ForNewsEn(title_or_info=i["title"],
                           text=i["text"], fordegree_id=card.id)
        db.session.add(t)
        db.session.commit()
    return jsonify({'msg': 'added!'})


@tdau.route('/update_card', methods=['POST'])
@token_required
def updateCArd(c):
    id = request.form.get('id')
    upper_img = request.files.get('upper_img')
    bottom_img = request.files.get('bottom_img')
    card = News2.query.get(id)

    card.name_uz = request.form.get('name_uz')
    card.name_ru = request.form.get('name_ru')
    card.name_en = request.form.get('name_en')
    card.about_uz = request.form.get('about_uz')
    card.about_ru = request.form.get('about_ru')
    card.about_en = request.form.get('about_en')
    card.video_link = request.form.get('video')
    card.desc_uz = request.form.get('desc_uz')
    card.desc_ru = request.form.get('desc_ru')
    card.desc_en = request.form.get('desc_en')
    card.for_page = request.form.get('page')
    card.language = request.form.get('lang')

    if upper_img and allowed_pic(upper_img.filename):
        card.upper_img = save_picture(upper_img, card.id, 'upper_card_page')

    if bottom_img and allowed_pic(bottom_img.filename):
        card.bottom_img = save_picture(bottom_img, card.id, 'bottom_card_page')
    db.session.commit()
    if request.form.get("title_uz"):
        titles = request.form.get("title_uz")

        titles = eval(titles)
        if len(titles) > 0:
            for j in Text_ForNewsUz.query.filter_by(fordegree_id=id).all():
                db.session.delete(j)
                db.session.commit()
            for i in titles:
                db.session.add(Text_ForNewsUz(
                    fordegree_id=card.id, title_or_info=i['title'], text=i['text']))
                db.session.commit()
    if request.form.get("title_ru"):
        titles = request.form.get("title_ru")

        titles = eval(titles)
        if len(titles) > 0:
            for j in Text_ForNewsRu.query.filter_by(fordegree_id=id).all():
                db.session.delete(j)
                db.session.commit()
            for i in titles:
                db.session.add(Text_ForNewsRu(
                    fordegree_id=card.id, title_or_info=i['title'], text=i['text']))
                db.session.commit()

            if request.form.get("title_en"):
                titles = request.form.get("title_en")

                titles = eval(titles)
                if len(titles) > 0:
                    for j in Text_ForNewsEn.query.filter_by(fordegree_id=id).all():
                        db.session.delete(j)
                        db.session.commit()
                    for i in titles:
                        db.session.add(Text_ForNewsEn(
                            fordegree_id=card.id, title_or_info=i['title'], text=i['text']))
                        db.session.commit()
    return jsonify({'msg': 'updated'})


@tdau.route('/delete_card')
@token_required
def deleteCard(c):
    id = request.args.get('id')
    card = News2.query.get(id)
    if card.upper_img != None and card.bottom_img != None:
        db.session.delete(card)
        full_path = os.path.join(current_app.root_path, 'static', 'card', str(card.id))
        shutil.rmtree(full_path)
        db.session.commit()
        return jsonify({'msg': 'deleted!'}, 200)
    db.session.delete(card)
    db.session.commit()
    return jsonify({'msg': 'deleted!'}, 200)


@tdau.route('/get_card')
def getCard():
    id = request.args.get('id')
    card = News2.query.get(id)
    cards = News2.query.order_by(func.random()).filter(News2.id != card.id, News2.for_page == card.for_page).limit(3)

    return card.format(cards)


@tdau.route('/update_card_get', methods=['GET'])
def updateCard_get():
    id = request.args.get('id')
    card = News2.query.get_or_404(id)

    return card.format2()

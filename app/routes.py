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
                role_id=9

            )
            db.session.add(role_m)
            db.session.commit()

            code = random.randint(1000,9999)

            session = requests.Session()
            session.auth = ('eijara', "S5Qzy$B$")
            p = {
                'messages' : {
                    'recipient' : phone,
                    'message-id' : 1,
                    'sms' : {
                        'originator' : '3700',
                        'content' : {
                            'text' : 'Hi! Your registration code is ' + str(code) + ' . Please enter it to complete your registration.',
                        }
                    }
                }
            }
            auth = session.post('http://91.204.239.44/broker-api/send',json = p)
            
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
    content = [x.format() for x in News.query.all()], [x.format()
                                                       for x in University_foreign.query.all()], [x.format() for x in Billboard.query.all()]
    #  \[x.format() for x in Billboard.query.all()]

    return jsonify(content)


@tdau.route('/add_news', methods=['POST', 'GET'])
@token_required
def add_news(с):
    if request.method == 'POST':
        content = News(title_news=request.form.get('title_news'),
                       picture_news=request.files.get('picture_news'))

        # Grab Image name
        pic_filename = secure_filename(content.picture_news.filename)

        # Set UUID
        pic_name = str(uuid.uuid1()) + "_" + pic_filename

        # Save That Image
        saver = request.files.get('picture_news')

        # Change it to a string to save to db
        content.picture_news = pic_name

        db.session.add(content)
        db.session.commit()

        saver.save(os.path.join('uploads/images/', pic_name))

        return 'Success adding content_text'
    return jsonify({"msg": "Done"})


@tdau.route('/delete_news')
@token_required
def delete_news(c):
    id = request.args.get('id')
    post_to_delete = News.query.get_or_404(id)

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
        title_news = request.form.get('title')
        if title_news:
            pic_edit.title_news = request.form.get('title')
        # if pic_edit.picture_news != request.files.get('picture_news') and request.files.get('picture_news'):
        if request.files.get('picture_news'):
            pic_edit.picture_news = request.files.get('picture_news')

            # Grab Image name
            pic_filename = secure_filename(pic_edit.picture_news.filename)

            # Set UUID
            pic_name = str(uuid.uuid1()) + "_" + pic_filename

            # Save That Image
            saver = request.files['picture_news']

            # Change it to a string to save to db
            pic_edit.picture_news = pic_name

            db.session.add(pic_edit)
            db.session.commit()
            saver.save(os.path.join('uploads/images/', pic_name))

        db.session.add(pic_edit)
        db.session.commit()
    # else:

        return jsonify({"msg": "OK"})
    return jsonify({"msg": "update_news"})


@tdau.route("/list_admissions", methods=['GET'])
def select_universities():
    univer_id = request.args.get('university_id')
    if univer_id:
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
    print('data is ',data)
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

    adm = Admission_Foreign.query.filter_by(user_id=u.id).first()


    if adm:
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
                return jsonify({"msg": "passport number already exists"})
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
            if Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="qualification info").first():
                os.remove(Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="qualification info").first().path)
                Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="qualification info").delete()
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
            if Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="qualification diploma").first():
                os.remove(Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="qualification diploma").first().path)
                Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="qualification diploma").delete()
                db.session.commit()
            adm_att = Adm_Attach_Foreign(

                admission_foreign_id=adm.id,
                university_foreign_id=adm.university_id,
                info="qualification diploma",
                path=hash_and_save(qualification_diploma, 'admission'),

            )
            db.session.add(adm_att)
            db.session.commit()

        if essay:
            if Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="essay").first():
                os.remove(Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="essay").first().path)
                Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="essay").delete()
                db.session.commit()
            adm_att = Adm_Attach_Foreign(

                admission_foreign_id=adm.id,
                university_foreign_id=adm.university_id,
                info="essay",
                path=hash_and_save(essay, 'admission'),
            )
            db.session.add(adm_att)
            db.session.commit()

        if resume:
            if Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="resume").first():
                os.remove(Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="resume").first().path)
                Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="resume").delete()
                db.session.commit()
            adm_att = Adm_Attach_Foreign(
                admission_foreign_id=adm.id,
                university_foreign_id=adm.university_id,
                info="resume",
                path=hash_and_save(resume, 'admission'),
            )
            db.session.add(adm_att)
            db.session.commit()

        if recommendation:
            if Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="recommendation").first():
                os.remove(Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="recommendation").first().path)
                Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="recommendation").delete()
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
            if Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="recommendation second").first():
                os.remove(Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="recommendation second").first().path)
                Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="recommendation second").delete()
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
            if Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="personal image").first():
                os.remove(Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="personal image").first().path)
                Adm_Attach_Foreign.query.filter_by(admission_foreign_id=adm.id, university_foreign_id=adm.university_id, info="personal image").delete()
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


@tdau.route("/add/university_foreign", methods=['POST'])
@token_required
def add_university_foreign(с):
    u = University_foreign()
    u.title = request.form.get('title')
    u.description = request.form.get('description')
    u.logo = 'none'
    u.picture = 'none'
    u.picture_desc = 'none'
    u.video = 'none'
    db.session.add(u)
    db.session.commit()
    logo = request.files.get('logo')
    picture = request.files.get('picture')
    picture_desc = request.files.get('picture_desc')
    if request.files.get('videos'):
        video = request.files.get('videos')
        video.save(os.path.join('uploads/videos/',
               "university_foreign_id" + str(u.id) + secure_filename(str(video.filename))))
        u.video = str(os.path.join('uploads/videos/',
                  "university_foreign_id" + str(u.id) + secure_filename(str(video.filename))))
    elif request.form.get('videos'):
        video_str = request.form.get("videos")
        u.video = video_str
    logo.save(os.path.join('uploads/images/',
              "university_foreign_id" + str(u.id) + secure_filename(str(logo.filename))))
    picture.save(os.path.join('uploads/images/',
                 "university_foreign_id" + str(u.id) + secure_filename(str(picture.filename))))
    picture_desc.save(os.path.join('uploads/images/', "university_foreign_id" +
                      str(u.id) + secure_filename(str(picture_desc.filename))))
    
    u.logo = str(os.path.join('uploads/images/',
                 "university_foreign_id" + str(u.id) + secure_filename(str(logo.filename))))
    u.picture = str(os.path.join(
        'uploads/images/', "university_foreign_id" + str(u.id) + secure_filename(str(picture.filename))))
    u.picture_desc = str(os.path.join(
        'uploads/images/', "university_foreign_id" + str(u.id) + secure_filename(str(picture_desc.filename))))
    
    db.session.add(u)
    db.session.commit()
    ed_t = Education_type_foreign(name="Bachelour", university_id=u.id)
    ed_t2 = Education_type_foreign(name="Master", university_id=u.id)
    db.session.add(ed_t)
    db.session.add(ed_t2)
    db.session.commit()
    titles = request.form.get('titles')
    titles = json.loads(titles)
    for i in titles:
        t = Text_foreign(title_or_info=i["title"],
                         text=i["text"], university_id=u.id)
        db.session.add(t)
        db.session.commit()

    return jsonify({"msg": "ok"}), 200


@tdau.route("/edit/university_foreign", methods=['GET', 'POST'])
@token_required
def edit_university_foreign(c):
    if request.method == 'POST':
        id = request.form.get("id")
        uni = University_foreign.query.get_or_404(id)
        if request.form.get("title"):
            uni.title = request.form.get("title")
        if request.form.get("picture_desc"):
            uni.picture_desc = request.form.get("picture_desc")
        if request.form.get("description"):
            uni.description = request.form.get("description")
        if request.form.get("titles"):
            titles = request.form.get("titles")
            print("titles in /edit/university_foreign is " + titles)
            titles = json.loads(titles)
            if len(titles) > 0:
                for j in Text_foreign.query.filter_by(university_id=id).all():
                    db.session.delete(j)
                    db.session.commit()
                for i in titles:
                    db.session.add(Text_foreign(
                        university_id=uni.id, title_or_info=i['title'], text=i['text']))
                    db.session.commit()

        if request.files.get("logo"):
            logo = request.files.get("logo")
            logo.save(os.path.join('uploads/images/', "university_foreign_id" +
                      str(uni.id) + secure_filename(str(logo.filename))))
            # delete old logo
            try:
                os.remove(os.path.join('uploads/images/', uni.logo))
            except:
                pass
            uni.logo = str(os.path.join(
                'uploads/images/', "university_foreign_id" + str(uni.id) + secure_filename(str(logo.filename))))
        if request.files.get("picture"):
            picture = request.files.get("picture")
            picture.save(os.path.join('uploads/images/', "university_foreign_id" +
                         str(uni.id) + secure_filename(str(picture.filename))))
            # delete old picture
            try:
                os.remove(os.path.join('uploads/images/', uni.picture))
            except:
                pass
            
            uni.picture = str(os.path.join(
                'uploads/images/', "university_foreign_id" + str(uni.id) + secure_filename(str(picture.filename))))
        if request.files.get("videos"):
            video = request.files.get("videos")
            video.save(os.path.join('uploads/videos/', "university_foreign_id" +
                       str(uni.id) + secure_filename(str(video.filename))))
            # delete old video
            if uni.video != 'none' or not uni.video:
                try:
                    os.remove(os.path.join('uploads/videos/', uni.video))
                except:
                    pass
            uni.video = str(os.path.join(
                'uploads/videos/', "university_foreign_id" + str(uni.id) + secure_filename(str(video.filename))))
        elif request.form.get("videos"):
            video_str = request.form.get("videos")
            uni.video = video_str
        if request.files.get("picture_desc"):
            picture_desc = request.files.get("picture_desc")
            picture_desc.save(os.path.join('uploads/images/', "university_foreign_id" +
                              str(uni.id) + secure_filename(str(picture_desc.filename))))
            #delete old picture_desc
            if uni.picture_desc != 'none' or not uni.picture_desc:
                try:
                    os.remove(os.path.join('uploads/images/', uni.picture_desc))
                except:
                    pass
            uni.picture_desc = str(os.path.join(
                'uploads/images/', "university_foreign_id" + str(uni.id) + secure_filename(str(picture_desc.filename))))
        db.session.commit()
        return jsonify({"msg": "ok"})
    id = request.args.get('id')
    uni = University_foreign.query.get_or_404(id)
    return jsonify(uni.format())


@tdau.route('/delete/university_foreign', methods=['POST'])
@token_required
def delete_university_foreign(c):
    id = request.form.get("id")
    uni = University_foreign.query.get_or_404(id)
    db.session.delete(uni)
    db.session.commit()
    return jsonify({"msg": "ok"})


@tdau.route('/add_billboard', methods=['POST'])
@token_required
def add_billboard(c):
    if request.method == 'POST':
        content = Billboard(title=request.form.get('title'), picture=request.files.get(
            'picture'), desc=request.form.get('desc'), date=request.form.get('date'), time=request.form.get('time'))

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

        saver.save(os.path.join('uploads/images/', pic_name))

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
        'title_bill': bill.title,
        'date_bill': bill.date,
        'time_bill': bill.time,
        'bill_desc': bill.desc,
        'picture_bill': bill.picture,


    }

    return jsonify(jsonf)


@tdau.route('/update_billboard', methods=['POST', 'GET'])
def update_billboard():

    if request.method == 'POST':
        id = request.form.get('id')
        bill_edit = Billboard.query.get_or_404(id)
        title = request.form.get('title')
        desc = request.form.get('desc')
        date = request.form.get('date')
        time = request.form.get('time')
        if title:
            bill_edit.title = request.form.get('title')
        if desc:
            bill_edit.desc = request.form.get('desc')
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
            saver.save(os.path.join('uploads/images/', pic_name))
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

    adm = Admission_Foreign.query.filter_by(university_id=uid, register_step = 9).all()

    data = []
    for a in adm:
        data.append(a.excel())
    df = pd.DataFrame(data=data)
    direc= 'uploads'
    path = 'admissions_excel'
    filename = "admissions%s.xlsx"%(uid)
    full = direc + "/" + path + "/"+ filename
    df.to_excel(full, index=False)
    return full

    
@tdau.route("/add_rector_msg", methods=['POST'])
@token_required
def add_rector_msg(c):
    print('I AM HERE')
    rector_name = request.form.get('rector_name')
    description = request.form.get('description')
    add_infos = request.form.get('add_infos')
    work_acts = request.form.get('work_acts')
    add_infos = json.loads(add_infos)
    work_acts = json.loads(work_acts)
    post = Post(
        rector_name=rector_name,
        description=description
    )
    db.session.add(post)

    if 'rector_photo' in request.files:
        rector_photo = request.files['rector_photo']
        post.rector_photo = hash_and_save(rector_photo, 'admission')
    if 'photo' in request.files:
        photo = request.files['photo']
        post.photo = hash_and_save(photo, 'admission')
    
    db.session.commit()

    for add_info in add_infos:
        post_add_info = Additional_Info_Meta(
            post_id = post.id,
            key = add_info['title'],
            value = add_info['text']
        )
        db.session.add(post_add_info)
        db.session.commit()

    for work_act in work_acts:
        post_work_act = Work_Activity_Meta(
            post_id = post.id,
            key = work_act['title'],
            value = work_act['text']
        )
        db.session.add(post_work_act)
        db.session.commit()
    
    return jsonify({"msg": "ok"})

@tdau.route("/get_rector_msg", methods=['GET'])
def get_rector_msg():
    last_id = Post.query.order_by(Post.id.desc()).first().id
    post = Post.query.get(last_id).format()

    return jsonify([post])


@tdau.route('/get_faculty', methods = ['POST'])
def get_faculty():
    name = request.form.get('type')
    print(name, flush=True)
    facs =[x.syre_format() for x in Faculty_foreign.query.filter_by(code = name).all()]
    return jsonify(facs)

@tdau.route("/add_structure", methods=['POST'])
@token_required
def add_structure(c):
    fullname = request.form.get('fullname')
    description = request.form.get('description')
    role = request.form.get('role')
    email = request.form.get('email')
    phone = request.form.get('phone')
    reception_time = request.form.get('reception_time')

    st = Structure(
        role = role,
        fullname = fullname,
        desc = description,
        email = email,
        phone = phone,
        reception_time = reception_time
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
    fullname = request.form.get('fullname')
    description = request.form.get('description')
    email = request.form.get('email')
    phone = request.form.get('phone')
    reception_time = request.form.get('reception_time')

    st = Structure(
        role = 'rector',
        fullname = fullname,
        desc = description,
        email = email,
        phone = phone,
        reception_time = reception_time
    )
    db.session.add(st)

    if 'photo' in request.files:
        photo = request.files['photo']
        st.photo = hash_and_save(photo, 'structure')

    db.session.commit()

    return jsonify({"msg": "ok"})

@tdau.route("/get_structure", methods=['GET'])
def get_structure():
    st = Structure.query.filter(Structure.role != 'rector').all()
    st = [x.format() for x in st]

    return jsonify(st)

@tdau.route("/get_rect_structure", methods=['GET'])
def get_rect_structure():
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
            
            if st.fullname:
                fullname = request.form.get('fullname')
                st.fullname = fullname
            
            if st.desc:
                description = request.form.get('description')
                st.desc = description
            
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

    return jsonify({'msg' : 'ok'})

@tdau.route("/write_about_us", methods=['POST'])
@token_required
def write_about_us(c):
    desc1 = request.form.get('desc1')
    desc2 = request.form.get('desc2')
    title = request.form.get('title')
    link = request.form.get('link')

    if not About_Page.query.all():
        ap = About_Page(
            desc1 = desc1,
            desc2 = desc2,
            title = title,
            link = link
        )
        db.session.add(ap)

    else:
        ap = About_Page.query.first()
        
        if ap.desc1:
            ap.desc1 = desc1
        
        if ap.desc2:
            ap.desc2 = desc2
        
        if ap.title:
            ap.title = title
        
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
    desc = request.form.get('desc')
    rector_name = request.form.get('rector_name')
    rector_reception = request.form.get('rector_reception')
    rector_address = request.form.get('rector_address')
    rector_phone = request.form.get('rector_phone')
    rector_email = request.form.get('rector_email')

    br = Branch(
        name = name,
        desc = desc,
        rector_name = rector_name,
        rector_reception = rector_reception,
        rector_address = rector_address,
        rector_phone = rector_phone,
        rector_email = rector_email
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
    name = request.form.get('name')
    desc = request.form.get('desc')

    pr = Programme(
        name = name,
        desc = desc
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
    name = request.form.get('name')
    desc = request.form.get('desc')
    link = request.form.get('link')
    pr_id = request.form.get('pr_id')
    metas = request.form.get('metas')
    metas = json.loads(metas)

    fc = Faculty_Data(
        name = name,
        desc = desc,
        link = link,
        programme_id = pr_id
    )
    db.session.add(fc)

    if 'photo' in request.files:
        photo = request.files['photo']
        fc.photo = hash_and_save(photo, 'structure')

    for meta in metas:
        fc_meta = Faculty_Data_Meta(
            faculty_data_id = fc.id,
            key = meta['title'],
            value = meta['text']
        )
        db.session.add(fc_meta)
        db.session.commit()

    db.session.commit()

    return jsonify({"msg": "ok"})

@tdau.route("/about_us", methods=['GET'])
def about_us():
    au = About_Page.query.first().format()

    return jsonify(au)

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
    pr = Programme.query.get(int(id)).format()

    return jsonify(pr)

@tdau.route("/all_facs", methods=['GET'])
def all_facs():
    fc = Faculty_Data.query.all()
    data = []
    for f in fc:
        data.append(f.format())
    
    return jsonify(data)

@tdau.route("/get_fac", methods=['GET'])
def get_fac():
    id = request.args.get('id')
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

    if br.desc:
        desc = request.form.get('desc')
        br.desc = desc

    if br.rector_name:
        rector_name = request.form.get('rector_name')
        br.rector_name = rector_name

    if br.rector_reception:
        rector_reception = request.form.get('rector_reception')
        br.rector_reception = rector_reception

    if br.rector_address:
        rector_address = request.form.get('rector_address')
        br.rector_address = rector_address

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

    return jsonify({'msg' : 'ok'})

@tdau.route("/edit_prog", methods=['POST'])
@token_required
def edit_prog(c):
    id = request.form.get('id')

    pr = Programme.query.get(int(id))

    if pr.name:
        name = request.form.get('name')
        pr.name = name

    if pr.desc:
        desc = request.form.get('desc')
        pr.desc = desc

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

    return jsonify({'msg' : 'ok'})

@tdau.route("/edit_fac", methods=['POST'])
@token_required
def edit_fac(c):
    id = request.form.get('id')
    pr_id = request.form.get('pr_id')
    metas = request.form.get('metas')
    metas = json.loads(metas)

    fc = Faculty_Data.query.get(int(id))

    if fc.name:
        name = request.form.get('name')
        fc.name = name

    if fc.desc:
        desc = request.form.get('desc')
        fc.desc = desc

    if fc.link:
        link = request.form.get('link')
        fc.link = link

    if fc.programme_id:
        pr_id = request.form.get('pr_id')
        fc.programme_id = pr_id

    if fc.photo:
        if 'photo' in request.files:
            photo = request.files['photo']
            fc.photo = hash_and_save(photo, 'structure')

    if fc.faculty_data_metas:
        for meta in metas:
            fc_meta = Faculty_Data_Meta(
                faculty_data_id = fc.id,
                key = meta['title'],
                value = meta['text']
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

    return jsonify({'msg' : 'ok'})
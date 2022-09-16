from app import db
from sqlalchemy.orm import relationship
import datetime
from werkzeug.security import check_password_hash, generate_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20),  nullable=False)
    last_login = db.Column(db.DateTime, nullable = True)
    email = db.Column(db.String)
    passport_number = db.Column(db.String)
    pnfl = db.Column(db.String)


    verify_code = db.Column(db.String, nullable = True)

    created_time = db.Column(db.DateTime, default=datetime.datetime.now)

    role_metas = relationship("Role_meta", cascade = "all,delete", backref = "user", lazy = True)
    admissions = relationship("Admission", cascade="all,delete", backref="user")
    foreign_admissions = relationship("Admission_Foreign", cascade="all,delete", backref="user")
    metas = relationship("UserMeta", cascade="all,delete", backref="user")
    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password, password)
    def format(self):
        return {
            'username': self.username,
            'phone': self.phone,
            'last_login': self.last_login,
            'created_time': self.created_time,
            'attributes': [ {
                'key': meta.format()['key'],
                'value': meta.format()['value'],
            } for meta in self.metas ]
        }
    def __repr__(self) -> str:
        return "%s"%self.username

class Role_meta(db.Model):
    __tablename__ = 'role_meta'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id') ,nullable = False)

    def format(self):
        return{
            "id": self.id,
            "role_id" : self.role_id,
            "role_name" : self.role.name,
            "user_id" : self.user_id
        }


    def login(self):
        return{
            "id": self.id,
            "name" : self.role.name,
        }

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    destination = db.Column(db.String, nullable=True)

    role_meta = relationship("Role_meta", cascade = "delete,all", backref = "role", lazy = True)

    def format(self):
        return{
            "id" : self.id,
            "name" : self.name,
        }

class Admission(db.Model):
    # adm status 1 = waitlist, 2 = accepted, 3 = refused , 4 = registrating
    __tablename__ = 'admission'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=True)
    surname = db.Column(db.String(60), nullable=True)
    middle_name = db.Column(db.String(60), nullable=True)
    birthdate = db.Column(db.Date, nullable=True)
    pnfl = db.Column(db.String, unique=True, nullable=True)
    dtm = db.Column(db.String, unique=True, nullable=True)
    passport_number = db.Column(db.String, nullable = True)
    passport_expiry = db.Column(db.Date, nullable=True)
    phone = db.Column(db.String, nullable=False)
    phone_a = db.Column(db.String, nullable=True)
    email = db.Column(db.String, unique=True, nullable=False)

    faculty_meta_id = db.Column(db.Integer, db.ForeignKey('faculty_meta.id'), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    gender_id = db.Column(db.Integer, db.ForeignKey("gender.id"), nullable=True)
    
    nationality = db.Column(db.String, nullable=True)
    country_birth = db.Column(db.String, nullable=True)
    country_permanent = db.Column(db.String, nullable=True)
    current_country = db.Column(db.String, nullable=True)
    accept_deadline = db.Column(db.String, nullable=True)
    aplication_type = db.Column(db.String, nullable=True)
    education_form_id = db.Column(db.Integer, db.ForeignKey("education_form.id"), nullable=True)
    
    adress1 = db.Column(db.String, nullable=True)
    adress2 = db.Column(db.String, nullable=True)
    region = db.Column(db.String, nullable=True)
    district = db.Column(db.String, nullable=True)
    post_index = db.Column(db.String, nullable=True)
    
    post_adress1 = db.Column(db.String, nullable=True)
    post_adress2 = db.Column(db.String, nullable=True)
    post_region = db.Column(db.String, nullable=True)
    post_district = db.Column(db.String, nullable=True)
    post_index_2 = db.Column(db.String, nullable=True)

    school = db.Column(db.String, nullable=True)
    qualification = db.Column(db.String, nullable=True)
    qualification2 = db.Column(db.String, nullable=True)
    qualification_start = db.Column(db.Date, nullable=True)
    qualification_end = db.Column(db.Date, nullable=True)
    GPA = db.Column(db.String, nullable=True)

    status = db.Column(db.Integer, nullable=False)
    verify_code = db.Column(db.Integer, nullable=True)
    comment = db.Column(db.String, nullable=True)
    register_step = db.Column(db.Integer, nullable=True)
    attaches = relationship('Adm_Attach', cascade="all,delete", backref='admission', lazy=True)

    def notification_1(self):
        return {
            "id": self.id,
            'sts': self.status,
            'step': self.register_step,
        }

    
    def notification_2(self):
        return {
            "id": self.id,
            'sts': self.status,
            "username": self.user.username,
            "password" : self.user.password,
        }

    def notification_3(self):
        return {
            "id": self.id,
            'sts': self.status,
            "comment": self.comment,
        }
    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'middle_name': self.middle_name,
            'birthdate': self.birthdate,
            'pnfl': self.pnfl,
            'dtm': self.dtm,
            'passport_number': self.passport_number,
            'passport_expiry': self.passport_expiry,
            'phone': self.phone,
            'phone_a': self.phone_a,
            'email': self.email,
            "status": self.status,
            "comment": self.comment,
            "register_step": self.register_step,
            "user_id": self.user_id,
            "nationality" : self.nationality,
            "birthdate" : self.birthdate,
            "gender_id" : self.gender_id,
            "country_birth" : self.country_birth,
            "country_permanent" : self.country_permanent,
            "current_country" : self.current_country,
            "accept_deadline" : self.accept_deadline,
            "aplication_type" : self.aplication_type,
            "education_form_id" : self.education_form_id,
            "education_type_id" : self.education_type_id,
            'adress1' : self.adress1,
            'adress2' : self.adress2,
            'region' : self.region,
            'district' : self.district,
            'post_index' : self.post_index,
            'post_adress1' : self.post_adress1,
            'post_adress2' : self.post_adress2,
            'post_region' : self.post_region,
            'post_district' : self.post_district,
            'post_index_2' : self.post_index_2,
            'school' : self.school,
            'qualification' : self.qualification,
            'qualification2' : self.qualification2,
            'GPA' : self.GPA,
            'faculty_id' : self.faculty_id,
            'status' : self.status,
            'attachments': [x.format() for x in self.attaches]
        }

class Adm_Attach(db.Model):
    __tablename__ = "adm_attach"
    id = db.Column(db.Integer, primary_key=True)
    admission_id = db.Column(db.Integer, db.ForeignKey('admission.id'), nullable=False)
    path = db.Column(db.String(200), nullable=False)
    info = db.Column(db.String(200), nullable=True)
    def format(self):
        return {
            'id' : self.id,
            'info': self.info,
            'path' : self.path,
            'ext': self.path.rsplit('.',1)[-1]
    }

class Faculty_meta(db.Model):
    __tablename__ = "faculty_meta"
    id = db.Column(db.Integer, primary_key = True)
    faculty_id = db.Column(db.Integer,db.ForeignKey("faculty.id"),nullable = False)
    speciality_id = db.Column(db.Integer,db.ForeignKey("speciality.id"),nullable = False)
    admissions = relationship("Admission", cascade = "all,delete", backref = "faculty_meta", lazy = True)
    
    def format(self):
        s = db.session.query(Faculty, Speciality.name, Education_type.name).filter(Faculty.id == self.faculty_id, Speciality.id == self.speciality_id).join(Education_type).filter(Education_type.id == Faculty.education_type_id).first()
        return{
            'id' : self.id,
            'faculty_id' : self.faculty_id,
            'speciality_id' : self.speciality_id,
            "faculty_name" : s[0].name,
            "speciality_name" : s[1],
            "education_type_id" : s[0].education_type_id,
            "education_type_name" : s[2],
            
        }
    
class Faculty(db.Model):
    __tablename__ = 'faculty'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    code = db.Column(db.String, nullable=False)
    education_type_id = db.Column(db.Integer, db.ForeignKey("education_type.id"))
    
    faculty_metas = relationship("Faculty_meta", cascade = "all,delete", backref = "faculty", lazy= True)
    
    def format(self):
        s = db.session.query(Education_type.name,Education_type.id).filter(Education_type.id == self.education_type_id).first()
        return {
            "id" : self.id,
            "name" : self.name,
            "code" : self.code,
            "education_type_name" : s[0],
            "education_type_id" : s[1],
        }

    def group_load(self):
        gr_l = [x.group_load() for x in self.groups]
        l_h = 0
        for g_l in gr_l:
            l_h += g_l['lessons_hours']
        return {
            "id" : self.id,
            "faculty" : self.name,
            "group_count": len(self.groups),
            "lessons_hours" :  l_h,
            "group" : gr_l
        }
    
    def group_load_2(self, academic_program_id, academic_plan_id):
        gr_l = [x.group_load(academic_plan_id) for x in self.groups]
        ret_groups = []
        l_h = 0
        for g_l in gr_l:
            if g_l["academic_program_id"] == int(academic_program_id):
                l_h += g_l['lessons_hours']
                ret_groups.append(g_l)
        return {
            "fac_id" : self.id,
            "faculty_name" : self.name,
            "group_count": len(ret_groups),
            "lessons_hours" :  l_h,
            "groups" : ret_groups
        }

    def order_category(self):
        return [x.format() for x in self.departs]
    
    def edm(self):
        return {
            "faculty_id" : self.id,
            "name" : self.name,
            "code" : self.code,
            "fac_groups" : [x.edm() for x in self.groups]
        }
    def __repr__(self) -> str:
        return "%s"%self.name

class Speciality(db.Model):
    __tablename__ = "speciality"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    code = db.Column(db.String)
    

    faculty_metas = relationship("Faculty_meta", cascade = "all,delete", backref = "speciality", lazy = True)
    
    qualifications = relationship("Qualification", backref = "speciality", lazy = True)

    def format(self):
        return{
            "id" : self.id,
            "faculty_metas" : [x.format() for x in self.faculty_metas],
            "name" : self.name,
            "code" : self.code,
        }

class Qualification(db.Model):
    __tablename__ = "qualification"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    code = db.Column(db.String)

    speciality_id = db.Column(db.Integer, db.ForeignKey("speciality.id"), nullable=False)

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'speciality_id': self.speciality_id,
        }

class Education_type(db.Model):
    __tablename__ = "education_type"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    
    faculties = relationship("Faculty", backref = "education_type", lazy = True)

    def read(self):
        return {
            'id': self.id,
            'name': self.name,
        }
    
    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            "faculties": [x.format() for x in self.faculties]
        }

class Education_form(db.Model):
    __tablename__ = "education_form"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    
    admissions = relationship("Admission", cascade = "all,delete", backref = "education_form", lazy = True)
    def format(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class Nationality(db.Model):
    __tablename__ = "nationality"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    
    def format(self):
        return {
            'id': self.id,
            'name': self.name,
        }

class Gender(db.Model):
    __tablename__ = 'gender'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)

    admissions = relationship("Admission", cascade = "all,delete", backref = "gender", lazy =True)
    def format(self):
        return{
            "id" : self.id,
            "name" : self.name
        }

class Country(db.Model):
    __tablename__ = 'country'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)

    def format(self):
        return{
            "id" : self.id,
            "name" : self.name
        }

class Region(db.Model):
    __tablename__ = 'region'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    districts = relationship('District', cascade = "all,delete", backref = "region", lazy = True)
    def format(self):
        return{
            "id" : self.id,
            "name" : self.name
        }

class District(db.Model):
    __tablename__ = 'district'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    reg_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable = False)
    def format(self):
        return{
            "id" : self.id,
            "name" : self.name,
            "reg_id" : self.reg_id,
        }

class UserMeta(db.Model):
    __tablename__ = 'user_meta'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    key = db.Column(db.String(80),  nullable=False)
    value = db.Column(db.String(200),  nullable=False)

    def format(self):
        return {
            'user_id': self.user_id,
            'key': self.key,
            'value': self.value
        }


# class University(db.Model):
#     __table_args__ = {'extend_existing': True} 
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.Text, nullable=False)
#     logo = db.Column(db.Text, nullable=False)
#     picture = db.Column(db.Text, nullable=False)
#     faculty = db.Column(db.Text, nullable=True)
#     ed_types = db.Column(db.Text, nullable=True)
#     # news_id = db.Column(db.Integer, db.ForeignKey('news.id'))

#     infos = relationship('Videocontent', backref='university', cascade ='all,delete')
#     infos2 = relationship('HeaderSecondPage', backref='universityheader', cascade ='all,delete')
#     infos3 = relationship('SecondPagePicture', backref='universitypic', cascade ='all,delete')
#     infos4 = relationship('SecondPageFooterTitle', backref='universityfoottitle', cascade ='all,delete')
#     infos5 = relationship('SecondPageFooterDescription', backref='universityfootdesc', cascade='all,delete')
#     infos6 = relationship('SecondPageFooterAdvantage', backref='universityfootadv', cascade='all,delete')
#     admissioninfo = relationship('Admission', backref='admission', cascade='all,delete')
#     faculties = relationship('Faculty', backref='faculty', cascade='all,delete')
#     education_types = relationship('Education_type', backref='education_type', cascade='all,delete')
#     def format(self):
#         return {
#             'id': self.id,
#             'title': self.title,
#             'logo': self.logo,
#             'picture': self.picture

#         }
#     def test(self):
#         return {
#             'id': self.id,
#             'title': self.title,
#             'logo': self.logo,
#             'picture': self.picture,
#             "child1": [x.format() for x in self.infos],
#             "child2": [x.format() for x in self.infos2],
#             "child3": [x.format() for x in self.infos3],
#             "child4": [x.format() for x in self.infos4],
#             "child5": [x.format() for x in self.infos5],
#             "child6": [x.format() for x in self.infos6]
#         }

class News(db.Model):
    __table_args__ = {'extend_existing': True} 
    id = db.Column(db.Integer, primary_key=True)
    title_news = db.Column(db.String(120), nullable=False)
    picture_news = db.Column(db.String(120), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.datetime.now())
    # universities = db.relationship('Universities', backref='university')
    def format(self):
        return {
            'id': self.id,
            'title_news': self.title_news,
            'picture': self.picture_news,
           'date_posted': self.date_posted

        }

# class Apllication_univer(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
#     university_id = db.Column(db.Integer, db.ForeignKey('university.id'))
#     create_time = db.Column(db.DateTime, default=datetime.datetime.now())
#     status = db.Column(db.String(128), default='new')


# class University(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.Text, nullable=True)
#     logo = db.Column(db.Text, nullable=True)
#     picture = db.Column(db.Text, nullable=True)
#     poster = db.relationship("Posts", backref='poster', lazy=True)
#     about = db.Column(db.Text, nullable=True)
#     videos = db.Column(db.Text, nullable=True)
#     why_us = db.Column(db.Text, nullable=True)
#     title_why_us = db.Column(db.Text, nullable=True)
#     description_why_us = db.Column(db.Text, nullable=True)

#
#
#
#     def format(self):
#         return {
#             'id': self.id,
#             'title': self.title,
#             'logo': self.logo,
#             'picture': self.picture,
#             # 'post_id', self.post_id
#             'video': self.video,
#             'why_us': self.why_us,
#             # 'universities_content': self.universities_content,
#             'about': self.about,
#             'title_why_us': self.title_why_us,
#             'description_why_us': self.description_why_us
#         }

#
# class Posts(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title_news = db.Column(db.String(120))
#     picture_news = db.Column(db.String(120))
#     date_posted = db.Column(db.DateTime, default=datetime.datetime.now())
#
#     post_id = db.Column(db.Integer, db.ForeignKey('university.id'))
#     def format(self):
#         return {
#             "id" : self.id,
#             "created_time" : self.created_time,
#             "key" : self.key,
#             "value" : self.value,
#             "adm_id" : self.adm_id,
#             "creator_id" : self.creator_id,
#             "adm_status" : self.adm.status,
#         }

class Admission_Foreign(db.Model):
    __tablename__ = "admission_foreign"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=True)
    surname = db.Column(db.String(60), nullable=True)
    middle_name = db.Column(db.String(60), nullable=True)
    birthdate = db.Column(db.Date, nullable=True)
    pnfl = db.Column(db.String, unique=True, nullable=True)
    dtm = db.Column(db.String, unique=True, nullable=True)
    passport_number = db.Column(db.String, nullable = True)
    passport_expiry = db.Column(db.Date, nullable=True)
    phone = db.Column(db.String, nullable=False)
    phone_a = db.Column(db.String, nullable=True)
    email = db.Column(db.String, unique=True, nullable=True)


    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty_foreign.id'), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    gender_id = db.Column(db.Integer, db.ForeignKey("gender_foreign.id"))
    nationality = db.Column(db.String, nullable=True)
    country_birth = db.Column(db.String, nullable=True)
    country_permanent = db.Column(db.String, nullable=True)
    current_country = db.Column(db.String, nullable=True)
    accept_deadline = db.Column(db.String, nullable=True)
    aplication_type = db.Column(db.String, nullable=True)
    education_type_id = db.Column(db.Integer, db.ForeignKey("education_type_foreign.id"), nullable=True)
    
    adress1 = db.Column(db.String, nullable=True)
    adress2 = db.Column(db.String, nullable=True)
    region = db.Column(db.String, nullable=True)
    district = db.Column(db.String, nullable=True)
    post_index = db.Column(db.String, nullable=True)
    
    post_adress1 = db.Column(db.String, nullable=True)
    post_adress2 = db.Column(db.String, nullable=True)
    post_region = db.Column(db.String, nullable=True)
    post_district = db.Column(db.String, nullable=True)
    post_index_2 = db.Column(db.String, nullable=True)

    school = db.Column(db.String, nullable=True)
    qualification = db.Column(db.String, nullable=True)
    qualification2 = db.Column(db.String, nullable=True)
    qualification_start = db.Column(db.Date, nullable=True)
    qualification_end = db.Column(db.Date, nullable=True)
    GPA = db.Column(db.String, nullable=True)

    status = db.Column(db.Integer, nullable=False)
    verify_code = db.Column(db.Integer, nullable=True)
    comment = db.Column(db.String, nullable=True)
    register_step = db.Column(db.Integer, nullable=True)
    university_id = db.Column(db.Integer, db.ForeignKey('university_foreign.id'))
    attaches = relationship('Adm_Attach_Foreign', cascade="all,delete", backref='admission_foreign', lazy=True)

    def notification_1(self):
        return {
            "id": self.id,
            'sts': self.status,
            'step': self.register_step,
        }

    
    def notification_2(self):
        return {
            "id": self.id,
            'sts': self.status,
            "username": User.query.get(self.user_id).username,
            "password" : User.query.get(self.user_id).password,
            "comment": self.comment,
        }

    def notification_3(self):
        return {
            "id": self.id,
            'sts': self.status,
            "comment": self.comment,
        }

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'middle_name': self.middle_name,
            'birthdate': str(self.birthdate),
            'pnfl': self.pnfl,
            'dtm': self.dtm,
            'passport_number': self.passport_number,
            'passport_expiry': str(self.passport_expiry),
            'phone': self.phone,
            'phone_a': self.phone_a,
            'email': self.email,
            "status": self.status,
            "comment": self.comment,
            "register_step": self.register_step,
            "user_id": self.user_id,
            "gender_id": self.gender_id,
            "qualification_start": str(self.qualification_start),            
            "qualification_end": str(self.qualification_end),
            "nationality" : self.nationality,
            "birthdate" : self.birthdate,
            "country_birth" : self.country_birth,
            "country_permanent" : self.country_permanent,
            "current_country" : self.current_country,
            "accept_deadline" : self.accept_deadline,
            "aplication_type" : self.aplication_type,
            "education_type_id" : self.education_type_id,
            "education_type_name" : self.education_type_foreign.name if self.education_type_foreign else None,
            'adress1' : self.adress1,
            'adress2' : self.adress2,
            'region' : self.region,
            'district' : self.district,
            'post_index' : self.post_index,
            'post_adress1' : self.post_adress1,
            'post_adress2' : self.post_adress2,
            'post_region' : self.post_region,
            'post_district' : self.post_district,
            'post_index2' : self.post_index_2,
            'school' : self.school,
            'qualification' : self.qualification,
            'qualification2' : self.qualification2,
            'GPA' : self.GPA,
            'faculty_id' : self.faculty_id,
            'faculty_name' : self.faculty_foreign.name if self.faculty_foreign else None,
            'status' : self.status,
            'attachments': [x.format() for x in self.attaches]
        }

    def format2(self):
        return {
            "id" : self.id,
            "name" : self.name,
            "surname" : self.surname,
            "email" : self.email,
            "phone" : self.phone,
            "status" : self.status
        }

    def excel(self):
        return {
            'name': self.name,
            'surname': self.surname,
            'middle_name': self.middle_name,
            '  birthdate  ': str(self.birthdate),
            'pnfl': self.pnfl,
            'dtm': self.dtm,
            'passport_number': self.passport_number,
            'passport_expiry': str(self.passport_expiry),
            'phone': self.phone,
            'phone_2': self.phone_a,
            'email': self.email,
            "status": 'Rejected' if self.status == 2 else 'Accepted',
            "comment_why_rejected": self.comment,
            "gender": self.gender_foreign.name,
            "qualification_start": str(self.qualification_start),            
            "qualification_end": str(self.qualification_end),
            "nationality" : self.nationality,
            "birthdate" : self.birthdate,
            "country_birth" : self.country_birth,
            "country_permanent" : self.country_permanent,
            "current_country" : self.current_country,
            'faculty' : self.faculty_foreign.name,
            "accept_deadline" : self.accept_deadline,
            'program_type' : self.faculty_foreign.code,
            'adress1' : self.adress1,
            'adress2' : self.adress2,
            'region' : self.region,
            'district' : self.district,
            'school' : self.school,
            'qualification' : self.qualification,
            'qualification2' : self.qualification2,
            'GPA' : self.GPA,
            
        }


class Adm_Attach_Foreign(db.Model):
    __tablename__ = "adm_attach_foreign"
    id = db.Column(db.Integer, primary_key=True)
    admission_foreign_id = db.Column(db.Integer, db.ForeignKey('admission_foreign.id'), nullable=False)
    university_foreign_id = db.Column(db.Integer, db.ForeignKey('university_foreign.id'), nullable=False)
    path = db.Column(db.String(200), nullable=False)
    info = db.Column(db.String(200), nullable=True)
    def format(self):
        return {
            'id' : self.id,
            'admission_foreign_id' : self.admission_foreign_id,
            'info': self.info,
            'path' : self.path,

            'filename' : self.path.rsplit('.',1)[-2].rsplit('\\',1)[-1],

            'ext': self.path.rsplit('.',1)[-1]
    }

class Uni_Attach_Foreign(db.Model):
    __tablename__ = "uni_attach_foreign"
    id = db.Column(db.Integer, primary_key=True)
    university_foreign_id = db.Column(db.Integer, db.ForeignKey('university_foreign.id'), nullable=False)
    path = db.Column(db.String(200), nullable=False)
    info = db.Column(db.String(200), nullable=True)
    def format(self):
        return {
            'id' : self.id,
            'university_foreign_id' : self.university_foreign_id,
            'info': self.info,
            'path' : self.path,
            'ext': self.path.rsplit('.',1)[-1]
    }

class Education_type_foreign(db.Model):
    __tablename__ = "education_type_foreign"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)

    university_id = db.Column(db.Integer, db.ForeignKey('university_foreign.id'))
    admissions_foreign = relationship("Admission_Foreign", cascade = "all,delete", backref = "education_type_foreign", lazy = True)

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            "admissions_foreign": [x.format() for x in self.admissions_foreign]
        }

class About_Page(db.Model):
    __tablename__ = 'about_page'
    id = db.Column(db.Integer, primary_key=True)
    photo1 = db.Column(db.String, nullable=False)
    photo2 = db.Column(db.String, nullable=False)
    desc1 = db.Column(db.String, nullable=False)
    desc2 = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)

    def format(self):
        return {
            "photo1" : self.photo1,
            "photo2" : self.photo2,
            "desc1" : self.desc1,
            "desc2" : self.desc2,
            "title" : self.title,
            "link" : self.link
        }

class Branch(db.Model):
    __tablename__ = 'branch'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    photo1 = db.Column(db.String, nullable=False)
    photo2 = db.Column(db.String, nullable=False)
    logo = db.Column(db.String, nullable=False)
    desc = db.Column(db.String, nullable=False)
    rector_photo = db.Column(db.String, nullable=False)
    rector_name = db.Column(db.String, nullable=False)
    rector_reception = db.Column(db.String, nullable=False)
    rector_address = db.Column(db.String, nullable=False)
    rector_phone = db.Column(db.String, nullable=False)
    rector_email = db.Column(db.String, nullable=False)

    def format(self):
        return {
            "id" : self.id,
            "name" : self.name,
            "photo1" : self.photo1,
            "photo2" : self.photo2,
            "logo" : self.logo,
            "desc" : self.desc,
            "rector_photo" : self.rector_photo,
            "rector_name" : self.rector_name,
            "rector_reception" : self.rector_reception,
            "rector_address" : self.rector_address,
            "rector_phone" : self.rector_phone,
            "rector_email" : self.rector_email
        }

class Programme(db.Model):
    __tablename__ = 'programme'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    photo = db.Column(db.String, nullable=False)
    desc = db.Column(db.String, nullable=False)
    faculty_datas = relationship("Faculty_Data", cascade="all,delete", backref="programme", passive_deletes=True, lazy=True)

    def format(self):
        return {
            "id" : self.id,
            "name" : self.name,
            "photo" : self.photo,
            "desc" : self.desc,
            "count" : len(self.faculty_datas)
        }

class Faculty_Data(db.Model):
    __tablename__ = 'faculty_data'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    photo = db.Column(db.String, nullable=False)
    desc = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)
    programme_id = db.Column(db.Integer, db.ForeignKey('programme.id', ondelete='CASCADE'))
    faculty_data_metas = relationship("Faculty_Data_Meta", cascade="all,delete", passive_deletes=True, backref="faculty_data", lazy=True)

    def format(self):
        return {
            "id" : self.id,
            "name" : self.name,
            "photo" : self.photo,
            "desc" : self.desc,
            "link" : self.link,
            "programme_id" : self.programme_id,
            "faculty_data_metas" : [x.format() for x in self.faculty_data_metas]
        }

class Faculty_Data_Meta(db.Model):
    __tablename__ = 'faculty_data_meta'
    id = db.Column(db.Integer, primary_key=True)
    faculty_data_id = db.Column(db.Integer, db.ForeignKey('faculty_data.id', ondelete='CASCADE'))
    key = db.Column(db.String, nullable=False)
    value = db.Column(db.String, nullable=False)

    def format(self):
        return {
            "id" : self.id,
            "faculty_data_id" : self.faculty_data_id,
            "key" : self.key,
            "value" : self.value
        }

class Faculty_foreign(db.Model):
    __tablename__ = "faculty_foreign"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    code = db.Column(db.String, nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('university_foreign.id'))
    admissions_foreign = relationship("Admission_Foreign", backref="faculty_foreign", lazy=True)
    
    def format(self):
        return {
            "id" : self.id,
            "name" : self.name,
            "code" : self.code,
            "university_id" : self.university_id,
            "admissions_foreign" : [x.format() for x in self.admissions_foreign]
        }
    
    def syre_format(self):
        return{
            "id" : self.id,
            "name" : self.name,
            "code" : self.code,
            "university_id" : self.university_id
        }

class University_foreign(db.Model):
    __tablename__ = "university_foreign"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=True)
    logo = db.Column(db.String, nullable=False)
    picture = db.Column(db.String, nullable=False)
    picture_desc = db.Column(db.String, nullable=False)
    video = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    texts = db.relationship("Text_foreign", backref='university_foreign')
    faculties = relationship("Faculty_foreign", backref='university_foreign')
    edu_types_foreign = relationship("Education_type_foreign", backref='university_foreign')
    admissions_foreign = relationship("Admission_Foreign", backref='university_foreign')
    attaches = relationship('Adm_Attach_Foreign', cascade="all,delete", backref='university_foreign', lazy=True)
    def __repr__(self) -> str:
        return "%s"%self.title
    def format(self):
        return {
            "id": self.id,
            "title": self.title,
            "logo": self.logo,
            "picture": self.picture,
            "picture_desc": self.picture_desc,
            "videos": self.video,
            "description": self.description,
            "texts": [x.format() for x in self.texts],
            "faculties": [x.format() for x in self.faculties],
            "edu_types_foreign": [x.format() for x in self.edu_types_foreign],
        }

    def format2(self):
        return {
            "id" : self.id,
            "title" : self.title,
            "logo": self.logo,
            # "admissions" : [x.format2() for x in self.admissions_foreign]
        }

class Text_foreign(db.Model):
    __tablename__ = "text_foreign"
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('university_foreign.id'))
    title_or_info = db.Column(db.String, default='info')
    text = db.Column(db.Text, nullable=False)

    def format(self):
        return {

            "id": self.id,
            "university_id":self.university_id,
            "title":self.title_or_info,
            "text":self.text,
        }
    def format_front(self):
        return {
            "id": self.id,
            "title": self.title_or_info,
            "text": self.text,
        }



class Gender_foreign(db.Model):
    __tablename__ = 'gender_foreign'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)

    admissions_foreign = relationship('Admission_Foreign', cascade = "all,delete", backref = "gender_foreign", lazy = True)
    def format(self):
        return{
            "id" : self.id,
            "name" : self.name
        }


class Billboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    date = db.Column(db.Text, nullable=False)
    time = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    picture = db.Column(db.Text, nullable=False)

    def format(self):
        return {
            'id': self.id,
            'title_bill': self.title,
            'date_bill': self.date,
            'time_bill': self.time,
            'time_desc': self.desc,
            'picture_bill': self.picture

        }

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.String, nullable=True)
    rector_photo = db.Column(db.String, nullable=False)
    rector_name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    additional_infos = relationship("Additional_Info_Meta", backref='post')
    work_activities = relationship("Work_Activity_Meta", backref='post')

    def format(self):
        return {
            'id': self.id,
            'photo': self.photo,
            'rector_photo': self.rector_photo,
            'rector_name': self.rector_name,
            'description': self.description,
            'additional_infos': [x.format() for x in self.additional_infos],
            'work_activities': [x.format() for x in self.work_activities]
        }

class Additional_Info_Meta(db.Model):
    __tablename__ = 'additional_info_meta'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    key = db.Column(db.String,  nullable=False)
    value = db.Column(db.String,  nullable=False)

    def format(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value
        }

class Work_Activity_Meta(db.Model):
    __tablename__ = 'work_activity_meta'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    key = db.Column(db.String,  nullable=False)
    value = db.Column(db.String,  nullable=False)

    def format(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value
        }

class Structure(db.Model):
    __tablename__ = 'structure'
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String, nullable=False)
    photo = db.Column(db.String, nullable=True)
    fullname = db.Column(db.String, nullable=True)
    desc = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    phone = db.Column(db.String, nullable=True)
    reception_time = db.Column(db.String, nullable=True)

    def format(self):
        return {
            'id' : self.id,
            'role' : self.role,
            'photo' : self.photo,
            'fullname' : self.fullname,
            'desc' : self.desc,
            'email' : self.email,
            'phone' : self.phone,
            'reception_time' : self.reception_time
        }
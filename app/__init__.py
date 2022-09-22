
from flask import *
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

class MicroBlogModelView(ModelView):
    column_display_pk = True
    can_create = False
    can_delete = False
    can_edit = False
    can_export = True
    export_types = ['xlsx', 'csv']


from .exts import db
# import sentry_sdk
# from sentry_sdk.integrations.flask import FlaskIntegration

# sentry_sdk.init('YOUR_DSN_HERE', integrations=[FlaskIntegration()])

# Blueprints
from .models import *

from .routes import tdau
from flask_migrate import Migrate

def create_app(testing=False):
    app = Flask(__name__)
    if testing:
        app.config.from_pyfile('t_config.py')
    else:
        app.config.from_pyfile('config.py')
    db.init_app(app)
    migrate = Migrate(app, db)
    app.register_blueprint(tdau)
    
    @app.route('/uploads/<path:p>')
    def send_f(p):
        print("126516516")
        attach = request.args.get('download')
        if attach:
            return send_from_directory("../uploads",p, as_attachment=True)    
        return send_from_directory("../uploads",p)
    @app.route("/", methods=['GET'])
    def home():
        return jsonify({"msg": "Hello World"})
    @app.after_request
    def after_request(response):
        header = response.headers
        header.add('Access-Control-Allow-Origin', '*')
        header.add('Access-Control-Allow-Headers', '*')
        header.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response
    with app.app_context():
        pass
        #db.drop_all()
        #db.create_all()
    admin = Admin(app,name='microblog', template_mode='bootstrap4')
    admin.add_view(MicroBlogModelView(User, db.session))
    admin.add_view(MicroBlogModelView(Role_meta, db.session))
    admin.add_view(MicroBlogModelView(Role, db.session))
    admin.add_view(MicroBlogModelView(UserMeta, db.session))
    admin.add_view(MicroBlogModelView(Admission, db.session))
    admin.add_view(MicroBlogModelView(Adm_Attach, db.session))
    admin.add_view(MicroBlogModelView(University_foreign, db.session))
    admin.add_view(MicroBlogModelView(Text_foreign, db.session))
    admin.add_view(MicroBlogModelView(Faculty_foreign, db.session))
    admin.add_view(MicroBlogModelView(Faculty, db.session))
    admin.add_view(MicroBlogModelView(Faculty_meta, db.session))
    admin.add_view(MicroBlogModelView(Speciality, db.session))
    admin.add_view(MicroBlogModelView(Qualification, db.session))
    admin.add_view(MicroBlogModelView(Education_type, db.session))
    admin.add_view(MicroBlogModelView(Education_type_foreign, db.session))
    admin.add_view(MicroBlogModelView(Education_form, db.session))
    admin.add_view(MicroBlogModelView(Nationality, db.session))
    admin.add_view(MicroBlogModelView(Gender, db.session))
    admin.add_view(MicroBlogModelView(Country, db.session))
    admin.add_view(MicroBlogModelView(Region, db.session))
    admin.add_view(MicroBlogModelView(District, db.session))
    admin.add_view(MicroBlogModelView(Uni_Attach_Foreign, db.session))
    admin.add_view(MicroBlogModelView(Adm_Attach_Foreign, db.session))
    admin.add_view(MicroBlogModelView(Admission_Foreign, db.session))
    admin.add_view(MicroBlogModelView(Gender_foreign, db.session))
    admin.add_view(MicroBlogModelView(Billboard, db.session))

    
    return app






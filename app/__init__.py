
from flask import *
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

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
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Role_meta, db.session))
    admin.add_view(ModelView(Role, db.session))
    admin.add_view(ModelView(UserMeta, db.session))
    admin.add_view(ModelView(Admission, db.session))
    admin.add_view(ModelView(Adm_Attach, db.session))
    admin.add_view(ModelView(University_foreign, db.session))
    admin.add_view(ModelView(Text_foreign, db.session))
    admin.add_view(ModelView(Faculty_foreign, db.session))
    admin.add_view(ModelView(Faculty, db.session))
    admin.add_view(ModelView(Faculty_meta, db.session))
    admin.add_view(ModelView(Speciality, db.session))
    admin.add_view(ModelView(Qualification, db.session))
    admin.add_view(ModelView(Education_type, db.session))
    admin.add_view(ModelView(Education_type_foreign, db.session))
    admin.add_view(ModelView(Education_form, db.session))
    admin.add_view(ModelView(Nationality, db.session))
    admin.add_view(ModelView(Gender, db.session))
    admin.add_view(ModelView(Country, db.session))
    admin.add_view(ModelView(Region, db.session))
    admin.add_view(ModelView(District, db.session))
    admin.add_view(ModelView(Uni_Attach_Foreign, db.session))
    admin.add_view(ModelView(Adm_Attach_Foreign, db.session))
    admin.add_view(ModelView(Admission_Foreign, db.session))
    admin.add_view(ModelView(Gender_foreign, db.session))
    admin.add_view(ModelView(Billboard, db.session))

    
    return app






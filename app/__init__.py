
from flask import *
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, current_user
from .exts import db
from flask_bcrypt import Bcrypt
# import sentry_sdk
# from sentry_sdk.integrations.flask import FlaskIntegration

# sentry_sdk.init('YOUR_DSN_HERE', integrations=[FlaskIntegration()])

# Blueprints
from .models import *

from .routes import tdau

from flask_migrate import Migrate



login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message = 'Пожалуйста сначало зарегистрируйтесь!'
login_manager.login_message_category = 'info'
bcrypt = Bcrypt()

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('flask__admin.login'))


def create_app(testing=False):
    app = Flask(__name__)
    if testing:
        app.config.from_pyfile('t_config.py')
    else:
        app.config.from_pyfile('config.py')
    db.init_app(app)
    from .flask__admin import flask__admin
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate = Migrate(app, db)
    app.register_blueprint(tdau)
    app.register_blueprint(flask__admin)
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
    admin.add_view(AdminModelView(User, db.session))
    admin.add_view(AdminModelView(Role_meta, db.session))
    admin.add_view(AdminModelView(Role, db.session))
    admin.add_view(AdminModelView(UserMeta, db.session))
    admin.add_view(AdminModelView(Admission, db.session))
    admin.add_view(AdminModelView(Adm_Attach, db.session))
    admin.add_view(AdminModelView(University_foreign, db.session))
    admin.add_view(AdminModelView(Text_foreign_uz, db.session))
    admin.add_view(AdminModelView(Faculty_foreign, db.session))
    admin.add_view(AdminModelView(Faculty, db.session))
    admin.add_view(AdminModelView(Faculty_meta, db.session))
    admin.add_view(AdminModelView(Speciality, db.session))
    admin.add_view(AdminModelView(Qualification, db.session))
    admin.add_view(AdminModelView(Education_type, db.session))
    admin.add_view(AdminModelView(Education_type_foreign, db.session))
    admin.add_view(AdminModelView(Education_form, db.session))
    admin.add_view(AdminModelView(Nationality, db.session))
    admin.add_view(AdminModelView(Gender, db.session))
    admin.add_view(AdminModelView(Country, db.session))
    admin.add_view(AdminModelView(Region, db.session))
    admin.add_view(AdminModelView(District, db.session))
    admin.add_view(AdminModelView(Uni_Attach_Foreign, db.session))
    admin.add_view(AdminModelView(Adm_Attach_Foreign, db.session))
    admin.add_view(AdminModelView(Admission_Foreign, db.session))
    admin.add_view(AdminModelView(Gender_foreign, db.session))
    admin.add_view(AdminModelView(Billboard, db.session))

    
    return app






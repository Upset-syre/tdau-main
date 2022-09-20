from app import create_app
from app.exts import db
from app.models import AdminFlask
from app.models import *
from app.flask__admin import createAdmin2


if __name__ == "__main__":

    app = create_app()
    with app.app_context():
        db.create_all()
        admin = AdminFlask.query.filter_by(admin_name='admin').first()
        u = User.query.filter_by(username='admin').first()
        if not u:
            u = User(
                username='admin',
                phone='998999999999'
            )
            db.session.add(u)
            u.set_password('6569321John0604')
            db.session.commit()
            print('UserAdmin created!')
        if admin:
            app.run(debug=True, host="0.0.0.0", port=5050)

        createAdmin2()
        app.run(debug=True, host="0.0.0.0", port=5050)

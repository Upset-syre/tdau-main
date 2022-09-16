from app import create_app
from app.models import *

app = create_app()
with app.app_context():
    u = User(
        username = 'admin',
        phone = '998999999999'
    )
    db.session.add(u)
    u.set_password('6569321John0604')
    db.session.commit()
    # db.drop_all()
    # db.create_all()
    # Programme.__table__.create(db.session.bind)
    # Faculty_Data.__table__.create(db.session.bind)
    # Faculty_Data_Meta.__table__.create(db.session.bind)
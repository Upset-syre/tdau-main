from app import create_app
from app.models import *

app = create_app()
with app.app_context():
    Programme.__table__.create(db.session.bind)
    Faculty_Data.__table__.create(db.session.bind)
    Faculty_Data_Meta.__table__.create(db.session.bind)
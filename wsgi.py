from api import create_app, db
from api.models import *


app = create_app(config_name = 'wsgi')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Student = Student)

with app.app_context():
    db.create_all()
    
    

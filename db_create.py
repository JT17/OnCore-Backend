from application import db
from application.models import * 

db.create_all()

#print("DB created.")
#for t in db.metadata.tables.items():
#    print(t)

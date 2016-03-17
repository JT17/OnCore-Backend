from models import Address, User, Appointment
from database import db_session
import datetime

addr = Address(1600, 'Pennsylvania', 'Ave', 'Washington DC', 20500, 'DC');
db_session.add(addr);
db_session.flush();
user = User('Barack', 'Obama', 1111111111, 12345568, addr.id);
db_session.add(user);
db_session.flush();
appt = Appointment(user.id, datetime.datetime.now());

db_session.add(appt);
db_session.commit();

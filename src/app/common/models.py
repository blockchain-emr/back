from .config import db
import datetime


class Organization(db.Document):
    password     = db.StringField(required=True)
    full_name    = db.StringField()
    username     = db.StringField(required=True, unique = True)
    email        = db.StringField(required=True, unique = True)

    def __str__(self):
        return "{}".format(self.full_name)


class Doctor(db.Document):
    password     = db.StringField(required=True)
    first_name   = db.StringField()
    last_name    = db.StringField()
    email        = db.StringField(required=True, unique = True)
    phone_number = db.StringField()
    organization = db.ReferenceField("Organization")

    def __str__(self):
        return "{} {}".format(self.first_name , self.last_name)

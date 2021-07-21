from apis.models.model import db


class equipment(db.Model):
    __tablename__ = 'equipments'

    id = db.Column(db.BigInteger, primary_key=True)
    vessel_id = db.Column(db.BigInteger, db.ForeignKey('vessels.id'))
    name = db.Column(db.String(256))
    code = db.Column(db.String(8))
    location = db.Column(db.String(256))
    active = db.Column(db.Boolean)


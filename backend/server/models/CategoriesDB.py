from backend.server import db


class CategoriesDB(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    exerciseName = db.Column(db.String(100))
    category = db.Column(db.String(50))

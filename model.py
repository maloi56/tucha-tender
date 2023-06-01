from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # note no "app" here, and no import from my_app above


class Selected(db.Model):
    id = db.Column(db.TEXT, primary_key=True)
    title = db.Column(db.TEXT, nullable=False)
    price = db.Column(db.INTEGER, nullable=False)
    date = db.Column(db.Date, nullable=False)
    href = db.Column(db.TEXT, nullable=False)
    status = db.Column(db.TEXT, nullable=False)


class FilterWords(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    word = db.Column(db.TEXT, nullable=False)


class BanWords(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    word = db.Column(db.TEXT, nullable=False)


class Rules(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    priceFrom = db.Column(db.INTEGER)
    priceTo = db.Column(db.INTEGER)
    date = db.Column(db.Date, nullable=False)


class Users(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    role = db.Column(db.INTEGER, nullable=False)
    login = db.Column(db.TEXT, nullable=False)
    psw = db.Column(db.TEXT, nullable=False)
    time = db.Column(db.INTEGER, nullable=False)
    # Определите внешний ключ (если необходимо)
    role_fk = db.ForeignKey('roles.id')


class Rating(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    rate = db.Column(db.INTEGER)
    comment = db.Column(db.TEXT)
    costprice = db.Column(db.INTEGER)
    role = db.Column(db.INTEGER, nullable=False)
    tender = db.Column(db.Text, nullable=False)
    document = db.Column(db.LargeBinary)
    role_fk = db.ForeignKey('roles.id')
    tender_fk = db.ForeignKey('selected.id')


class Roles(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    name = db.Column(db.TEXT, nullable=False)

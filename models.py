import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy import ForeignKey,create_engine
from urllib.parse import quote_plus
from sqlalchemy.orm import relationship
load_dotenv()

database = 'Biblio'
password = 'motdepasse'

motdepasse=("motdepasse")

motdepasse = quote_plus(os.getenv('pswd_db'))

db_path= "postgresql://postgres:{}@localhost:5432/Biblio".format(motdepasse)

db=SQLAlchemy()

def setup_db(app, path=db_path):

    app.config['SQLALCHEMY_DATABASE_URI'] = db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.app = app
    db.init_app(app)
    db.create_all()

class Categorie(db.Model):
    __tablename__ = 'categories'
    categorie_id = db.Column(db.Integer, primary_key=True)
    libelle = db.Column(db.String(150), nullable=False)
    valeur = db.relationship ("Livre",backref = "categories",lazy=True )

    def __init__(self,libelle):
        self.libelle = libelle

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def format(self):
        return {
            'id_categorie': self.categorie_id,
            'libelle_categorie' : self.libelle
       }

class Livre(db.Model):
    __tablename__ = 'livres'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(12), nullable=False)
    titre = db.Column(db.String(150), nullable=False)
    date_publication = db.Column(db.Date, nullable=False)
    auteur = db.Column(db.String(150), nullable=False)
    editeur = db.Column(db.String(150), nullable=False)
    categorie_id = db.Column(db.Integer,db.ForeignKey('categories.categorie_id'),nullable=False)


    def __init__(self,isbn,titre, date_publication,auteur,editeur,categorie_id):
        self.isbn = isbn
        self.titre = titre
        self.date_publication = date_publication
        self.auteur = auteur
        self.editeur = editeur
        self.categorie_id = categorie_id

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def format(self):
        return {
            'id' : self.id,
            'isbn' : self.isbn,
            'titre' : self.titre,
            'date_publication' : self.date_publication,
            'auteur' : self.auteur,
            'editeur' : self.editeur,
            'categorie_id': self.categorie_id
        }

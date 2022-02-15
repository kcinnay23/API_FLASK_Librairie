import os
from turtle import back
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from urllib.parse import quote_plus
from flask import Flask,jsonify, request, abort
from sqlalchemy.orm import relationship
from flask_migrate import Migrate
from dotenv import load_dotenv
from requests import get
load_dotenv()

database = 'Biblio'
password = 'motdepasse'
###db_path ='postgresql://{}:{}@{}/

# {}'.format('postgres','mp','localhost:5432','Biblio')

app = Flask(__name__)
motdepasse=("motdepasse")

motdepasse = quote_plus(os.getenv('pswd_db'))

app.config['SQLALCHEMY_DATABASE_URI']="postgresql://postgres:{}@localhost:5432/Biblio".format(motdepasse)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app)

migrate=Migrate(app,db)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods','GET,PATCH,POST,DELETE,OPTIONS')
    return response

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

db.create_all()

#############################################################
# fonction permettant d'afficher les éléments d'une liste
#############################################################

def paginate(request):
    items = [item.format() for item in request]
    return items

##############################
# Lister tous les livres +
##############################

@app.route('/livres')
def get_livres():
    try:
        livres = Livre.query.all()
        livres = paginate(livres)
        return jsonify({
            'success': True,
            'status_code': 200,
            'livres': livres,
            'total_livres': len(livres)
        })
    except:
        abort(404)
    finally:
        db.session.close()

#################################################
# Chercher un livre en particulier par son id +
#################################################

@app.route('/livres/<int:id>')
def get_book(id):
    livre = Livre.query.get(id)
    if livre is None:
        abort(404)
    else:
        return livre.format()

################################################
# Lister la liste des livres d'une categorie
################################################

@app.route('/categories/<int:id>/livres')
def book_category(id):
    try:
        category = Categorie.query.get(id)
        books = Livre.query.filter_by(categorie_id=id).all()
        books = paginate(books)
        return jsonify({
            'Success': True,
            'Status_code': 200,
            'total': len(books),
            'categorie': category.format(),
            'livres': books
        })
    except:
        abort(404)
    finally:
        db.session.close()

#######################################
# Lister toutes les categories +
#######################################

@app.route('/categories')
def get_categories():
    categories = Categorie.query.all()
    categories = paginate(categories)
    if categories is None:
        abort(404)
    else:
        return jsonify({
            'success': True,
            'status_code': 200,
            'Categorie': categories,
            'total': len(categories)
        })

########################################
# Chercher une categorie par son id +
########################################

@app.route('/categories/<int:id>')
def get_category(id):
    categorie = Categorie.query.get(id)
    if categorie is None:
        abort(404)
    else:
        return categorie.format()

############################
# Supprimer un livre +
############################

@app.route('/livres/<int:id>', methods=['DELETE'])
def del_livre(id):
    try:
        livr = Livre.query.get(id)
        livr.delete()
        return jsonify({
            'success': True,
            'id_book': id,
            'new_total': livr.query.count()
        })
    except:
        abort(404)
    finally:
        db.session.close()

#############################
# Supprimer une categorie +
#############################

@app.route('/categories/<int:id>', methods=['DELETE'])
def del_categorie(id):
    try:
        category = Categorie.query.get(id)
        category.delete()
        return jsonify({
            'success': True,
            'status': 200,
            'id_cat': id,
            'new_total': Categorie.query.count()
        })
    except:
        abort(404)
    finally:
        db.session.close()

###########################################
# Modifier les informations d'un livre
###########################################

@app.route('/livres/<int:id>', methods=['PATCH'])
def change_book(id):
    body = request.get_json()
    book = Livre.query.get(id)
    try:
        if 'titre' in body and 'auteur' in body and 'editeur' in body and 'date_publication' in body:
            book.titre = body['titre']
            book.auteur = body['auteur']
            book.editeur = body['editeur']
            book.date_publication = body['date_publication']
        book.update()
        return jsonify ({
            'success modify' : True,
            'book' : book.format()
        })
    except:
        abort(404)
########################################
# Modifier le libellé d'une categorie
########################################

@app.route('/categories/<int:id>', methods=['PATCH'])
def change_name(id):
    body = request.get_json()
    category = Categorie.query.get(id)
    try:
        if 'libelle_categorie' in body:
            category.libelle = body['libelle_categorie']
        category.update()
        return jsonify({
            'success modify' : True,
            'category':category.format()
            })
    except:
        abort(404)

##############################################
# Rechercher un livre par son titre ou son auteur
##############################################
@app.route('/livres/<string:word>')
def search_book(word):
    mot = '%'+word+'%'
    titre = Livre.query.filter(Livre.titre.like(mot)).all()
    titre = paginate(titre)
    return jsonify({
        'livres': titre
    })

'''@app.route('/livres/<string:value>')
def search_livre(value):
    val = '%'+value+'%'
    auteur = Livre.query.filter(Livre.auteur.like(val)).all()
    auteur = paginate(auteur)
    return jsonify({
        'livres': auteur
    })'''

##############################################
# Ajouter une categorie
##############################################
@app.route('/categories', methods=['POST'])
def add_category():
    body = request.get_json()
    new_categorie = body['libelle_categorie']
    category = Categorie(libelle=new_categorie)
    category.insert()
    return jsonify({
        'success': True,
        'added': category.format(),
        'total_categories': Categorie.query.count()
    })

##############################################
# Ajouter un livre
##############################################
@app.route('/livres', methods=['POST'])
def add_book():
    body = request.get_json()
    isbn = body['isbn']
    new_titre = body['titre']
    new_date = body['date_publication']
    new_auteur = body['auteur']
    new_editeur = body['editeur']
    categorie_id = body['categorie_id']
    livre = Livre(isbn=isbn, titre=new_titre, date_publication=new_date,
                auteur=new_auteur, editeur=new_editeur, categorie_id=categorie_id)
    livre.insert()
    count = Livre.query.count()
    return jsonify({
        'success': True,
        'added': livre.format(),
        'total_books': count,
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
        }), 404

@app.errorhandler(500)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal server Error"
        }), 500

@app.errorhandler(400)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Mauvaise requete"
        }), 400
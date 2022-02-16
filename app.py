from models import Livre,Categorie,setup_db, db
from flask import Flask,jsonify, request, abort,send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv
from requests import get
from turtle import back

#############################################################
# fonction permettant d'afficher les éléments d'une liste
#############################################################

def paginate(request):
    items = [item.format() for item in request]
    return items

def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    migrate = Migrate(app, db)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods','GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/static/<path:path>')
    def get_docs(path):
        return send_from_directory('static',path)

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

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=False)
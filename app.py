from flask import Flask, request, redirect, url_for, session
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired
from wtforms.fields import TelField
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
from flask import Flask, request
from sqlalchemy import or_, and_
from flask import Flask, request, jsonify
import time
import json
from datetime import datetime
from sqlalchemy.orm import relationship


 
app = Flask(__name__)
app.debug = True
 
app.config['SECRET_KEY'] = 'votre-clé-secrète'

# adding configuration for using a sqlite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\Baptiste\\Downloads\\app_db.db'
 
# Creating an SQLAlchemy instance
db = SQLAlchemy(app)

 
# Settings for migrations
migrate = Migrate(app, db)
 
# Models

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_client = db.Column(db.String(50))
    prenom = db.Column(db.String(100))
    nom = db.Column(db.String(100))
    tel = db.Column(db.String(100))
    tickets = relationship('Ticket', backref='user')
    code_postal = db.Column(db.Integer)


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    pieces = relationship('Piece', backref='ticket')


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100))
    pieces = relationship('Piece', backref='category')
    color = db.Column(db.String(100))

class Piece(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    immat = db.Column(db.String(100))
    marque = db.Column(db.String(100))
    modele = db.Column(db.String(100))
    libelle = db.Column(db.String(100))
    numero = db.Column(db.String(100))
    energie = db.Column(db.String(100))
    details = db.Column(db.String(100))
    etat = db.Column(db.String(100))
    prix = db.Column(db.String(100))












class TicketForm(FlaskForm):
    # Informations sur le client
    type_client = SelectField('Type de Client', choices=[('individual', 'Individuel'), ('professional', 'Professionnel')], validators=[DataRequired()])
    prenom = StringField('Prénom', validators=[DataRequired()])
    nom = StringField('Nom', validators=[DataRequired()])
    tel = StringField('Téléphone', validators=[DataRequired()])
    
    # Informations sur la pièce automobile
    immat = StringField("Immatriculation", validators=[DataRequired()])
    marque = StringField('Marque de la Voiture', validators=[DataRequired()])
    modele = StringField("Modèle", validators=[DataRequired()])
    libelle = StringField('Libellé', validators=[DataRequired()])
    code_constr_moteur = StringField('Numéro Fabriquant/Moteur', validators=[DataRequired()])
    energie = StringField('Énergie')

    submit = SubmitField('Soumettre le Billet')


def searchForUser(prenom, nom, tel):
    filters = []
    filters.append(User.prenom.ilike(f"%{prenom}%"))
    filters.append(User.nom.ilike(f"%{nom}%"))
    filters.append(User.tel == tel)

    users = User.query.filter(*filters).all()

    return users

def add_categories():
    new_category = Category(category_name="Carrosserie", color="blue")
    new_category2 = Category(category_name="Habitacle", color="green")
    new_category3 = Category(category_name="Roues", color="red")
    new_category4 = Category(category_name="Mecanique Légère", color="pink")
    new_category5 = Category(category_name="Mécanique Lourde", color="yellow")

    db.session.add_all([new_category, new_category2, new_category3, new_category4, new_category5])
    db.session.commit()

categoryDict = {
    "Carrosserie" : 1,
    "Habitacle" : 2,
    "Roues" : 3,
    "Mecanique Légère" : 4,
    "Mécanique Lourde" : 5
}

 
@app.route('/ticket', methods=['GET', 'POST'])
def submit_ticket():


    form = TicketForm()



    if form.validate_on_submit():

        return redirect(url_for('submit_ticket'))
    else:
        print(form.errors)
    return render_template('add_profile.html', form=form)


@app.route('/get_data', methods=['POST'])
def get_data():
    add_categories()
    data = request.get_json()
    # Now you can use the data
    
    alreadyUser = searchForUser(data["prenom"], data["nom"], data["tel"])
    if len(alreadyUser) != 0:
        new_user = alreadyUser[0]
    else:
        new_user = User(type_client=data["type_client"], prenom = data["prenom"], nom = data["nom"], tel=data["tel"], code_postal = data["code_postal"])
        db.session.add_all([new_user])
        db.session.commit()

    new_ticket = Ticket(user_id=new_user.id, status="En attente de traitement")
    db.session.add_all([new_ticket])
    db.session.commit()

    new_pieces = []
    print(data)
    print(len(data["immat"]) - 1)
    for i in range(len(data["immat"]) - 1):    #TODO
        print("run")
        try:
            new_pieces.append(Piece(ticket_id=new_ticket.id, category_id = categoryDict[data["category"]], immat = data["immat"][i+1], marque = data["marque"][i+1], modele = data["modele"][i+1], libelle = data["libelle"][i+1], numero = data["numero"][i+1], energie = data["energie"][i+1], etat = "En attente de traitement", details = data["details"][i+1], prix = "A définir"))
        except Exception as e:
            print("Error: ", str(e))

        print(new_pieces)
        print("end")

    db.session.add_all(new_pieces)

    db.session.commit()

    # You can return a response
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@app.route('/liste')
def liste():
    tickets = Ticket.query.all()

    return render_template('liste.html', tickets=tickets)



from flask import request

from flask import request

@app.route('/update/<string:table_name>/<int:item_id>', methods=['POST'])
def update_item(table_name, item_id):
    data = request.get_json()  # get the data from the POST request

    if table_name == 'Piece':
        item = Piece.query.get(item_id)
    elif table_name == 'Ticket':
        item = Ticket.query.get(item_id)
    else:
        return f"Table {table_name} not found", 404

    if item:
        for key, value in data.items():
            if hasattr(item, key):  # only update if the key exists in your model
                setattr(item, key, value)
        db.session.commit()
        return f"Item ID {item_id} in {table_name} updated successfully", 200
    else:
        return f"Item with ID {item_id} in {table_name} not found", 404








@app.route('/get_data_editing', methods=['POST'])
def get_data_editing():
    data = request.get_json()
    print(data)

    # You can return a response
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
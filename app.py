from flask import Flask, request, redirect, url_for, session, Markup
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
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_babel import Babel
from flask_admin.contrib.sqla import filters
from flask_admin.helpers import get_url
from markupsafe import Markup
from flask_admin import expose
from sqlalchemy.orm import joinedload
import pytz



 
app = Flask(__name__)
babel = Babel(app)
app.debug = True
 
app.config['SECRET_KEY'] = 'votre-clé-secrète'
app.config['BABEL_DEFAULT_LOCALE'] = 'fr'


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
    created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Europe/Paris')))
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
    ouvert_par = db.Column(db.Integer, db.ForeignKey('employee.id'))
    gere_par = db.Column(db.Integer, db.ForeignKey('employee.id'))
    @property
    def user(self):
        return self.ticket.user

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))

    ouvert_pieces = relationship('Piece', backref='ouvert_employee', foreign_keys=[Piece.ouvert_par])
    gere_pieces = relationship('Piece', backref='gere_employee', foreign_keys=[Piece.gere_par])











class TicketForm(FlaskForm):
    # Informations sur le client
    type_client = SelectField('Type de Client', choices=[('individuel', 'Individuel'), ('professionel', 'Professionnel')], validators=[DataRequired()])


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
    new_category5 = Category(category_name="Mécanique Lourde", color="orange")

    db.session.add_all([new_category, new_category2, new_category3, new_category4, new_category5])
    db.session.commit()

 
@app.route('/ticket', methods=['GET', 'POST'])
def submit_ticket():
    #add_categories()


    form = TicketForm()



    if form.validate_on_submit():

        return redirect(url_for('submit_ticket'))
    else:
        print(form.errors)


    categories = Category.query.all()
    employee = Employee.query.all()

    return render_template('add_profile.html', form=form, category = categories, employee = employee)


@app.route('/get_data', methods=['POST'])
def get_data():
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
            category = Category.query.filter_by(category_name=data['category']).first()
            employee = Employee.query.filter_by(nom=data["employee"]).first()
            new_pieces.append(Piece(ouvert_par = employee.id, ticket_id=new_ticket.id, category_id = category.id, immat = data["immat"][i+1], marque = data["marque"][i+1], modele = data["modele"][i+1], libelle = data["libelle"][i+1], numero = data["numero"][i+1], energie = data["energie"][i+1], etat = "En attente de traitement", details = data["details"][i+1], prix = "A définir"))
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
    category = Category.query.all()
    employee = Employee.query.all()

    return render_template('liste.html', tickets=tickets, category = category, employee = employee)




@app.route('/update/<string:table_name>/<int:item_id>', methods=['POST'])
def update_item(table_name, item_id):
    data = request.get_json()  # get the data from the POST request
    print(data)

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



#FILTRES
#User
class UserAdmin(ModelView):
    column_filters = [
        'prenom',
        'nom',
        'type_client',
        'tel',
        'code_postal',
        filters.FilterLike(User.nom, 'Nom commence par'),
    ]

    column_list = ('prenom', 'nom', 'type_client', 'tel', 'code_postal', 'pieces')

    def _user_formatter(view, context, model, name):
        if model.tickets:
            markup_links = []
            for ticket in model.tickets:
                for piece in ticket.pieces:
                    markup_links.append(Markup('<a href="{}">{}</a>'.format(url_for('piece.edit_view', id=piece.id), piece.libelle)))
            return Markup(", ".join(markup_links))
        return ''

    column_formatters = {
        'pieces': _user_formatter,
    }

#Ticket
class FilterStatus(filters.FilterEqual):
    def get_options(self, view):
        return [
            ('Terminé', 'Terminé'),
            ('En attente de traitement', 'En attente de traitement'),
            ('En cours', 'En cours'),
        ]

from flask_admin.model.template import macro

class TicketAdmin(ModelView):
    column_filters = (
        FilterStatus(column=Ticket.status, name='Status'),
        filters.DateBetweenFilter(column=Ticket.created_at, name='Created At')
    )

    column_formatters = dict(
        user=lambda v, c, m, p: Markup(f'<a href="{get_url("user.edit_view", id=m.user.id)}">{m.user.nom}</a>') if m.user else '',
        pieces=lambda v, c, m, p: Markup(', '.join([f'<a href="{get_url("piece.edit_view", id=piece.id)}">{piece.libelle}</a>' for piece in m.pieces])),
        created_at=lambda v, c, m, p: m.created_at.strftime("%Y-%m-%d à %H:%M") if m.created_at else ''
    )

    column_list = ['id', 'status', 'created_at', 'user', 'pieces']

    column_labels = {
        'id': 'N° Ticket',
        'created_at' : 'Date de création',
        'user' : 'Client',
        'pieces' :  'Pièces'
    }


#Piece
class PieceAdmin(ModelView):
    column_filters = (
        filters.FilterEqual(column=Piece.immat, name='Immat'),
        filters.FilterEqual(column=Piece.marque, name='Marque'),
        filters.FilterEqual(column=Piece.modele, name='Modele'),
        filters.FilterEqual(column=Piece.libelle, name='Libelle'),
        filters.FilterEqual(column=Piece.numero, name='Numero'),
        filters.FilterEqual(column=Piece.energie, name='Energie'),
        filters.FilterEqual(column=Piece.details, name='Details'),
        filters.FilterEqual(column=Piece.etat, name='Etat'),
        filters.FilterEqual(column=Piece.prix, name='Prix'),
    )

    column_formatters = dict(
        user=lambda v, c, m, p: Markup(f'<a href="{get_url("user.edit_view", id=m.user.id)}">{m.user.nom} {m.user.prenom}</a>') if m.user else '',
    )

    column_list = ('immat', 'marque', 'modele', 'libelle', 'numero', 'energie', 'details', 'etat', 'prix', 'user', "ouvert_par", "gere_par")

    column_labels = {
        'user': 'Client', 
        'ouvert_par' : 'Crée par',
        'gere_par' : "Géré par"
    }









admin = Admin(app, name='Base de donnée', template_mode='bootstrap3')
babel.init_app(app, locale_selector=lambda : 'fr')

admin.add_view(UserAdmin(User, db.session, name='Clients'))  # give the view a unique name
admin.add_view(TicketAdmin(Ticket, db.session, name='Tickets'))
admin.add_view(PieceAdmin(Piece, db.session, name='Pièces'))
admin.add_view(ModelView(Category, db.session, name='Catégories'))
admin.add_view(ModelView(Employee, db.session, name='Employés'))

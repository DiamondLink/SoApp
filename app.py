import os
import time

print("Initial working directory: ", os.getcwd())
# This will print your initial working directory before any changes are made.

# Get the path of the directory where the script is located
current_directory = os.path.dirname(os.path.realpath(__file__))
print("Current directory of the script: ", current_directory)
# This will print the directory containing the script file.

# Define the new directory
new_directory = os.path.join(current_directory, 'templates')
static_path = os.path.join(current_directory, 'static')
print("New directory to switch to: ", new_directory)
# This will print the directory we want to switch to.

# Change the current working directory
os.chdir(new_directory)
print("Final working directory: ", os.getcwd())
# This will print the final working directory after the change.


from flask import Flask, request, redirect, url_for, session, Markup, jsonify
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
import json
from datetime import datetime, timedelta
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
from sqlalchemy.ext.hybrid import hybrid_property
from waitress import serve
import apsw
import sqlite3
from flask_admin.contrib.sqla.filters import BaseSQLAFilter
from send_sms import send
from flask_admin.model.filters import BaseFilter
from sqlalchemy.orm import joinedload
import shutil
import dropbox
import threading
import requests


template_dir = os.path.abspath(new_directory)

 
app = Flask(__name__, template_folder=template_dir, static_folder=static_path)
babel = Babel(app)
app.debug = True
 
app.config['SECRET_KEY'] = 'votre-clé-secrète'
app.config['BABEL_DEFAULT_LOCALE'] = 'fr'

db_path = 'app_db.db'

# adding configuration for using a sqlite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(db_path)



 
# Creating an SQLAlchemy instance
db = SQLAlchemy(app)

 
# Settings for migrations
migrate = Migrate(app, db)


 
# Models

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    type_client = db.Column(db.String(50))
    nom = db.Column(db.String(100))
    tel = db.Column(db.String(100))
    tickets = relationship('Ticket', backref='user')
    code_postal = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Europe/Paris')))


class Ticket(db.Model):
    __tablename__ = 'ticket'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Europe/Paris')))
    pieces = relationship('Piece', backref='ticket')
    info = db.Column(db.String(100))



class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100))
    pieces = relationship('Piece', backref='category')
    color = db.Column(db.String(100))

class Piece(db.Model):
    __tablename__ = 'piece'
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    immat = db.Column(db.String(100))
    marque = db.Column(db.String(100))
    modele = db.Column(db.String(100))
    phase = db.Column(db.String(100))
    libelle = db.Column(db.String(100))
    numero = db.Column(db.String(100))
    ref_mot = db.Column(db.String(100))
    energie = db.Column(db.String(100))
    details = db.Column(db.String(100))
    etat = db.Column(db.String(100))
    prix = db.Column(db.String(100))
    ouvert_par = db.Column(db.Integer, db.ForeignKey('employee.id'))
    gere_par = db.Column(db.Integer, db.ForeignKey('employee.id'))
    created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Europe/Paris')))
    num_ref_lp = db.Column(db.String(100))
    dimension_pneu = db.Column(db.String(100))
    @property
    def user(self):
        return self.ticket.user

    @hybrid_property
    def ticket_status(self):
        return self.ticket.status

    def to_dict(self):
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'category_id': self.category_id,
            'immat': self.immat,
            'marque': self.marque,
            'modele': self.modele,
            'phase': self.phase,
            'libelle': self.libelle,
            'numero': self.numero,
            'ref_mot': self.ref_mot,
            'energie': self.energie,
            'details': self.details,
            'etat': self.etat,
            'prix': self.prix,
            'ouvert_par': self.ouvert_par,
            'gere_par': self.gere_par,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'num_ref_lp': self.num_ref_lp,
        }

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))

    ouvert_pieces = relationship('Piece', backref='ouvert_employee', foreign_keys=[Piece.ouvert_par])
    gere_pieces = relationship('Piece', backref='gere_employee', foreign_keys=[Piece.gere_par])






def refresh_access_token(refresh_token, client_id, client_secret):
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    response = requests.post('https://api.dropboxapi.com/oauth2/token', data=payload)

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception("Failed to refresh access token")

def backup():
    db_path = 'instance//app_db.db'
    backup_dir = ''  # replace with your actual backup directory path
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # get current date and time
    backup_file = os.path.join(backup_dir, f'app_db_backup_{timestamp}.db')

    shutil.copy2(db_path, backup_file)

    # Replace these with your actual refresh token, client ID, and client secret
    refresh_token = 'I6DBkNRjykkAAAAAAAAAAXmjQ6HtuK_KndTiwERrySempP_Kyr7xwlPqnKV0UKyl'
    client_id = '2tn6o03mhzqz3or'
    client_secret = 'ejj3dsfgzws8db2'

    # Refresh the access token
    access_token = refresh_access_token(refresh_token, client_id, client_secret)

    dbx = dropbox.Dropbox(access_token)

    with open(backup_file, 'rb') as f:
        dbx.files_upload(f.read(), f'/Backups/{backup_file}', mode=dropbox.files.WriteMode('overwrite'))

    os.remove(backup_file)

    print("Backup Saved")

    folder_path = '/Backups'
    thirty_days_ago = datetime.now() - timedelta(days=180)
    for entry in dbx.files_list_folder(folder_path).entries:
        if isinstance(entry, dropbox.files.FileMetadata):
            file_path = entry.path_lower
            file_modified_time = entry.client_modified
            if file_modified_time < thirty_days_ago:
                dbx.files_delete_v2(file_path)


    return "Backup Saved"


@app.route('/delete_all_data_main_db_0335')
def delete_all_data_main_db():
    with app.app_context():
        # Reflect all tables in the database
        meta = db.metadata
        for table in reversed(meta.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
    return 'All data from the main database has been deleted.'






class TicketForm(FlaskForm):
    # Informations sur le client
    type_client = SelectField('Type de Client', choices=[('particulier', 'Particulier'), ('professionnel', 'Professionnel')], validators=[DataRequired()], render_kw={"placeholder": "Type Client"})


    nom = StringField('Nom')
    tel = StringField('Téléphone')
    
    # Informations sur la pièce automobile
    immat = StringField("Immatriculation")
    marque = StringField('Marque')
    modele = StringField("Modèle")
    libelle = StringField('Libellé')
    code_constr_moteur = StringField('Ref Constructeur')

    def validate_energie(form, field):
        pass

    submit = SubmitField('Soumettre le Billet')



def searchForUser(tel):
    filters = []
    filters.append(User.tel == tel)

    users = User.query.filter(*filters).all()

    return users

def add_categories():
    new_category = Category(category_name="Carrosserie", color="blue")
    new_category2 = Category(category_name="Habitacle", color="green")
    new_category3 = Category(category_name="Roues", color="orange")
    new_category4 = Category(category_name="Mecanique Légère", color="purple")
    new_category5 = Category(category_name="Boite Vitesse/Moteurs", color="red")

    db.session.add_all([new_category, new_category2, new_category5, new_category4, new_category3])
    db.session.commit()

def add_employee():
    new_employee = Employee(nom = "Lisa")
    new_employee2 = Employee(nom = "Fabien")
    new_employee3 = Employee(nom = "Kevin")
    new_employee4 = Employee(nom = "Damien")
    new_employee5 = Employee(nom = "Lilliana")
    new_employee6 = Employee(nom = "Stéphanie S")
    new_employee7 = Employee(nom = "Jihad")
    new_employee8 = Employee(nom = "DIR SOA")
    

    db.session.add_all([new_employee, new_employee2, new_employee3, new_employee4, new_employee5, new_employee6, new_employee7, new_employee8])
    db.session.commit()

@app.route("/send_sms", methods=['POST'])
def handle_sms():

    telephone = "05 61 37 52 00"

    data = request.get_json()
    print(data)

    with open('sms_text.json', 'r', encoding="utf-8") as f:
        templates = json.load(f)

    piece = Piece.query.get(data["id"])

    piece.energie = piece.energie[:-1] + '1'
    print(piece.libelle)
    print(piece.energie)
    db.session.commit()

    sms_text = templates[data["etat"]].format(prix=piece.prix, num=data["num"], telSOA = telephone, libelle = piece.libelle)

    print(sms_text)


    send(sms_text, [data["tel"]])

    return "sms sended"

@app.route("/remove_dots_phone")
def remove_dots_from_phone_numbers():
    # Query all users
    users = User.query.all()

    # Iterate through all users and update the phone number
    for user in users:
        if user.tel:
            # replace periods with empty string
            new_tel = user.tel.replace('.', '')
            user.tel = new_tel

    # Commit changes to database
    db.session.commit()

    return "dots removed phone"
    



@app.route('/addinit')
def add_initial_datas():
    add_categories()
    add_employee()
    return "Initial Datas Added"
 
@app.route('/create_ticket', methods=['GET', 'POST'])
def submit_ticket():
    with open('modeles.json') as f:
        data = json.load(f)

    form = TicketForm()



    if form.validate_on_submit():

        return redirect(url_for('liste'))
    else:
        print(form.errors)


    categories = Category.query.all()
    employee = Employee.query.all()

    return render_template('add_profile.html', form=form, category = categories, employee = employee, data=data)


def update_ticket_and_pieces_for_restore(ticket_id, ticket_fields, piece_fields):
    # Get the ticket by id
    ticket = Ticket.query.get(ticket_id)

    print(ticket.id)
    print(ticket.created_at)

    # Update the ticket fields
    for key, value in ticket_fields.items():
        setattr(ticket, key, value)

    # Commit the ticket changes to the database
    db.session.commit()

    # Get all pieces attached to this ticket
    pieces = Piece.query.filter_by(ticket_id=ticket_id).all()

    # Update the pieces
    for piece in pieces:
        for key, value in piece_fields.items():
            setattr(piece, key, value)

    # Commit the pieces changes to the database
    db.session.commit()

# Example of usage:



@app.route("/restore", methods = ['POST'])
def restore():
    data = request.get_json()
    print(data)

    ticketDict = {
        "status" : "En attente de traitement"
    }
    pieceDict = {
        "etat" : "En attente de traitement",
        "prix" : "A définir",
        "gere_par" : None
    }

    update_ticket_and_pieces_for_restore(data["id"], ticketDict, pieceDict)

    return "restored"



@app.route('/ticket', methods=['GET', 'POST'])
def get_tickets():
    if request.method == 'POST':
        tickets = []
        tel = request.form.get('tel')
        if len(tel) == 0:
            return render_template('search_client.html', tickets=tickets, first = "False")
        if tel[0] == "0":
            tel = tel[1:]
        
        if tel[:4] == "+330":
            tel = "+33" + tel[4:]
        
        print(tel)

        users = User.query.filter(User.tel.like(f"%{tel}%"))

        for user in users:
            for tik in user.tickets:
                tickets.append(tik)
            # Pass this tickets object to your HTML page
        return render_template('search_client.html', tickets=tickets, first="False")

    return render_template('search_client.html', first = "True")




@app.route('/get_data', methods=['POST'])
def get_data():
    data = request.get_json()
    # Now you can use the data
    
    alreadyUser = searchForUser(data["tel"])
    if len(alreadyUser) != 0 and data["tel"] != "+33":
        new_user = alreadyUser[0]
    else:
        new_user = User(type_client=data["type_client"], nom = data["nom"], tel=data["tel"], code_postal = data["code_postal"])
        db.session.add_all([new_user])
        db.session.commit()

    new_ticket = Ticket(user_id=new_user.id, status="En attente de traitement", info=data['info'])
    db.session.add_all([new_ticket])
    db.session.commit()

    new_pieces = []

    for key, value in data.items():
        if isinstance(value, list):
            data[key] = [item if item is not None else "" for item in value]
            data[key].pop(0)


    for i in range(len(data["immat"])):    #TODO
        try:
            category = Category.query.filter_by(category_name=data['category'][i]).first()
            employee = Employee.query.filter_by(nom=data["employee"]).first()
            new_pieces.append(Piece(ouvert_par = employee.id, ticket_id=new_ticket.id, category_id = category.id, immat = data["immat"][i], marque = data["marque"][i], modele = data["modele"][i], libelle = data["libelle"][i], numero = data["numero"][i], energie = data["energie"][i] + "0", etat = "En attente de traitement", details = data["details"][i], prix = "A définir", phase = data["phase"][i], ref_mot = data["ref_mot"][i],dimension_pneu = data["dimension_pneu"][i]))
        except Exception as e:
            print("Error: ", str(e))

    db.session.add_all(new_pieces)

    db.session.commit()

    time.sleep(0.5)

    # You can return a response
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route('/liste')
def liste():
    tickets = Ticket.query.all()
    category = Category.query.all()
    employee = Employee.query.all()
    pieces = [piece.to_dict() for piece in Piece.query.join(Ticket).filter(Ticket.status != 'Terminé').all()]

    return render_template('liste.html', tickets=tickets, category = category, employee = employee, pieces=json.dumps(pieces))




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




class CustomFilter(BaseSQLAFilter):
    def apply(self, query, value, alias=None):
        # this is just an example. You need to implement the join and filter operation here.
        return query.join(Ticket).join(User).filter(User.tel.like(value))
        
    def operation(self):
        return 'like'

#FILTRES
class TelFilter(BaseFilter):
    def __init__(self, column, name):
        super(TelFilter, self).__init__(name)
        self.column = column

    def apply(self, query, value, alias=None):
        return query.join(Piece.ticket).join(Ticket.user).filter(User.tel.ilike("%{}%".format(value)))

    def operation(self):
        return 'contient'
#User
class UserAdmin(ModelView):
    column_filters = [
        'nom',
        'type_client',
        'tel',
        'code_postal',
        filters.FilterLike(User.nom, 'Nom commence par'),
    ]

    column_list = ('nom', 'type_client', 'tel', 'code_postal', 'pieces')

    def _user_formatter(view, context, model, name):
        if model.tickets:
            markup_links = []
            for ticket in model.tickets:
                for piece in ticket.pieces:
                    markup_links.append(Markup('<a href="{}">{}</a>'.format(url_for('admin_pieces.edit_view', id=piece.id), piece.libelle)))
            return Markup(", ".join(markup_links))
        return ''

    column_formatters = {
        'pieces': _user_formatter
    }

    column_labels = {
        'nom' : "Nom / Description Client"

    }

#Ticket
class FilterStatus(filters.FilterLike):
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
        user=lambda v, c, m, p: Markup(f'<a href="{get_url("admin_clients.edit_view", id=m.user.id)}">{m.user.nom}</a>') if m.user else '',
        pieces=lambda v, c, m, p: Markup(', '.join([f'<a href="{get_url("admin_pieces.edit_view", id=piece.id)}">{piece.libelle}</a>' for piece in m.pieces])),
        created_at=lambda v, c, m, p: m.created_at.strftime("%Y-%m-%d à %H:%M") if m.created_at else ''
    )

    column_list = ['id', 'status', 'info','created_at', 'user', 'pieces']

    column_labels = {
        'id': 'N° Ticket',
        'created_at' : 'Date de création',
        'user' : 'Client',
        'pieces' :  'Pièces',
        'info' : 'Info'
    }


#Piece
class PieceAdmin(ModelView):
    can_edit = False

    column_filters = (
        filters.FilterLike(column=Piece.immat, name='Immat'),
        filters.FilterLike(column=Piece.marque, name='Marque'),
        filters.FilterLike(column=Piece.modele, name='Modele'),
        filters.FilterLike(column=Piece.libelle, name='Libelle'),
        filters.FilterLike(column=Piece.numero, name='Ref Constructeur'),
        filters.FilterLike(column=Piece.ref_mot, name='Ref Moteur'),
        filters.FilterLike(column=Piece.energie, name='Energie'),
        filters.FilterLike(column=Piece.etat, name='Etat'),
        filters.FilterLike(column=Piece.prix, name='Prix'),
        filters.FilterLike(column=Piece.ref_mot, name='Ref Moteur'),
        filters.FilterLike(column=Piece.num_ref_lp, name='Ref/N°/LP Piece'),
        TelFilter(column=User.tel, name='Tel'),
        filters.FilterLike(column=Piece.ticket_id, name='N° Ticket')
    )

    column_formatters = dict(
        user=lambda v, c, m, p: Markup(f'<a href="{get_url("admin_clients.edit_view", id=m.user.id)}">{m.user.tel}</a>') if m.user else '',
        ouvert_par= lambda v, c, m, p: m.ouvert_employee.nom if m.ouvert_employee else '',
        gere_par= lambda v, c, m, p: m.gere_employee.nom if m.gere_employee else ''
    )

    column_list = ('ticket_id', 'immat', 'marque', 'modele',  'libelle', 'numero', 'ref_mot', 'details', 'etat', 'prix', 'user', "ouvert_par", "gere_par",'num_ref_lp')

    column_labels = {
        'user': 'Client', 
        'ouvert_par' : 'Crée par',
        'gere_par' : "Géré par",
        'numero' : "Ref Constructeur",
        'ref_mot' : "Ref Moteur",
        'num_ref_lp' : "Ref/N°/LP Piece",
        'details' : "Commentaires",
        'user' : "Tel",
        'ticket_id' : "N° Ticket"
    }




def is_table_empty(table_name):
    with app.app_context():
        return db.session.query(table_name).count() == 0



admin = Admin(app, name='Base de donnée [Administrateur]', template_mode='bootstrap3', url='/admin-db', endpoint='admin_db')
babel.init_app(app, locale_selector=lambda : 'fr')

admin.add_view(UserAdmin(User, db.session, name='Clients', endpoint='admin_clients'))  # give the view a unique name
#admin.add_view(TicketAdmin(Ticket, db.session, name='Tickets', endpoint='admin_tickets'))
admin.add_view(PieceAdmin(Piece, db.session, name='Pièces', endpoint='admin_pieces'))
admin.add_view(ModelView(Category, db.session, name='Catégories', endpoint='admin_categories'))
admin.add_view(ModelView(Employee, db.session, name='Employés', endpoint='admin_employees'))

















class UserAdmin2(ModelView):
    can_edit = False
    can_create = False
    can_delete = False

    column_filters = [
        'nom',
        'type_client',
        'tel',
        'code_postal',
        filters.FilterLike(User.nom, 'Nom commence par'),
    ]

    column_list = ('nom', 'type_client', 'tel', 'code_postal', 'pieces')

    def _user_formatter(view, context, model, name):
        if model.tickets:
            markup_links = []
            for ticket in model.tickets:
                for piece in ticket.pieces:
                    markup_links.append(Markup('<a href="{}">{}</a>'.format(url_for('user_pieces.edit_view', id=piece.id), piece.libelle)))
            return Markup(", ".join(markup_links))
        return ''

    column_formatters = {
        'pieces': _user_formatter
    }

    column_labels = {
        'nom' : "Nom / Description Client"

    }



class TicketAdmin2(ModelView):
    can_edit = False
    can_create = False
    can_delete = False

    column_filters = (
        FilterStatus(column=Ticket.status, name='Status'),
        filters.DateBetweenFilter(column=Ticket.created_at, name='Created At')
    )

    column_formatters = dict(
        user=lambda v, c, m, p: Markup(f'<a href="{get_url("user_clients.edit_view", id=m.user.id)}">{m.user.nom}</a>') if m.user else '',
        pieces=lambda v, c, m, p: Markup(', '.join([f'<a href="{get_url("user_pieces.edit_view", id=piece.id)}">{piece.libelle}</a>' for piece in m.pieces])),
        created_at=lambda v, c, m, p: m.created_at.strftime("%Y-%m-%d à %H:%M") if m.created_at else ''
    )

    column_list = ['id', 'status', 'info','created_at', 'user', 'pieces']

    column_labels = {
        'id': 'N° Ticket',
        'created_at' : 'Date de création',
        'user' : 'Client',
        'pieces' :  'Pièces',
        'info' : 'Info'
    }


#Piece
class PieceAdmin2(ModelView):
    can_edit = False
    can_create = False
    can_delete = False

    column_filters = (
        filters.FilterLike(column=Piece.immat, name='Immat'),
        filters.FilterLike(column=Piece.marque, name='Marque'),
        filters.FilterLike(column=Piece.modele, name='Modele'),
        filters.FilterLike(column=Piece.libelle, name='Libelle'),
        filters.FilterLike(column=Piece.numero, name='Ref Constructeur'),
        filters.FilterLike(column=Piece.ref_mot, name='Ref Moteur'),
        filters.FilterLike(column=Piece.energie, name='Energie'),
        filters.FilterLike(column=Piece.etat, name='Etat'),
        filters.FilterLike(column=Piece.prix, name='Prix'),
        filters.FilterLike(column=Piece.ref_mot, name='Ref Moteur'),
        filters.FilterLike(column=Piece.num_ref_lp, name='Ref/N°/LP Piece'),
        TelFilter(column=User.tel, name='Tel'),
        filters.FilterLike(column=Piece.ticket_id, name='N° Ticket')
    )

    column_formatters = dict(
        user=lambda v, c, m, p: Markup(f'<a href="{get_url("user_clients.edit_view", id=m.user.id)}">{m.user.tel}</a>') if m.user else '',
        ouvert_par= lambda v, c, m, p: m.ouvert_employee.nom if m.ouvert_employee else '',
        gere_par= lambda v, c, m, p: m.gere_employee.nom if m.gere_employee else ''
    )

    column_list = ('ticket_id', 'immat', 'marque', 'modele', 'libelle', 'numero', 'ref_mot', 'details', 'etat', 'prix', 'user', "ouvert_par", "gere_par", 'num_ref_lp')

    column_labels = {
        'user': 'Client', 
        'ouvert_par' : 'Crée par',
        'gere_par' : "Géré par",
        'numero' : "Ref Constructeur",
        'ref_mot' : "Ref Moteur",
        'num_ref_lp' : "Ref/N°/LP Piece",
        'details' : "Commentaires",
        "user" : "Tel",
        'ticket_id' : "N° Ticket"
    }

class ReadOnlyModelView(ModelView):
    can_edit = False
    can_delete = False
    can_create = False



admin2 = Admin(app, name='Base de donnée', template_mode='bootstrap3', url='/user-db', endpoint='user_db')

admin2.add_view(UserAdmin2(User, db.session, name='Clients', endpoint='user_clients'))  # give the view a unique name
#admin2.add_view(TicketAdmin2(Ticket, db.session, name='Tickets', endpoint='user_tickets'))
admin2.add_view(PieceAdmin2(Piece, db.session, name='Pièces', endpoint='user_pieces'))
admin2.add_view(ReadOnlyModelView(Category, db.session, name='Catégories', endpoint='user_categories'))
admin2.add_view(ReadOnlyModelView(Employee, db.session, name='Employés', endpoint='user_employees'))


def time_until_next_month():
    now = datetime.now()

    # If we're in December, the next first of the month is in January of the next year.
    if now.month == 12:
        next_month = now.replace(year=now.year+1, month=1, day=1, hour=0, minute=0, second=0)
    else:
        next_month = now.replace(month=now.month+1, day=1, hour=0, minute=0, second=0)

    return (next_month - now).total_seconds()

def periodic_backup():
    while True:
        backup()
        time.sleep(time_until_next_month())





if __name__ == '__main__':

    t = threading.Thread(target=periodic_backup)
    t.start()
    print("Backup Program Started !")
    print("\nProgram Started !")



    serve(app, host='0.0.0.0', port=5000)
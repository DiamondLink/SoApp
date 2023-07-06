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
import time
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




 
app = Flask(__name__)
babel = Babel(app)
app.debug = True
 
app.config['SECRET_KEY'] = 'votre-clé-secrète'
app.config['BABEL_DEFAULT_LOCALE'] = 'fr'

db_path = 'C:\\Users\\Baptiste\\Downloads\\app_db.db'
archive_path = 'C:\\Users\\Baptiste\\Downloads\\archive_db.db'

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
    prenom = db.Column(db.String(100))
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
    created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Europe/Paris')))
    pieces = relationship('Piece', backref='ticket')



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
    @property
    def user(self):
        return self.ticket.user

    @hybrid_property
    def ticket_status(self):
        return self.ticket.status

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))

    ouvert_pieces = relationship('Piece', backref='ouvert_employee', foreign_keys=[Piece.ouvert_par])
    gere_pieces = relationship('Piece', backref='gere_employee', foreign_keys=[Piece.gere_par])


@app.route('/archive')
def backup_database():
    # Connect to the Flask database
    connection = apsw.Connection(db_path)
    cursor = connection.cursor()

    # Get the current timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Create the backup file name
    backup_file = f'backup_{timestamp}.db'

    # Execute the backup SQL command
    cursor.execute(f'ATTACH DATABASE "{backup_file}" AS backup_db')
    cursor.execute('BEGIN')
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = cursor.fetchall()
    for table in tables:
        cursor.execute(f'SELECT * FROM {table[0]}')
        rows = cursor.fetchall()
        columns = cursor.getdescription()

        create_table_query = f'CREATE TABLE backup_db.{table[0]}('
        for column in columns:
            create_table_query += f'{column[0]} {column[1]}, '
        create_table_query = create_table_query[:-2] + ')'

        cursor.execute(create_table_query)
        cursor.executemany(f'INSERT INTO backup_db.{table[0]} VALUES ({",".join(["?"] * len(columns))})', rows)

    cursor.execute('COMMIT')

    # Close the database connection
    connection.close()

@app.route('/archive_old_data')
def archive_old_data():
    six_months_ago = datetime.now() - timedelta(seconds = 5)
    tables = [User, Ticket, Piece]  # list your table models here

    for table in tables:
        # Select rows older than six months
        rows = table.query.filter(table.created_at < six_months_ago).all()

        if rows:
            # Add rows to the archive database and remove them from the main database
            for row in rows:
                db.session.execute(f"INSERT INTO {table.__tablename__} SELECT * FROM main.{table.__tablename__} WHERE id = :id", params={'id': row.id})
                db.session.delete(row)

            db.session.commit()

    return 'Data archived'


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


    prenom = StringField('Prénom', validators=[DataRequired()])
    nom = StringField('Nom', validators=[DataRequired()])
    tel = StringField('Téléphone', validators=[DataRequired()])
    
    # Informations sur la pièce automobile
    immat = StringField("Immatriculation")
    marque = StringField('Marque')
    modele = StringField("Modèle")
    libelle = StringField('Libellé')
    code_constr_moteur = StringField('Ref Constructeur')

    def validate_energie(form, field):
        pass

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

def add_employee():
    new_employee = Employee(nom = "Lisa")
    new_employee2 = Employee(nom = "Fabien")
    new_employee3 = Employee(nom = "Kevin")
    

    db.session.add_all([new_employee, new_employee2, new_employee3])
    db.session.commit()

 
@app.route('/ticket', methods=['GET', 'POST'])
def submit_ticket():
    #add_categories()
    #add_employee()

    with open("modeles.json") as f:
        data = json.load(f)

    form = TicketForm()



    if form.validate_on_submit():

        return redirect(url_for('liste'))
    else:
        print(form.errors)


    categories = Category.query.all()
    employee = Employee.query.all()

    return render_template('add_profile.html', form=form, category = categories, employee = employee, data=data)


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

    for key, value in data.items():
        if isinstance(value, list):
            data[key] = [item for item in value if item is not None]

    print(data)
    for i in range(len(data["immat"])):    #TODO
        print("run")
        try:
            category = Category.query.filter_by(category_name=data['category'][i]).first()
            employee = Employee.query.filter_by(nom=data["employee"]).first()
            new_pieces.append(Piece(ouvert_par = employee.id, ticket_id=new_ticket.id, category_id = category.id, immat = data["immat"][i], marque = data["marque"][i], modele = data["modele"][i], libelle = data["libelle"][i], numero = data["numero"][i], energie = data["energie"][i], etat = "En attente de traitement", details = data["details"][i], prix = "A définir", phase = data["phase"][i]))
        except Exception as e:
            print("Error: ", str(e))

        print(new_pieces)
        print("end")

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
                    markup_links.append(Markup('<a href="{}">{}</a>'.format(url_for('admin_pieces.edit_view', id=piece.id), piece.libelle)))
            return Markup(", ".join(markup_links))
        return ''

    column_formatters = {
        'pieces': _user_formatter
    }

    column_labels = {
        'prenom' : "Prénom / Société",
        'nom' : "Nom / Contact (Entreprise)"

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
        user=lambda v, c, m, p: Markup(f'<a href="{get_url("admin_clients.edit_view", id=m.user.id)}">{m.user.nom}</a>') if m.user else '',
        pieces=lambda v, c, m, p: Markup(', '.join([f'<a href="{get_url("admin_pieces.edit_view", id=piece.id)}">{piece.libelle}</a>' for piece in m.pieces])),
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
    can_edit = False

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
        filters.FilterEqual(column=Piece.ref_mot, name='ref_mot'),
    )

    column_formatters = dict(
        user=lambda v, c, m, p: Markup(f'<a href="{get_url("admin_clients.edit_view", id=m.user.id)}">{m.user.nom} {m.user.prenom}</a>') if m.user else '',
        ouvert_par= lambda v, c, m, p: m.ouvert_employee.nom if m.ouvert_employee else '',
        gere_par= lambda v, c, m, p: m.gere_employee.nom if m.gere_employee else ''
    )

    column_list = ('immat', 'marque', 'modele', 'phase', 'libelle', 'numero', 'ref_mot', 'energie', 'details', 'etat', 'prix', 'user', "ouvert_par", "gere_par", 'ticket_status')

    column_labels = {
        'user': 'Client', 
        'ouvert_par' : 'Crée par',
        'gere_par' : "Géré par",
        'ticket_status' : "Status du ticket",
        'numero' : "Ref Constructeur",
        'ref_mot' : "Ref Moteur"
    }






def is_table_empty(table_name):
    with app.app_context():
        return db.session.query(table_name).count() == 0


#add_categories()
#add_employee()


admin = Admin(app, name='Base de donnée [Administrateur]', template_mode='bootstrap3', url='/admin-db', endpoint='admin_db')
babel.init_app(app, locale_selector=lambda : 'fr')

admin.add_view(UserAdmin(User, db.session, name='Clients', endpoint='admin_clients'))  # give the view a unique name
admin.add_view(TicketAdmin(Ticket, db.session, name='Tickets', endpoint='admin_tickets'))
admin.add_view(PieceAdmin(Piece, db.session, name='Pièces', endpoint='admin_pieces'))
admin.add_view(ModelView(Category, db.session, name='Catégories', endpoint='admin_categories'))
admin.add_view(ModelView(Employee, db.session, name='Employés', endpoint='admin_employees'))



































class UserAdmin2(ModelView):
    can_edit = False
    can_create = False
    can_delete = False

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
                    markup_links.append(Markup('<a href="{}">{}</a>'.format(url_for('user_pieces.edit_view', id=piece.id), piece.libelle)))
            return Markup(", ".join(markup_links))
        return ''

    column_formatters = {
        'pieces': _user_formatter
    }

    column_labels = {
        'prenom' : "Prénom / Société",
        'nom' : "Nom / Contact (Entreprise)"

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

    column_list = ['id', 'status', 'created_at', 'user', 'pieces']

    column_labels = {
        'id': 'N° Ticket',
        'created_at' : 'Date de création',
        'user' : 'Client',
        'pieces' :  'Pièces'
    }


#Piece
class PieceAdmin2(ModelView):
    can_edit = False
    can_create = False
    can_delete = False

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
        filters.FilterEqual(column=Piece.ref_mot, name='ref_mot'),
    )

    column_formatters = dict(
        user=lambda v, c, m, p: Markup(f'<a href="{get_url("user_clients.edit_view", id=m.user.id)}">{m.user.nom} {m.user.prenom}</a>') if m.user else '',
        ouvert_par= lambda v, c, m, p: m.ouvert_employee.nom if m.ouvert_employee else '',
        gere_par= lambda v, c, m, p: m.gere_employee.nom if m.gere_employee else ''
    )

    column_list = ('immat', 'marque', 'modele', 'phase', 'libelle', 'numero', 'ref_mot', 'energie', 'details', 'etat', 'prix', 'user', "ouvert_par", "gere_par", 'ticket_status')

    column_labels = {
        'user': 'Client', 
        'ouvert_par' : 'Crée par',
        'gere_par' : "Géré par",
        'ticket_status' : "Status du ticket",
        'numero' : "Ref Constructeur",
        'ref_mot' : "Ref Moteur"
    }

class ReadOnlyModelView(ModelView):
    can_edit = False
    can_delete = False
    can_create = False



admin2 = Admin(app, name='Base de donnée', template_mode='bootstrap3', url='/user-db', endpoint='user_db')

admin2.add_view(UserAdmin2(User, db.session, name='Clients', endpoint='user_clients'))  # give the view a unique name
admin2.add_view(TicketAdmin2(Ticket, db.session, name='Tickets', endpoint='user_tickets'))
admin2.add_view(PieceAdmin2(Piece, db.session, name='Pièces', endpoint='user_pieces'))
admin2.add_view(ReadOnlyModelView(Category, db.session, name='Catégories', endpoint='user_categories'))
admin2.add_view(ReadOnlyModelView(Employee, db.session, name='Employés', endpoint='user_employees'))


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)


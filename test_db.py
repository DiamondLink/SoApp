from app import db, app, User, Ticket, Category, Employee, Piece, add_categories, add_employee
import random

import random
from random import randrange
import string

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

with app.app_context():
    add_categories()
    add_employee()


for j in range(10000):
    with app.app_context():
        new_user = User(type_client=generate_random_string(7), nom = generate_random_string(7), tel=str(randrange(1111111111, 9999999999)), code_postal = generate_random_string(5))
        db.session.add(new_user)
        db.session.commit()
        new_ticket = Ticket(user_id=new_user.id, status="En attente de traitement")
        db.session.add(new_ticket)
        db.session.commit()
        new_pieces=Piece(ouvert_par = randrange(1, 4), ticket_id=new_ticket.id, category_id = randrange(1, 4), immat = generate_random_string(6), marque = generate_random_string(5), modele = generate_random_string(5), libelle = generate_random_string(4), numero = generate_random_string(4), energie = generate_random_string(5), etat = "En attente de traitement", details =generate_random_string(2), prix = "A définir")
        db.session.add(new_pieces)
        db.session.commit()
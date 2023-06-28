from app import db, app, Part, Ticket

ticket1 = Ticket(type_client = "Ind", prenom = "Baptiste", nom ="Villeneuve", tel = "07")
ticket2 = Ticket(type_client = "Ind", prenom = "aaaBaptiste", nom ="aaaVilleneuve", tel = "aaa07")

part1 = Part(immat = "a", marque = "a", modele = "a", libelle = "a", energie = "a", ticket = ticket2)
part2 = Part(immat = "ba", marque = "ba", modele = "ba", libelle = "ba", energie = "bba", ticket = ticket1)

with app.app_context():
    db.session.add_all([ticket1, ticket2])


    db.session.add_all([part1, part2])

    db.session.commit()
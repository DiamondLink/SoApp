from app import Ticket, app
 
with app.app_context():
    tickets = Ticket.query.all()

    for t in tickets:
        print(t.prenom)
        for pa in t.parts:
            print(pa.immat)
        print("\n")
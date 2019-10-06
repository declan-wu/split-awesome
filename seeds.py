from app import db, Bill, Item, User

# jackson = User("test@test.com", "L3QuMCBojXSGeHG9UrQAwet9MnV2", "Kevin", "Suen")
# kevin = User("test1@test.com", "L3QuMCBojXSGeHG9UrQAwet9MnV3", "Jackson", "Fung")
kevin = db.session.query(User).filter(User.id == 1).first()

fries = db.session.query(Item).filter(Item.id == 1).first()


kevin.items.append(fries)

db.session.add(kevin)
db.session.commit()

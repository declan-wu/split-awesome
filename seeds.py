from app import db, Bill, Item, User

new_user = User("test@test.com", "L3QuMCBojXSGeHG9UrQAwet9MnV2", "Kevin", "Suen")
db.session.add(new_user)
db.session.commit()


new_bill = Bill("L3QuMCBojXSGeHG9UrQAwet9MnV2")
fries = Item("fries", 1.5)
junior = Item('junior chicken', 2.2)
new_bill.items = [fries, junior]


db.session.add(new_bill)
db.session.commit()

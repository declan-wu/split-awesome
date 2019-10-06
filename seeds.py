from app import db, Bill, Item, User

jackson = User("test@test.com", "L3QuMCBojXSGeHG9UrQAwet9MnV2", "Kevin", "Suen")
kevin = User("test1@test.com", "L3QuMCBojXSGeHG9UrQAwet9MnV3", "Jackson", "Fung")
new_bill = Bill("L3QuMCBojXSGeHG9UrQAwet9MnV2")

fries = Item("large fries", 6.5)
junior = Item('junior chicken', 2.2)
pop = Item('sprite', 2)

new_bill.items = [fries, junior, pop]
jackson.items = [fries, junior]
kevin.items = [pop]

db.session.add(jackson)
db.session.add(kevin)
db.session.add(new_bill)
db.session.commit()

db.session.commit()

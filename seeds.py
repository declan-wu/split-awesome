from app import db, Bill, Item, User

# jackson = User("test@test.com", "L3QuMCBojXSGeHG9UrQAwet9MnV2", "Kevin", "Suen")
# kevin = User("test@test.com", "yGjatOFUiVOlXUAOg6K5hqS5YMs2", "Jackson", "Fung")
# kevin = db.session.query(User).filter(User.id == 1).first()

# fries = db.session.query(Item).filter(Item.id == 1).first()


# kevin.items.append(fries)

# db.session.add(kevin)
# db.session.commit()

new_user = User("test@test.com", "yGjatOFUiVOlXUAOg6K5hqS5YMs2", "Jackson", "Fung")

db.session.add(new_user)
db.session.commit()

new_bill = Bill("yGjatOFUiVOlXUAOg6K5hqS5YMs2")
fries = Item("fries", 1.5)
junior = Item('junior chicken', 2.2)
new_bill.items = [fries, junior]

db.session.add(new_bill)
db.session.commit()
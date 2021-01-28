from db_manipulator import Database
from settings import owner
db = Database('users.db')

print(db.user_portfolios(owner))
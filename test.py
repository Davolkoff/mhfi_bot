from db_manipulator import Database
from settings import owner
db = Database("users.db")

print(db.portfolio_sectors(owner, 1))
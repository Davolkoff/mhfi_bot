from db_manipulator import Database
from settings import owner
import sm_info as sm

db = Database("users.db")

print(db.portfolio_sectors(owner, 1))

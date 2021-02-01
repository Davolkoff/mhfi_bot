from db_manipulator import Database
from settings import owner

import messages
db = Database('users.db')

print(messages.my_portfolios(owner))
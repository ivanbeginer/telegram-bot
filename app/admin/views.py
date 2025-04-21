from app.core.orders.models import Order, Product
from app.core.users.models import User
from sqladmin import ModelView

class UserAdmin(ModelView, model=User):
    column_list = [User.user_id, User.is_waiter]

class OrderAdmin(ModelView,model=Order):
    column_list = [Order.id,Order.user_id,Order.status]

class ProductAdmin(ModelView,model=Product):
    column_list = [Product.id,Product.name, Product.price]


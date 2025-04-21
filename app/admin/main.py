import uvicorn
from sqladmin import Admin
from starlette.applications import Starlette

from app.admin.auth import AdminAuthBackend
from app.admin.views import UserAdmin, OrderAdmin, ProductAdmin
from app.infra.base import Base
from app.infra.postgres.db import DataBase
from settings.config import AppSettings


class AdminApp:
    def __init__(self,app_settings:AppSettings):
        self.web_app = Starlette()
        self.database = DataBase(app_settings.POSTGRES_DSN.get_secret_value(), declarative_base=Base)
        self.admin = Admin(self.web_app,self.database._engine, authentication_backend=AdminAuthBackend(settings=app_settings),base_url='/')
        self._register_views()

    def _register_views(self)->None:
        self.admin.add_view(UserAdmin)
        self.admin.add_view(OrderAdmin)
        self.admin.add_view(ProductAdmin)

def create_app()->Starlette:
    app = AdminApp(AppSettings())
    return app.web_app
if __name__=='__main__':
    settings = AppSettings()
    uvicorn.run('app.admin.main:create_app',host='127.0.0.1',port=settings.ADMIN_INTERFACE_PORT, log_level='info',workers=1)

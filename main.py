import logging
import time

from telegram import BotDescription
from telegram.ext import Application as PTBAppLication, ApplicationBuilder

from app.core.orders.repositories import OrderRepository, ProductRepository
from app.core.orders.services import OrderService, ProductService
from app.core.users.constants import RolesEnum
from app.jobs.sync_role import sync_roles
from settings.config import AppSettings
from app.infra.postgres.db import DataBase
from app.hendlers import HANDLERS
from app.core.users.repositories import UserRepository
from app.core.users.services import UserService
from app.infra.base import Base
from ptbcontrib.roles import RolesHandler, setup_roles

class Application(PTBAppLication):
    def __init__(self, app_settings: AppSettings, **kwargs):
        super().__init__(**kwargs)
        self._settings = app_settings
        self._roles = setup_roles(self)

        self.database = DataBase(app_settings.POSTGRES_DSN.get_secret_value(), declarative_base=Base)
        user_repository = UserRepository(database=self.database)
        self.user_service = UserService(repository=user_repository)
        order_repository = OrderRepository(database=self.database)
        self.order_service = OrderService(repository=order_repository)
        product_repository = ProductRepository(database=self.database)
        self.product_service = ProductService(repository=product_repository)
    @staticmethod
    async def application_startup(application:'Application')->None:
        await application.database.create_tables()
        await application.setup_roles()
        application._register_handlers()
        application.setup_jobs()
    @staticmethod
    async def application_shutdown(application: 'Application') -> None:
        await application.database.shutdown()
    def run(self)->None:
        self.run_polling()

    def _register_handlers(self):
        for handler in HANDLERS:
            if handler.role:
                if self._roles is None:
                    raise Exception('roles are not setup')

                self.add_handler(RolesHandler(handler.handler, roles=self._roles[handler.role]))

            else:
                self.add_handler(handler.handler)

    async def setup_roles(self)->None:
        for role in RolesEnum:
            if role not in self._roles:
                self._roles.add_role(role)
            for user_id in await self.user_service.get_user_ids_for_role(RolesEnum[role]):
                self._roles[role].add_member(user_id)

    def setup_jobs(self)->None:
        if self.job_queue is None:

            raise Exception('job queue missing')
        _roles_sync = self.job_queue.run_repeating(sync_roles,interval=60)



def configure_logging():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level= logging.INFO
    )
    logging.getLogger('httpx').setLevel(logging.WARNING)

def create_app(app_settings:...)->Application:
    appLication = (ApplicationBuilder().
                   application_class(Application, kwargs={'app_settings':app_settings})
                   .arbitrary_callback_data(True)
                   .post_init(Application.application_startup)
                   .post_shutdown(Application.application_shutdown)
                   .read_timeout(30)
                   .write_timeout(30)
                   .token(app_settings.TELEGRAM_API_KEY.get_secret_value()).build())

    return appLication # type: ignore[arg-type]



if __name__=='__main__':
    configure_logging()
    settings = AppSettings()
    app = create_app(settings)
    app.run()
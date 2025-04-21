from telegram.ext import BaseHandler, CommandHandler, CallbackQueryHandler
from typing import cast
from dataclasses import dataclass
from app.core.users.constants import RolesEnum
from app.hendlers.commands import start, waiter_start, create_order, add_item, finish_order, waiter_finish_order
from app.hendlers.filters import filter_for_command
from telegram.ext.filters import Regex

@dataclass
class Handler:
    handler:BaseHandler
    role:RolesEnum | None = None


HANDLERS: tuple[Handler,...] = (Handler(handler=CommandHandler('start',waiter_start),role=RolesEnum.waiter),
                                Handler(handler=CommandHandler('start',start)),
                                Handler(handler=CallbackQueryHandler(create_order,pattern=filter_for_command('create_order'))),
                                Handler(handler=CallbackQueryHandler(add_item,pattern=filter_for_command('add_item'))),
                                Handler(handler=CallbackQueryHandler(finish_order,pattern=filter_for_command('finish_order'))),
                                Handler(handler=CallbackQueryHandler(waiter_finish_order,pattern=filter_for_command('waiter_finish_order')),role=RolesEnum.waiter),)




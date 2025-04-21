from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from app.core.orders.constants import OrderStatusEnum
from app.core.orders.models import Product, Order


def build_order_buttons(order_id:int,items:list[Product])->InlineKeyboardMarkup:
    keyboard = []
    for item in items:
        keyboard.append([InlineKeyboardButton(text=f'{item.name}',callback_data=('add_item',order_id,item.id))])
    keyboard.append([InlineKeyboardButton('завершить заказ',callback_data=('finish_order',order_id))])
    return InlineKeyboardMarkup(keyboard)

def format_order_contents(order:Order)->str:
    if order.products:
        msg_text = '<b>В вашей корзине</b>\n'
        for ordered_product in order.products:
            msg_text+=f'-<b>{ordered_product.product.name}:</b>{ordered_product.amount}\n'
        if order.status == OrderStatusEnum.unlisted:
            msg_text +='Выберите то-то еще, либо оформите заказ'
    else:
        msg_text = '<b>Корзина пуста</b>\n'
    return msg_text

def format_order_contents_for_waiter(order:Order)->str:
    msg_text=''
    for ordered_product in order.products:
        msg_text+= f'- <b>{ordered_product.product.name}:</b>{ordered_product.amount}\n'
    return msg_text

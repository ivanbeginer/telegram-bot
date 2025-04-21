
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from typing import cast
from app.core.orders.constants import OrderStatusEnum
from app.core.orders.exeptions import ActiveOrderExists
from app.core.orders.services import OrderService, ProductService
from app.core.users.services import UserService
from app.hendlers.helpers import build_order_buttons, format_order_contents


async def start(update: Update, context:ContextTypes.DEFAULT_TYPE)->None:
    if update.effective_chat and update.effective_user:
        await context.application.user_service.register_visitor(update.effective_user.id)
        keyboard = [
            [InlineKeyboardButton('сделать заказ',callback_data=('create_order',))]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=update.effective_chat.id, text='добро пожаловать',reply_markup=markup)


async def waiter_start(update:Update, context:ContextTypes.DEFAULT_TYPE)->None:
    if update.effective_chat and update.effective_user:
        await context.application.user_service.register_visitor(update.effective_user.id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text='добро пожаловать на работу')

async def create_order(update:Update, context:ContextTypes.DEFAULT_TYPE)->None:
    query = update.callback_query
    await query.answer()

    order_service: OrderService = context.application.order_service
    product_service:ProductService = context.application.product_service
    try:
        order_id = await order_service.create_order(update.effective_user.id)
        items = await product_service.list_products()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Добавьте позиции в заказ',
            reply_markup=build_order_buttons(order_id,items)
        )
    except ActiveOrderExists:
        active_order = await order_service.get_active_order_for_user(user_id=update.effective_user.id)
        if active_order.status == OrderStatusEnum.ordered:
            await context.bot.send_message(chat_id=update.effective_chat.id,text=f'Что бы создать заказ дождитесь завершения текущего\n Текущий: <b>{active_order.id}</b>\n\n {format_order_contents(active_order)}',parse_mode=ParseMode.HTML)
        elif active_order.status == OrderStatusEnum.unlisted:
            items = await context.application.product_service.list_products()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=format_order_contents(active_order),reply_markup=build_order_buttons(active_order.id,items),parse_mode=ParseMode.HTML)

async def add_item(update:Update, context:ContextTypes.DEFAULT_TYPE)->None:
    query = update.callback_query
    await query.answer()
    callback_data = query.data
    order_service: OrderService = context.application.order_service
    product_service:ProductService = context.application.product_service

    order_id,item_id = int(callback_data[1]),int(callback_data[2])
    products = await product_service.list_products()

    await order_service.add_product_to_order(order_id,item_id)
    order = await order_service.get_order_by_id(order_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=format_order_contents(order),reply_markup=build_order_buttons(order_id,products),parse_mode=ParseMode.HTML)

async def finish_order(update:Update, context:ContextTypes.DEFAULT_TYPE)->None:
    query = update.callback_query
    await query.answer()
    callback_data = query.data
    order_service: OrderService = context.application.order_service
    user_service:UserService = context.application.user_service
    order_id = int(callback_data[1])

    await order_service.send_order_to_waiters(order_id)
    await context.bot.send_message(chat_id=update.effective_chat.id,text='заказ был передан официанту, ожидайте в ближайшее время')
    waiter_users_id = await user_service.repository.get_waiter_user_ids()
    order = await order_service.get_order_by_id(order_id)
    for waiter_user_id in waiter_users_id:
        await context.bot.send_message(chat_id=waiter_user_id,text=f'Создан новый заказ: {order_id}\n\n {format_order_contents(order)}',reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='Заказ доставлен',callback_data=('waiter_finish_order',order_id))]]))


async def waiter_finish_order(update:Update, context:ContextTypes.DEFAULT_TYPE)->None:
    order_service: OrderService = context.application.order_service
    query = update.callback_query
    await query.answer()
    callback_data = query.data
    order_id = int(callback_data[1])
    await order_service.mark_order_done(order_id)
    await context.bot.send_message(chat_id=update.effective_chat.id,text='Заказ завершен')

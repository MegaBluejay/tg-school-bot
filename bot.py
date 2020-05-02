from toolz.curried import *
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram import error
from school import digest
from datetime import datetime,time,timedelta,timezone
from ruamel.yaml import YAML
import os
import logging
yaml = YAML(typ='safe')

CommandHandler = curry(CommandHandler)
MessageHandler = curry(MessageHandler)
CallbackQueryHandler = curry(CallbackQueryHandler)

TOKEN = '826409377:AAHQB2o4zQbFSEZkLDlhQaNv4GPoxRRfHGU'
NAME = 'tg-school-bot'
PORT = os.environ.get('PORT','8443')

subjects = yaml.load(open('./subjects'))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logger = logging.getLogger(__name__)

updater = Updater(token=TOKEN, use_context=1)
dispatcher = updater.dispatcher

@CommandHandler('start')
def start(update,context):
    context.bot.send_message(chat_id=update.effective_chat.id,text='HW!')
@MessageHandler(Filters.text & (~Filters.command))
def echo(update,context):
    context.bot.send_message(chat_id=update.effective_chat.id,text=update.message.text)

def generate_message(args=None):
    if args:
        offset, *tm = args
        t = datetime.combine(datetime.now(timezone(timedelta(hours=3))) + timedelta(days=int(offset)), time(*map(int, tm)))
    else:
        t = datetime.now()
    is_lesson, n, left, current, nxt = digest(t)
    if n is not None:
        message =  f"""
{'Current' if is_lesson else 'Previous'} ({n}) lesson: {current}
{f'Next lesson: {nxt}' if nxt else ''}
{int(str(left).split(':')[1])} mins left to end of {'lesson' if is_lesson else 'break'}"""
    else:
         message = "it's over"
    face_name = subjects[current]
    return message,face_name

@CommandHandler('status')
def status(update,context):
    message, face_name = generate_message(context.args)
    msg = context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    photo = context.bot.send_photo(chat_id=update.effective_chat.id,photo=open('./assets/'+face_name, 'rb'))
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('refresh', callback_data='refresh'+str(photo.message_id))]])
    msg.edit_reply_markup(reply_markup=reply_markup)

@CallbackQueryHandler(pattern='refresh')
def refresh(update,context):
    message, face_name = generate_message()
    if message != update.callback_query.message.text:
        msg = context.bot.edit_message_text(chat_id=update.effective_chat.id,message_id=update.callback_query.message.message_id,
                                      text=message)
        old_id = int(update.callback_query.data.split('refresh')[1])
        try:
            photo = context.bot.edit_message_media(chat_id=update.effective_chat.id,message_id=old_id, media=InputMediaPhoto(open('./assets/'+face_name,'rb')))
            photo_id = photo.message_id
        except error.BadRequest:
            photo_id = old_id
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('refresh',callback_data='refresh'+str(photo_id))]])
        msg.edit_reply_markup(reply_markup=reply_markup)

dispatcher.add_handler(start)
dispatcher.add_handler(echo)
dispatcher.add_handler(status)
dispatcher.add_handler(refresh)

updater.start_webhook(listen='0.0.0.0',
                      port=int(PORT),
                      url_path=TOKEN)
updater.bot.set_webhook(f'https://{NAME}.herokuapp.com/{TOKEN}')
updater.idle()

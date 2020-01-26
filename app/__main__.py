"""Telegram bot"""

import re

from telegram import ParseMode
from telegram.ext import MessageHandler, CommandHandler, Filters, ConversationHandler, RegexHandler

from app import LOGGER, BOT, UPDATER

from app import database
from app.conversations.add_account import ADD_ACCOUNT_CONV


def cmd_start(update, context):
    """Start command"""
    update.message.reply_text(
        'Hello {},\ntype /help for a list of commands'.format(update.message.from_user.first_name))

def cmd_help(update, context):
    """Help command"""
    message_list = [
        '**Command list**',
        '/accounts - list of accounts',
        '/add\\_account - add account to list',
    ]
    message = '\n'.join(message_list)
    print(message)
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

def cmd_accounts(update, context):
    """Return account list"""
    accounts = database.get_rr_accounts(update.message.from_user.id)
    message_list = ['Accounts verified to this Telgeram account:']
    for account in accounts:
        # name = re.sub(r'\[.*\]\s', '', account.name)
        desktop_link = '[desktop](https://rivalregions.com/#slide/profile/{})'.format(account.id)
        mobile_link = '[mobile](https://m.rivalregions.com/#slide/profile/{})'.format(account.id)
        message_list.append(
            '• {} {} - {}'.format(
                escape_text(account.name),
                desktop_link,
                mobile_link,
            )
        )
    message = '\n'.join(message_list)
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

def escape_text(text):
    """Escape text"""
    return text \
        .replace("_", "\\_") \
        .replace("*", "\\*") \
        .replace("[", "\\[") \
        .replace("`", "\\`")

def main():
    """Main function"""
    dispatcher = UPDATER.dispatcher

    # general commands
    dispatcher.add_handler(CommandHandler('start', cmd_start))
    dispatcher.add_handler(CommandHandler('help', cmd_help))

    # account commaonds
    dispatcher.add_handler(CommandHandler('accounts', cmd_accounts))

    dispatcher.add_handler(ADD_ACCOUNT_CONV)

    UPDATER.start_polling()
    UPDATER.idle()

if __name__ == '__main__':
    main()

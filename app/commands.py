"""Telegram commands"""

from telegram import ParseMode


from app import database, functions
from app.models import TelegramAccount


def cmd_start(update, context):
    """Start command"""
    update.message.reply_text(
        'Hello {},\ntype /help for a list of commands'.format(update.message.from_user.first_name))
    telegram_account = database.get_telegram_account(update.message.from_user.id)
    if not telegram_account:
        database.add_telegram_account(update)


def cmd_help(update, context):
    """Help command"""
    message_list = [
        '**Command list**',
        '/accounts - list of accounts',
        '/add\\_account - add account to list',
    ]
    message = '\n'.join(message_list)
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

def cmd_accounts(update, context):
    """Return account list"""
    message_list = ['Accounts verified to this Telgeram account:']
    telegram_account = database.get_telegram_account(update.message.from_user.id)
    if telegram_account:
        accounts = database.get_rr_accounts(telegram_account)
    else:
        accounts = []
    if not accounts:
        message_list.append('• none')
    for account in accounts:
        desktop_link = '[desktop](https://rivalregions.com/#slide/profile/{})'.format(account.id)
        mobile_link = '[mobile](https://m.rivalregions.com/#slide/profile/{})'.format(account.id)
        message_list.append(
            '• {} {} - {}'.format(
                functions.escape_text(account.name),
                desktop_link,
                mobile_link,
            )
        )
    message = '\n'.join(message_list)
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

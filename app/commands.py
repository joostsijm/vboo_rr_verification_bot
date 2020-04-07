"""Telegram commands"""

from telegram import ParseMode

from app import LOGGER, database, functions


def cmd_start(update, context):
    """Start command"""
    LOGGER.info('"@%s" start bot', update.message.from_user.username)
    update.message.reply_text(
        'Hello {}, use /add to add an account, use /help for a list of commands.'.format(
            update.message.from_user.first_name
        )
    )
    telegram_account = database.get_telegram_account(update.message.from_user.id)
    if not telegram_account:
        database.add_telegram_account(update)

def cmd_help(update, context):
    """Help command"""
    message_list = [
        '**Command list**',
        '/add - add verified account',
        '/remove - remove verified account',
        '/accounts - list of verified accounts',
    ]
    message = '\n'.join(message_list)
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

def cmd_accounts(update, context):
    """Return player list"""
    message_list = ['Accounts verified to this Telgeram account:']
    telegram_account = database.get_telegram_account(update.message.from_user.id)
    if telegram_account:
        players = database.get_rr_players(telegram_account)
    else:
        players = []
    if not players:
        message_list.append('• none')
    for player in players:
        desktop_link = '[desktop](https://rivalregions.com/#slide/profile/{})'.format(player.id)
        mobile_link = '[mobile](https://m.rivalregions.com/#slide/profile/{})'.format(player.id)
        message_list.append(
            '• {} {} - {}'.format(
                functions.escape_text(player.name),
                desktop_link,
                mobile_link,
            )
        )
    message = '\n'.join(message_list)
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

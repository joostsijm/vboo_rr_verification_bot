"""Telegram commands"""

from telegram import ParseMode

from app import LOGGER, database, functions


def cmd_start(update, context):
    """Start command"""
    LOGGER.info('"@%s" start bot', update.message.from_user.username)
    update.message.reply_text(
        'Hello {}, use /add to add an player, use /help for a list of commands.'.format(
            update.message.from_user.first_name
        )
    )
    telegram_player = database.get_telegram_player(update.message.from_user.id)
    if not telegram_player:
        database.add_telegram_player(update)


def cmd_help(update, context):
    """Help command"""
    message_list = [
        '**Command list**',
        '/add - add account to list',
        '/players - list of accounts',
    ]
    message = '\n'.join(message_list)
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

def cmd_accounts(update, context):
    """Return player list"""
    message_list = ['Accounts verified to this Telgeram player:']
    telegram_player = database.get_telegram_player(update.message.from_user.id)
    if telegram_player:
        players = database.get_rr_players(telegram_player)
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

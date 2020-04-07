"""Add player conversation"""

import random
import string

from telegram import ParseMode
from telegram.ext import MessageHandler, CommandHandler, Filters, ConversationHandler

from app import api, functions, database, HEADERS, BASE_URL, LOGGER


PLAYER_NUMBER, CHOOSE, CONFIRM, VERIFICATION = range(4)

def conv_start(update, context):
    """Start conversion"""
    LOGGER.info('"@%s" start remove account conversation', update.message.from_user.username)
    update.message.reply_text('Starting removal conversation, use /cancel to stop.')
    return conv_ask_player(update, context)

def conv_ask_player(update, context):
    """Ask player id"""
    message_list = ['Send the number of account you would like to remove:']
    telegram_account = database.get_telegram_account(update.message.from_user.id)
    if not telegram_account:
        update.message.reply_text('No accounts found')
        return ConversationHandler.END
    players = database.get_rr_players(telegram_account)
    if not players:
        update.message.reply_text('No accounts found')
        return ConversationHandler.END

    context.user_data['player_list'] = players
    if not players:
        message_list.append('• none')
    index = 1
    for player in players:
        desktop_link = '[desktop](https://rivalregions.com/#slide/profile/{})'.format(player.id)
        mobile_link = '[mobile](https://m.rivalregions.com/#slide/profile/{})'.format(player.id)
        message_list.append(
            '{}: {} {} - {}'.format(
                index,
                functions.escape_text(player.name),
                desktop_link,
                mobile_link,
            )
        )
        index += 1
    message = '\n'.join(message_list)
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    return PLAYER_NUMBER

def conv_choose_player(update, context):
    """Ask max resource"""
    index = int(update.message.text)
    try:
        player = context.user_data['player_list'][index - 1]
    except IndexError:
        update.message.reply_text(
            'Number {} not found, give me another number.'.format(index)
        )
        return PLAYER_NUMBER
    update.message.reply_text(
        'Send `confirm` to remove {} from verified accounts.'.format(
            functions.escape_text(player.name)
        ),
        parse_mode=ParseMode.MARKDOWN
    )
    context.user_data['player'] = player
    return CONFIRM

def get_player(player_id):
    """Get player by ID"""
    try:
        return api.get_rr_player(player_id)
    except api.PlayerNotFoundException:
        return False

def conv_player_confirm(update, context):
    """Sending announcement"""
    player = context.user_data['player']
    LOGGER.info('"@%s" remove verified account %s', update.message.from_user.username, player.name)
    update.message.reply_text(
        'Removing verified account.',
        parse_mode=ParseMode.MARKDOWN
    )
    database.remove_verified_player(update.message.from_user.id, player.id)
    context.user_data.clear()
    return ConversationHandler.END

def conv_cancel(update, context):
    """Cancel announcement"""
    update.message.reply_text('Canceled action.')
    context.user_data.clear()
    return ConversationHandler.END

# announcement conversation
REMOVE_CONV = ConversationHandler(
    entry_points=[CommandHandler('remove', conv_start)],
    states={
        PLAYER_NUMBER: [
            MessageHandler(Filters.regex(r'^\d*$'), conv_choose_player),
            MessageHandler(Filters.text, conv_ask_player),
        ],
        CONFIRM: [
            MessageHandler(Filters.regex('(?i)confirm'), conv_player_confirm),
            MessageHandler(Filters.text, conv_cancel),
        ],
    },
    fallbacks=[CommandHandler('cancel', conv_cancel)]
)

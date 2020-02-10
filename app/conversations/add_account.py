"""Add player conversation"""

import random
import string

from telegram import ParseMode
from telegram.ext import MessageHandler, CommandHandler, Filters, ConversationHandler

from app import api, functions, database, HEADERS, BASE_URL, LOGGER


PLAYER_ID, CHOOSE, CONFIRM, VERIFICATION = range(4)

def conv_ask_player_id(update, context):
    """Ask player id"""
    LOGGER.info('"@%s" start add player conversation', update.message.from_user.username)
    update.message.reply_text('Send me your Rival Regions player name or ID.')
    return PLAYER_ID

def conv_player_choose(update, context):
    """Ask max resource"""
    player_name = update.message.text
    LOGGER.info(
        '"@%s" searching for player name "%s"', 
        update.message.from_user.username,
        player_name
    )
    players = api.get_players_by_name(player_name)
    if len(players) == 0:
        update.message.reply_text('No players found witht that name, try again')
        return PLAYER_ID
    context.user_data['player_list'] = players
    message = 'Chose from list:\n'
    for num, player in enumerate(players, start=1):
        message += '{}) {} ({})\n'.format(num, player['name'], player['level'])
    update.message.reply_text(message)
    return CHOOSE

def conv_player_number_error(update, context):
    """Wrong input error"""
    incorrect_input = update.message.text
    LOGGER.info(
        '"@%s" incorrect number number "%s"',
        update.message.from_user.username,
        incorrect_input
    )
    update.message.reply_text(
        '{}, I don\'t recognize that. What number?'.format(
            incorrect_input
        )
    )
    return CHOOSE

def conv_player_id_confirm(update, context):
    """Confirm player """
    player_id = int(update.message.text)
    if player_id <= 25:
        player_index = player_id-1
        if player_index >= len(context.user_data['player_list']):
            update.message.reply_text('{} is not an option, try again.'.format(player_id),)
            return CHOOSE
        player = context.user_data['player_list'][player_index]
        player_id = player['id']
    context.user_data['player_id'] = player_id
    update.message.reply_text(
        'Retreiving player from Rival Regions, this might take a couple seconds.'
    )
    LOGGER.info(
        '"@%s" RR player id "%s"',
        update.message.from_user.username,
        player_id
    )
    player = api.get_rr_player(player_id)

    message_list = [
        '*Player details*',
        '*ID*: {}'.format(player_id),
        '*Name*: {}'.format(functions.escape_text(player['name'])),
        '*Region*: {}'.format(player['region']),
        '*Residency*: {}'.format(player['residency']),
        '*Registration date*: {}'.format(player['registation_date']),
        '\nPlease confirm this is your player by typing \'confirm\'.',
    ]

    update.message.reply_text(
        '\n'.join(message_list),
        parse_mode=ParseMode.MARKDOWN
    )
    return CONFIRM

def conv_verification(update, context):
    """Sending announcement"""
    update.message.reply_text(
        'Verification code will be send to your Rival Region player in a couple of secconds. ' + \
        'Check your personal messages for a verification code and send it here.',
        parse_mode=ParseMode.MARKDOWN
    )
    letters = string.ascii_lowercase
    verification_code = ''.join(random.choice(letters) for i in range(5))
    LOGGER.info(
        '"@%s" verification code "%s"',
        update.message.from_user.username,
        verification_code
    )
    message = 'Your verification code:\n{}\n\n'.format(verification_code) + \
    'Please don\'t share this code except with @rr_verification_bot on Telegram.'
    api.send_personal_message(context.user_data['player_id'], message)
    context.user_data['verification_code'] = verification_code
    return VERIFICATION

def conv_finish(update, context):
    """Sending announcement"""
    verification_code = update.message.text
    if verification_code != context.user_data['verification_code']:
        LOGGER.info(
            '"@%s" wrong verification code try "%s"',
            update.message.from_user.username,
            verification_code,
        )
        if 'tries' not in context.user_data:
            context.user_data['tries'] = 0
        context.user_data['tries'] += 1
        if context.user_data['tries'] >= 3:
            LOGGER.info(
                '"@%s" too many wrong verification tries', 
                update.message.from_user.username
            )
            update.message.reply_text(
                'Failed verification to many times, canceled action.',
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data.clear()
            return ConversationHandler.END
        update.message.reply_text(
            'Verificated code doesn\'t match, try again.',
            parse_mode=ParseMode.MARKDOWN
        )
        return VERIFICATION
    player_id = context.user_data['player_id']
    LOGGER.info(
        '"@%s" succesfully verified RR player "%s"',
        update.message.from_user.username,
        player_id,
    )
    database.verify_rr_player(update.message.from_user.id, player_id)
    update.message.reply_text(
        'Verificated your Rival Region player to Telegram. Type /players to see your players',
        parse_mode=ParseMode.MARKDOWN
    )
    context.user_data.clear()
    return ConversationHandler.END

def conv_error_finish(update, context):
    """Ask max resource"""
    incorrect_input = update.message.text
    update.message.reply_text(
        '"{}" not recognized. Send me the verification code.\n/cancel to cancel'.format(
            incorrect_input
        ),
    )
    return VERIFICATION

def conv_cancel(update, context):
    """Cancel announcement"""
    update.message.reply_text('Canceled action.')
    context.user_data.clear()
    return ConversationHandler.END

# announcement conversation
ADD_ACCOUNT_CONV = ConversationHandler(
    entry_points=[CommandHandler('add_account', conv_ask_player_id)],
    states={
        PLAYER_ID: [
            MessageHandler(Filters.regex(r'^\d*$'), conv_player_id_confirm),
            MessageHandler(Filters.text, conv_player_choose),
        ],
        CHOOSE: [
            MessageHandler(Filters.regex(r'^\d*$'), conv_player_id_confirm),
            MessageHandler(Filters.text, conv_player_choose),
        ],
        CONFIRM: [
            MessageHandler(Filters.regex('confirm'), conv_verification),
            MessageHandler(Filters.text, conv_cancel),
        ],
        VERIFICATION: [
            MessageHandler(Filters.regex(r'^([a-z]|\d)+$'), conv_finish),
            MessageHandler(Filters.text, conv_error_finish),
        ],
    },
    fallbacks=[CommandHandler('cancel', conv_cancel)]
)

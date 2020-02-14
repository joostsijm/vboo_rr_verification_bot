"""Add player conversation"""

import random
import string

from telegram import ParseMode
from telegram.ext import MessageHandler, CommandHandler, Filters, ConversationHandler

from app import api, functions, database, HEADERS, BASE_URL, LOGGER


PLAYER_ID, CHOOSE, CONFIRM, VERIFICATION = range(4)

def conv_ask_player_id(update, context):
    """Ask player id"""
    LOGGER.info('"@%s" start add account conversation', update.message.from_user.username)
    update.message.reply_text(
        'Starting add account conversation, use /cancel to stop.' +
        ' Send me your Rival Regions account name or ID.'
    )
    return PLAYER_ID

def conv_player_choose(update, context):
    """Ask max resource"""
    player_name = update.message.text
    LOGGER.info(
        '"@%s" searching for player name "%s"', 
        update.message.from_user.username,
        player_name
    )
    update.message.reply_text(
        'Searching for \'{}\', this might take a couple seconds.'.format(player_name)
    )
    players = api.get_players_by_name(player_name)
    if len(players) == 0:
        update.message.reply_text('No accounts found witht that name, try again.')
        return PLAYER_ID
    if len(players) == 1:
        player = players[0]
        player_id = player['id']
        if database.is_connected(update.message.from_user.id, player_id):
            update.message.reply_text('Account already connected.')
            context.user_data.clear()
            return ConversationHandler.END
        context.user_data['player_id'] = player_id
        player = get_player(player_id)
        if not player:
            LOGGER.warn(
                '"@%s" Can\'t find RR player ID "%s"',
                update.message.from_user.username, player_id
            )
            update.message.reply_text('Couldn\'t find an account by that ID, try again.')
            return PLAYER_ID
        ask_confirmation(update, player)
        return CONFIRM
    context.user_data['player_list'] = players
    message = 'Choose from list:\n'
    for num, player in enumerate(players, start=1):
        message += '{}) {} ({})\n'.format(num, player['name'], player['level'])
    update.message.reply_text(message)
    return CHOOSE

def conv_player_id_confirm(update, context):
    """Confirm player ID"""
    player_id = int(update.message.text)
    if player_id <= 25:
        player_index = player_id-1
        if player_index >= len(context.user_data['player_list']):
            update.message.reply_text('{} is not an option, try again.'.format(player_id),)
            return CHOOSE
        player = context.user_data['player_list'][player_index]
        player_id = player['id']
    if database.is_connected(update.message.from_user.id, player_id):
        update.message.reply_text('Account already connected.')
        context.user_data.clear()
        return ConversationHandler.END
    context.user_data['player_id'] = player_id
    update.message.reply_text(
        'Retreiving account from Rival Regions, this might take a couple seconds.'
    )
    player = get_player(player_id)
    if not player:
        LOGGER.warn(
            '"@%s" Can\'t find RR player ID "%s"',
            update.message.from_user.username, player_id
        )
        update.message.reply_text('Couldn\'t find an account by that ID, try again.')
        return CHOOSE
    ask_confirmation(update, player)
    return CONFIRM

def get_player(player_id):
    """Get player by ID"""
    try:
        return api.get_rr_player(player_id)
    except api.PlayerNotFoundException:
        return False

def ask_confirmation(update, player):
    """Get account and ask for confirmation"""
    LOGGER.info(
        '"@%s" Ask for confirmation on RR player ID "%s"',
        update.message.from_user.username, player.id
    )

    message_list = [
        '*Player details*',
        '*ID*: {}'.format(player.id),
        '*Name*: {}'.format(functions.escape_text(player['name'])),
        '*Region*: {}'.format(player['region']),
        '*Residency*: {}'.format(player['residency']),
        '*Registration date*: {}'.format(player['registation_date']),
    ]

    update.message.reply_text(
        '\n'.join(message_list),
        parse_mode=ParseMode.MARKDOWN
    )
    update.message.reply_text('Please confirm this is your account by typing \'confirm\'.')
        

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
    'Telegram user @{} tried to add this account. '.format(
        update.message.from_user.username
    ) + \
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
        '"@%s" succesfully verified RR account "%s"',
        update.message.from_user.username,
        player_id,
    )
    database.verify_rr_player(update.message.from_user.id, player_id)
    update.message.reply_text(
        'Verificated your Rival Region player to Telegram. Type /accounts to see your accounts',
        parse_mode=ParseMode.MARKDOWN
    )
    context.user_data.clear()
    return ConversationHandler.END

def conv_error_finish(update, context):
    """Wrong verification code"""
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
ADD_CONV = ConversationHandler(
    entry_points=[CommandHandler('add', conv_ask_player_id)],
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
            MessageHandler(Filters.regex('(?i)confirm'), conv_verification),
            MessageHandler(Filters.text, conv_cancel),
        ],
        VERIFICATION: [
            MessageHandler(Filters.regex(r'^([a-z]|\d)+$'), conv_finish),
            MessageHandler(Filters.text, conv_error_finish),
        ],
    },
    fallbacks=[CommandHandler('cancel', conv_cancel)]
)

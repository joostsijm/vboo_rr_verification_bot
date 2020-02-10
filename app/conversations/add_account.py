"""Add account conversation"""

import random
import string

from telegram import ParseMode
from telegram.ext import MessageHandler, CommandHandler, Filters, ConversationHandler

from app import api, functions, database, HEADERS, BASE_URL, LOGGER


ACCOUNT_ID, CHOOSE, CONFIRM, VERIFICATION = range(4)

def conv_ask_account_id(update, context):
    """Ask account id"""
    LOGGER.info('"@%s" start add account conversation', update.message.from_user.username)
    update.message.reply_text('Send me your Rival Regions account name or ID.')
    return ACCOUNT_ID

def conv_account_choose(update, context):
    """Ask max resource"""
    account_name = update.message.text
    LOGGER.info(
        '"@%s" searching for account name "%s"', 
        update.message.from_user.username,
        account_name
    )
    accounts = api.get_accounts_by_name(account_name)
    if len(accounts) == 0:
        update.message.reply_text('No accounts found witht that name, try again')
        return ACCOUNT_ID
    context.user_data['account_list'] = accounts
    message = 'Chose from list:\n'
    for num, account in enumerate(accounts, start=1):
        message += '{}) {} ({})\n'.format(num, account['name'], account['level'])
    update.message.reply_text(message)
    return CHOOSE

def conv_account_number_error(update, context):
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

def conv_account_id_confirm(update, context):
    """Confirm account """
    account_id = int(update.message.text)
    if account_id <= 25:
        account_index = account_id-1
        if account_index >= len(context.user_data['account_list']):
            update.message.reply_text('{} is not an option, try again.'.format(account_id),)
            return CHOOSE
        account = context.user_data['account_list'][account_index]
        account_id = account['id']
    context.user_data['account_id'] = account_id
    update.message.reply_text(
        'Retreiving account from Rival Regions, this might take a couple seconds.'
    )
    LOGGER.info(
        '"@%s" RR account id "%s"',
        update.message.from_user.username,
        account_id
    )
    account = api.get_rr_account(account_id)

    message_list = [
        '*Account details*',
        '*ID*: {}'.format(account_id),
        '*Name*: {}'.format(functions.escape_text(account['name'])),
        '*Region*: {}'.format(account['region']),
        '*Residency*: {}'.format(account['residency']),
        '*Registration date*: {}'.format(account['registation_date']),
        '\nPlease confirm this is your account by typing \'confirm\'.',
    ]

    update.message.reply_text(
        '\n'.join(message_list),
        parse_mode=ParseMode.MARKDOWN
    )
    return CONFIRM

def conv_verification(update, context):
    """Sending announcement"""
    update.message.reply_text(
        'Verification code will be send to your Rival Region account in a couple of secconds. ' + \
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
    api.send_personal_message(context.user_data['account_id'], message)
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
    account_id = context.user_data['account_id']
    LOGGER.info(
        '"@%s" succesfully verified RR account "%s"',
        update.message.from_user.username,
        account_id,
    )
    database.verify_rr_account(update.message.from_user.id, account_id)
    update.message.reply_text(
        'Verificated your Rival Region account to Telegram. Type /accounts to see your accounts',
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
    entry_points=[CommandHandler('add_account', conv_ask_account_id)],
    states={
        ACCOUNT_ID: [
            MessageHandler(Filters.regex(r'^\d*$'), conv_account_id_confirm),
            MessageHandler(Filters.text, conv_account_choose),
        ],
        CHOOSE: [
            MessageHandler(Filters.regex(r'^\d*$'), conv_account_id_confirm),
            MessageHandler(Filters.text, conv_account_choose),
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

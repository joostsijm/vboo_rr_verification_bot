"""Add account conversation"""

from telegram import ParseMode
from telegram.ext import MessageHandler, CommandHandler, Filters, ConversationHandler, RegexHandler


ACCOUNT_ID, CONFIRM, VERIFICATION = range(3)

def conv_ask_account_id(update, context):
    """Ask account id"""
    update.message.reply_text('What\'s your Rival Regions acount ID?')
    return ACCOUNT_ID

def conv_error_ask_account_id(update, context):
    """Ask max resource"""
    incorrect_input = update.message.text
    update.message.reply_text(
        '{}, I don\'t recognize that. What\'s your Rival Regions account ID?'.format(
            incorrect_input
        ),
    )
    return ACCOUNT_ID

def conv_account_id_confirm(update, context):
    """Sending announcement"""
    account_id = update.message.text

    message_list = [
        '**Account details**',
        'ID: {}'.format(account_id),
        'Name: {}'.format(account_id),
        'Region: {}'.format(account_id),
        'Residency: {}'.format(account_id),
        '\nPlease confirm this is your account by typing \'confirm\'',
    ]

    update.message.reply_text(
        '\n'.join(message_list),
        parse_mode=ParseMode.MARKDOWN
    )
    return CONFIRM

def conv_verification(update, context):
    """Sending announcement"""
    update.message.reply_text(
        'Verification code send to your Rival Region account ' + \
        'Check your personal messages for a verification code and send it here.',
        parse_mode=ParseMode.MARKDOWN
    )
    return VERIFICATION

def conv_finish(update, context):
    """Sending announcement"""
    update.message.reply_text(
        'Verificated your Rival Region account to Telegram',
        parse_mode=ParseMode.MARKDOWN
    )
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
            RegexHandler(r'^\d*$', conv_account_id_confirm),
            MessageHandler(Filters.text, conv_error_ask_account_id),
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

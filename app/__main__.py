"""Telegram bot"""

from telegram.ext import CommandHandler

from app import LOGGER, UPDATER, commands
from app.conversations.add_account import ADD_ACCOUNT_CONV


def main():
    """Main function"""
    dispatcher = UPDATER.dispatcher

    # commands
    dispatcher.add_handler(CommandHandler('start', commands.cmd_start))
    dispatcher.add_handler(CommandHandler('help', commands.cmd_help))
    dispatcher.add_handler(CommandHandler('accounts', commands.cmd_accounts))

    # conversations
    dispatcher.add_handler(ADD_ACCOUNT_CONV)

    UPDATER.start_polling()
    UPDATER.idle()

if __name__ == '__main__':
    main()

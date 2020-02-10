"""Database functons"""

from datetime import datetime

from app import SESSION, LOGGER
from app.models import Player, TelegramAccount, TelegramHandle, PlayerTelegram


def add_telegram_account(update):
    """Add new Telegram account"""
    session = SESSION()
    telegram_account = TelegramAccount()
    telegram_account.id = update.message.from_user.id
    telegram_account.name = update.message.from_user.name
    telegram_account.registration_date = datetime.now()
    session.add(telegram_account)
    session.commit()
    session.close()
    return telegram_account

def get_telegram_account(telegram_id):
    """Get Telegram account"""
    session = SESSION()
    telegram_account = _get_telegram_account(session, telegram_id)
    session.close()
    return telegram_account

def get_rr_accounts(telegram_account):
    """Get Rival Region accounts associated with Telegram account"""
    LOGGER.info(
        '"%s" get RR accounts',
        telegram_account.id,
    )
    session = SESSION()
    accounts = _get_rr_accounts(session, telegram_account.id)
    session.close()
    return accounts

def verify_rr_account(telegram_id, account_id):
    """Verify RR account in database"""
    session = SESSION()
    telegram_account = _get_telegram_account(session, telegram_id)
    accounts = _get_rr_accounts(session, telegram_id)
    for account in accounts:
        if account.id == account_id:
            LOGGER.info(
                '"%s" account already connected "%s"',
                telegram_id,
                account_id
            )
            session.close()
            return

    active_player_telegrams = session.query(PlayerTelegram) \
        .filter(PlayerTelegram.until_date_time != None) \
        .all()
    for active_player_telegram in active_player_telegrams:
        LOGGER.info(
            '"%s" unconnect account "%s"',
            active_player_telegram.telegram_id,
            account_id
        )
        active_player_telegram.until_date_time = datetime.now()

    LOGGER.info(
        '"%s" connecting account "%s"',
        telegram_id,
        account_id
    )
    player_telegram = PlayerTelegram()
    player_telegram.telegram_id = telegram_account.id
    player_telegram.player_id = account_id
    player_telegram.from_date_time = datetime.now()
    session.add(player_telegram)
    session.commit()
    session.close()

def _get_telegram_account(session, telegram_id):
    """Return telegram_account"""
    return session.query(TelegramAccount).get(telegram_id)

def _get_rr_accounts(session, telegram_account_id):
    """Get Rival Region accounts associated with Telegram account"""
    return session.query(Player) \
        .join(Player.player_telegram) \
        .filter(PlayerTelegram.telegram_id == telegram_account_id) \
        .filter(PlayerTelegram.until_date_time == None) \
        .all()


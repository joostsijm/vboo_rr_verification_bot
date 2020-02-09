"""Database functons"""

from app import SESSION
from app.models import Player, TelegramAccount, TelegramHandle, PlayerTelegram, TelegramVerification


def add_telegram_account(update):
    """Add new Telegram account"""
    session = SESSION()
    telegram_account = TelegramAccount()
    telegram_account.id = update.message.from_user.id
    telegram_account.name = update.message.from_user.name
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

def _get_telegram_account(session, telegram_id):
    """Return telegram_account"""
    return session.query(TelegramAccount).get(telegram_id)

def get_rr_accounts(telegram_account):
    """Get Rival Region accounts associated with Telegram account"""
    session = SESSION()
    rr_accounts = session.query(Player) \
        .join(Player.player_telegram) \
        .filter(PlayerTelegram.telegram_id == telegram_account.id) \
        .all()
    session.close()
    return rr_accounts

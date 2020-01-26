"""Database functons"""

from app import SESSION
from app.models import Player, TelegramAccount, TelegramHandle, PlayerTelegram, TelegramVerification


def get_telegram_account(telegram_id):
    """Get Telegram account"""
    session = SESSION()
    telegram_account = _get_telegram_account(session, telegram_id)
    session.close()
    return telegram_account

def _get_telegram_account(session, telegram_id):
    """Return telegram_account"""
    return session.query(TelegramAccount).get(telegram_id)

def get_rr_accounts(telegram_id):
    """Get Rival Region accounts associated with Telegram account"""
    session = SESSION()
    telegram_account = _get_telegram_account(session, telegram_id)
    rr_accounts = session.query(Player) \
        .join(Player.player_telegram) \
        .filter(PlayerTelegram.telegram_id == telegram_account.id) \
        .all()
    session.close()
    return rr_accounts

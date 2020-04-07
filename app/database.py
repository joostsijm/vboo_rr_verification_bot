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

def get_rr_players(telegram_account):
    """Get Rival Region players associated with Telegram player"""
    LOGGER.info('"%s" get RR accounts', telegram_account.id,)
    session = SESSION()
    players = _get_rr_players(session, telegram_account.id)
    LOGGER.info('"%s" found %s RR accounts', telegram_account.id, len(players))
    session.close()
    return players

def verify_rr_player(telegram_id, player_id):
    """Verify RR player in database"""
    session = SESSION()
    telegram_account = _get_telegram_account(session, telegram_id)
    players = _get_rr_players(session, telegram_id)
    for player in players:
        if player.id == player_id:
            LOGGER.info(
                '"%s" player already connected "%s"',
                telegram_id,
                player_id
            )
            session.close()
            return

    active_player_telegrams = session.query(PlayerTelegram) \
        .filter(PlayerTelegram.until_date_time == None) \
        .filter(PlayerTelegram.player_id == player_id) \
        .all()
    for active_player_telegram in active_player_telegrams:
        LOGGER.info(
            '"%s" unconnect player "%s"',
            active_player_telegram.telegram_id,
            player_id
        )
        active_player_telegram.until_date_time = datetime.now()

    LOGGER.info(
        '"%s" connecting player "%s"',
        telegram_id,
        player_id
    )
    player_telegram = PlayerTelegram()
    player_telegram.telegram_id = telegram_account.id
    player_telegram.player_id = player_id
    player_telegram.from_date_time = datetime.now()
    session.add(player_telegram)
    session.commit()
    session.close()

def remove_verified_player(telegram_account_id, player_id):
    """Remove Telegram player"""
    session = SESSION()
    player_telegram = session.query(PlayerTelegram) \
        .filter(PlayerTelegram.telegram_id == telegram_account_id) \
        .filter(PlayerTelegram.player_id == player_id) \
        .filter(PlayerTelegram.until_date_time == None) \
        .first()
    if player_telegram:
        player_telegram.until_date_time = datetime.now()
        session.commit()
        return True
    return False

def is_connected(telegram_id, player_id):
    """Check if account is already"""
    session = SESSION()
    player_telegram = session.query(PlayerTelegram) \
        .filter(PlayerTelegram.until_date_time == None) \
        .filter(PlayerTelegram.telegram_id == telegram_id) \
        .filter(PlayerTelegram.player_id == player_id) \
        .first()
    session.close()
    return bool(player_telegram)

def _get_telegram_account(session, telegram_id):
    """Return telegram_account"""
    return session.query(TelegramAccount).get(telegram_id)

def _get_rr_players(session, telegram_account_id):
    """Get Rival Region players associated with Telegram player"""
    return session.query(Player) \
        .join(Player.player_telegram) \
        .filter(PlayerTelegram.telegram_id == telegram_account_id) \
        .filter(PlayerTelegram.until_date_time == None) \
        .all()

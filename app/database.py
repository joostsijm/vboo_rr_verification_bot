"""Database functons"""

from datetime import datetime

from app import SESSION, LOGGER
from app.models import Player, TelegramAccount, TelegramHandle, PlayerTelegram


def add_telegram_player(update):
    """Add new Telegram player"""
    session = SESSION()
    telegram_player = TelegramAccount()
    telegram_player.id = update.message.from_user.id
    telegram_player.name = update.message.from_user.name
    telegram_player.registration_date = datetime.now()
    session.add(telegram_player)
    session.commit()
    session.close()
    return telegram_player

def get_telegram_player(telegram_id):
    """Get Telegram player"""
    session = SESSION()
    telegram_player = _get_telegram_player(session, telegram_id)
    session.close()
    return telegram_player

def get_rr_players(telegram_player):
    """Get Rival Region players associated with Telegram player"""
    LOGGER.info(
        '"%s" get RR players',
        telegram_player.id,
    )
    session = SESSION()
    players = _get_rr_players(session, telegram_player.id)
    session.close()
    return players

def verify_rr_player(telegram_id, player_id):
    """Verify RR player in database"""
    session = SESSION()
    telegram_player = _get_telegram_player(session, telegram_id)
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
        .filter(PlayerTelegram.until_date_time != None) \
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
    player_telegram.telegram_id = telegram_player.id
    player_telegram.player_id = player_id
    player_telegram.from_date_time = datetime.now()
    session.add(player_telegram)
    session.commit()
    session.close()

def _get_telegram_player(session, telegram_id):
    """Return telegram_player"""
    return session.query(TelegramAccount).get(telegram_id)

def _get_rr_players(session, telegram_player_id):
    """Get Rival Region players associated with Telegram player"""
    return session.query(Player) \
        .join(Player.player_telegram) \
        .filter(PlayerTelegram.telegram_id == telegram_player_id) \
        .filter(PlayerTelegram.until_date_time == None) \
        .all()


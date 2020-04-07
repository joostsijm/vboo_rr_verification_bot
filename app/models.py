"""Database models"""

from sqlalchemy import Column, ForeignKey, Integer, String, \
    DateTime, BigInteger, Date, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Player(Base):
    """Model for player"""
    __tablename__ = 'player'
    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    nation = Column(String)
    registration_date = Column(Date)


class TelegramAccount(Base):
    """Model for Telegram account"""
    __tablename__ = 'telegram_account'
    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    registration_date = Column(DateTime)


class TelegramHandle(Base):
    """Model for Telegram handle"""
    __tablename__ = 'telegram_handle'
    id = Column(Integer, primary_key=True)
    handle = Column(String)
    registration_date = Column(DateTime)

    telegram_account_id = Column(BigInteger, ForeignKey('telegram_account.id'))
    telegram_account = relationship(
        'TelegramAccount',
        backref=backref('account_handles', lazy='dynamic')
    )


class PlayerTelegram(Base):
    """Model for belongs to"""
    __tablename__ = 'player_telegram'
    player_id = Column(BigInteger, ForeignKey('player.id'), primary_key=True)
    telegram_id = Column(BigInteger, ForeignKey('telegram_account.id'), primary_key=True)
    from_date_time = Column(DateTime, primary_key=True)
    until_date_time = Column(DateTime)

    player = relationship(
        'Player',
        backref=backref('player_telegram', lazy='dynamic')
    )

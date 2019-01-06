from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Numeric
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Session = sessionmaker()

Base = declarative_base()

class Candle(Base):
    __tablename__ = 'candles'

    dt = Column(String, primary_key=True)
    open = Column(Numeric)
    high = Column(Numeric)
    low = Column(Numeric)
    close = Column(Numeric)
    volume = Column(Numeric)
    day = Column(String, index=True)

    def __init__(self, dt, open, high, low, close, volume, day):
        self.dt = dt
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.day = day

    @classmethod
    def add_list(cls, session, dict_list):
        for row in dict_list:
            if len(row['dt']) == 0:
                return
            candle = Candle(row['dt'], row['open'], row['high'], row['low'], row['close'], row['volume'], row['day'])
            session.merge(candle)

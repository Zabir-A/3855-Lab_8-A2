from sqlalchemy import Column, Integer, String, DateTime, Float
from base import Base
import datetime


class Buy(Base):
    __tablename__ = "buy"

    id = Column(Integer, primary_key=True)

    buy_id = Column(String(250), nullable=False)
    item_name = Column(String(250), nullable=False)
    item_price = Column(Float, nullable=False)
    buy_qty = Column(Integer, nullable=False)
    trace_id = Column(String(250), nullable=False)
    date_created = Column(String(100), nullable=False)

    def __init__(self, buy_id, item_name, item_price, buy_qty, trace_id):
        self.buy_id = buy_id
        self.item_name = item_name
        self.item_price = item_price
        self.buy_qty = buy_qty
        self.trace_id = trace_id
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        dict = {}
        dict["id"] = self.id
        dict["buy_id"] = self.buy_id
        dict["item_name"] = self.item_name
        dict["item_price"] = self.item_price
        dict["buy_qty"] = self.buy_qty
        dict["trace_id"] = self.trace_id
        dict["date_created"] = self.date_created

        return dict

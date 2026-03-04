"""
Falsification test: HFT order-book state is deterministic.
Same order sequence gives same book state.

# @falsification_id: F_LUXURY_001
"""
import pytest

class OrderBook:
    def __init__(self):
        self.bids = {}
        self.asks = {}

    def add_order(self, side: str, price: float, qty: int):
        book = self.bids if side == "bid" else self.asks
        book[price] = book.get(price, 0) + qty

ORDERS = [
    ("bid", 100.0, 10),
    ("ask", 101.0, 5),
    ("bid", 100.0, 3),
    ("ask", 102.0, 2),
]

def build_book():
    b = OrderBook()
    for o in ORDERS:
        b.add_order(*o)
    return b

def test_orderbook_deterministic():
    b1 = build_book()
    b2 = build_book()
    assert b1.bids == b2.bids
    assert b1.asks == b2.asks

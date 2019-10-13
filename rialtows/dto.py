from .core import BaseDto, Mapping
import arrow


class ResourceDto(BaseDto):
    def __init__(self, data, name):
        super().__init__(data)
        self.name = name

    def __str__(self):
        return "%s [ask=%.2f, bid=%.2f]" % (self.name, self.ask, self.bid)

    def __repr__(self):
        return str(self)


def to_timestamp(date):
    return arrow.get(date).timestamp


class BinanceDto(ResourceDto):
    date = Mapping("E", converter=int)
    ask = Mapping("a", converter=float)
    bid = Mapping("b", converter=float)
    def __init__(self, data):
        super().__init__(data, "binance")


class OkexDto(ResourceDto):
    date = Mapping("timestamp", converter=to_timestamp)
    ask = Mapping("best_ask", converter=float)
    bid = Mapping("best_bid", converter=float)

    def __init__(self, data):
        super().__init__(data, "okex")

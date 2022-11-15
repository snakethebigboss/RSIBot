from blankly import Alpaca, Strategy, StrategyState
from blankly.indicators import rsi

def init(symbol, state: StrategyState):
    # Download price data to give context to the algo
    state.variables['history'] = state.interface.history(symbol, 150, 'deque', state.resolution)['close']
    state.variables['own_position'] = False

def price_event(price, symbol, state: StrategyState):
    """ This function will give an updated price every 15 seconds from our definition below """
    state.variables['history'].append(price)
    rsi = rsi(state.variables['history'])
    curr_value = state.interface.account[state.base_asset].available
    if rsi[-1] < 30 and not curr_value:
        # Dollar cost average buy
        buy = state.interface.cash / price
        state.interface.market_order(symbol, 'buy', buy)
        state.variables['own_position'] = True
    elif rsi[-1] > 70 and curr_value:
        # Dollar cost average sell
        state.interface.market_order(symbol, 'sell', curr_value)
        state.variables['own_position'] = False

exchange = Alpaca()
s = Strategy(exchange)

# Make the price event function above run every day
s.add_price_event(price_event, 'TSLA', '1d', init=init)
results = s.backtest('3y',{'USD': 10000})

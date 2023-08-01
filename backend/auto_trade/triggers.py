from binance.cm_futures import CMFutures
from binance.um_futures import UMFutures
# API Key:
#
# Secret Key:

def toppings_changed(*args, **kwargs):
    # Do something




    cm_futures_client = UMFutures()

    # get server time
    print(cm_futures_client.time())

    cm_futures_client = UMFutures(key='sZPSg57dqsozdCWsu0C4ikkkwMbb4svJxEqaHoWopn4yOyG98OVhdXM5e26l9vJ4', secret='JHuNugCdDLfCYtWUQfUwy9VVapS1V8wsREyDjRzdEoiBVOO744DlvpbjL7yRIgNJ')

    # Get account information
    print(cm_futures_client.account())

    # Post a new order
    params = {
        'symbol': 'BTCUSDT',
        'side': 'SELL',
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'quantity': 0.002,
        'price': 59808
    }

    response = cm_futures_client.new_order(**params)
    print(response)

#
# if __name__ == "__main__":
#     asyncio.run(main())
toppings_changed()
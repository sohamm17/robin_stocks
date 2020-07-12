import robin_stocks.helper as helper
import robin_stocks.account as account
import robin_stocks.profiles as profiles
from datetime import datetime, timedelta
from dateutil import parser
from operator import itemgetter

def binary_search(list, key_string, key):
    if list is None or len(list) == 0:
        return None
    length = len(list)
    index = int(length/2)
    if parser.parse(list[index][key_string]).date() == key:
        return list[index]
    elif key < parser.parse(list[index][key_string]).date():
        return binary_search(list[:(index)], key_string, key)
    else:
        return binary_search(list[(index + 1):], key_string, key)

@helper.login_required
def get_time_weighted_return():
    twr = 1.0

    # Get all the deposits and withdrawals
    allTransactions = account.get_bank_transfers()
    deposits = sorted([x for x in allTransactions if (x['direction'] == 'deposit') and (x['state'] == 'completed')], key=itemgetter('updated_at'))
    withdrawals = sorted([x for x in allTransactions if (x['direction'] == 'withdraw') and (x['state'] == 'completed')], key=itemgetter('updated_at'))
    transfers = sorted(deposits+withdrawals,key=itemgetter('updated_at'))

    # Get the histiorical of portfolio value for every day in last 5 years
    equity_history = sorted(account.get_historical_portfolio(interval='day',span='5year',info='equity_historicals'), key=itemgetter('begins_at'))

    last_close_value = 0
    last_deposit = 0
    cur_close_value = 0

    # for each transfer - find the last equity value before the transfer
    # then canculate the period's return
    # and keep multiplying like geometric mean to get time_weighted_return
    for t in transfers:
        period_profit = 0
        transfer_update = parser.parse(t['created_at']).date()
        e = binary_search(equity_history, 'begins_at', transfer_update - timedelta(1))
        if e is None:
            e = binary_search(equity_history, 'begins_at', transfer_update - timedelta(2))
        if e is None:
            e = binary_search(equity_history, 'begins_at', transfer_update - timedelta(3))
        if e is None:
            e = binary_search(equity_history, 'begins_at', transfer_update - timedelta(4))

        # print (e)
        cur_close_value = float(e['close_equity'])
        cur_deposit = float(t['amount']) if t['direction'] == 'deposit' else (-float(t['amount']))

        if last_close_value != 0:
            period_profit = (cur_close_value - (last_close_value + last_deposit)) / (last_close_value + last_deposit)
            twr = twr * (1 + period_profit)
            # print ("\nperiod profit: " + str(round((period_profit * 100), 2)) + "%.")

        last_deposit = cur_deposit
        last_close_value = cur_close_value
        # if e is not None:
        #    print ("Date: {0}\t Close Amount: {1}".format(parser.parse(e['begins_at']).strftime("%d-%b-%y"),e['close_equity']))
        # print ("UpdateDate: {0} Creat: {1}\t Type: {2} Amount: {3}".format(parser.parse(t['updated_at']).strftime("%d-%b-%y"),
        # parser.parse(t['created_at']).strftime("%d-%b-%y"), t['direction'], t['amount']))

    current_close_value = float(profiles.load_portfolio_profile(info='equity'))
    last_period_profit = (current_close_value - (last_close_value + last_deposit))/(last_close_value + last_deposit)
    twr = twr *  (1 + last_period_profit)

    # print ("\nperiod profit: " + str(round((last_period_profit * 100), 2)) + "%.")
    twr = 100 * (twr - 1)
    # print ("Time-weighted Return:" + str(round((twr), 2)) + "%.")
    return round(twr, 2)

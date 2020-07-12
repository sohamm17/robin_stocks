import robin_stocks as r
from time_weighted_return import get_time_weighted_return


r.authentication.login("USERNAME","PASSWORD",store_session=True)

print ("Time-weighted Return: " + str(get_time_weighted_return()) + "%.")

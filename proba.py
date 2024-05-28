import pytz

# Проверяем, что можем получить доступ к членам библиотеки pytz
try:
    tz = pytz.timezone('Europe/Moscow')
    print("Successfully accessed pytz.timezone")
except AttributeError:
    print("Error accessing pytz.timezone")

try:
    utc = pytz.utc
    print("Successfully accessed pytz.utc")
except AttributeError:
    print("Error accessing pytz.utc")

try:
    error = pytz.UnknownTimeZoneError
    print("Successfully accessed pytz.UnknownTimeZoneError")
except AttributeError:
    print("Error accessing pytz.UnknownTimeZoneError")
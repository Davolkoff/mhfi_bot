import datetime


# функция, которая адекватно отображает текущее время
def normal_now():
    day = datetime.datetime.now().day
    month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    hour = datetime.datetime.now().hour
    minute = datetime.datetime.now().minute
    second = datetime.datetime.now().second
    return str(day).zfill(2) + "." + str(month).zfill(2) + "." + str(year) + " " + \
           str(hour).zfill(2) + ":" + str(minute).zfill(2) + ":" + str(second).zfill(2)


# приведение даты в нормальный вид
def normalize_date(date):
    formated_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    return str(formated_date.day).zfill(2) + "." + str(formated_date.month).zfill(2) + "." + str(formated_date.year)

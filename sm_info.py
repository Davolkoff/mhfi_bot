import json  # библиотека для парсинга json файлов
import lxml.etree  # библиотека для парсинга xml файлов
import requests  # библиотека для работы с интернет-запросами
import tickers  # файл с тикерами
import finviz  # библиотека для связи с сервисом finviz
import lxml.html as LH  # модуль для парсинга xml страниц
import re  # модуль для работы со строками
import datetime  # модуль для получения времени
from bs4 import BeautifulSoup  # Модуль для работы с HTML


# получение цены бумаги с московской биржи
def get_moex_price(ticker):
    url = "https://iss.moex.com/iss/securities/" + ticker + ".xml?iss.meta=off&iss.only=boards&boards.columns=secid," \
                                                            "is_primary,boardid "
    answer = requests.get(url).content
    xml = lxml.etree.XML(answer)
    level = xml.xpath("//document//data//rows//row[@is_primary=1]/@boardid")[0]

    if level in ["TQOB", "EQOB", "TQOD", "TQCB", "EQQI", "TQIR"]:
        param = "bonds"
    else:
        param = "shares"

    url = "https://iss.moex.com/iss/engines/stock/markets/" + param + "/boards/" + level + "/securities.xml?iss.meta=off&iss" \
                                                                                           ".only=securities&securities" \
                                                                                           ".columns=SECID,PREVADMITTEDQUOTE "
    answer = requests.get(url).content
    xml = lxml.etree.XML(answer)
    return xml.xpath("//row[@SECID='" + ticker + "']/@PREVADMITTEDQUOTE")[0]


# получение цены бумаги с Yahoo Finance по тикеру
def get_yahoo_price(ticker):
    answer = requests.get(
        "https://query1.finance.yahoo.com/v10/finance/quoteSummary/" + ticker + "?modules=price").content
    return json.loads(answer)["quoteSummary"]["result"][0]["price"]["regularMarketPrice"]["raw"]


# получение валюты бумаги с Yahoo Finance по тикеру
def get_yahoo_wallet(ticker):
    answer = requests.get(
        "https://query1.finance.yahoo.com/v10/finance/quoteSummary/" + ticker + "?modules=price").content
    return json.loads(answer)["quoteSummary"]["result"][0]["price"]["currency"]


# получение ранга Zacks.com
def zacks_rank(ticker):
    answer = requests.get("https://quote-feed.zacks.com/" + ticker).content
    return json.loads(answer)[ticker]["zacks_rank"]


# получение названия биржи
def exchange(ticker):
    if ticker in tickers.moex_tickers:
        answer = requests.get(
            f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}.ME?modules=price").content
    else:
        answer = requests.get(f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=price").content
    return json.loads(answer)["quoteSummary"]["result"][0]["price"]["exchange"]


# получение дохода с начала года
def ytd_return(ticker):
    try:
        if ticker in tickers.moex_tickers:
            answer = requests.get(
                f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}.ME?modules=defaultKeyStatistics").content
        else:
            answer = requests.get(f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=defaultKeyStatistics").content
        return "\n<b>Доход с начала года:</b> "+json.loads(answer)["quoteSummary"]["result"][0]["defaultKeyStatistics"]["ytdReturn"]["fmt"] + "\n\n"
    except:
        return ""


# получение дивидендной доходности
def dividend(ticker):
    try:
        answer = requests.get(
            f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=defaultKeyStatistics").content
        return "\n<b>Дивидендная доходность:</b>" + json.loads(answer)["quoteSummary"]["result"][0]["defaultKeyStatistics"]["yield"]["fmt"] + "\n"
    except:
        return ""


# получение названия компании
def long_name(ticker):
    if ticker in tickers.moex_tickers:
        answer = requests.get(
            "https://query1.finance.yahoo.com/v10/finance/quoteSummary/" + ticker + ".ME?modules=price").content
    else:
        answer = requests.get("https://query1.finance.yahoo.com/v10/finance/quoteSummary/" + ticker + "?modules=price").content
    return json.loads(answer)["quoteSummary"]["result"][0]["price"]["longName"]


# объединение функций получения цены с Мосбиржи и Yahoo Finance для справок
def price_spr(ticker):
    if ticker in tickers.moex_tickers:
        return str(get_moex_price(ticker)) + " RUB"
    else:
        return str(get_yahoo_price(ticker)) + " " + str(get_yahoo_wallet(ticker))


# объединение функций получения цены с Мосбиржи и Yahoo Finance для расчётов
def price(ticker):
    if ticker in tickers.moex_tickers:
        return get_moex_price(ticker)
    else:
        return get_yahoo_price(ticker)


# объединение функций YF и мосбиржи для получения валюты
def wallet(ticker):
    if ticker in tickers.moex_tickers:
        return "RUB"
    else:
        return get_yahoo_wallet(ticker)


# проверка существования тикера
def ticker_exists(ticker):
    try:
        price_spr(ticker)
        return True
    except:
        return False

# получение значения volume из finviz
def finviz_volume(ticker):
    volume = int(str(finviz.get_stock(ticker)["Volume"]).replace(",", ""))
    return volume


# получение значения average volume из finviz
def finviz_avg_volume(ticker):
    if str(finviz.get_stock(ticker)["Avg Volume"])[-1] == "M":
        return int(str(finviz.get_stock(ticker)["Avg Volume"]).replace("M", "").replace(".", "")) * 10000
    elif str(finviz.get_stock(ticker)["Avg Volume"])[-1] == "K":
        return int(str(finviz.get_stock(ticker)["Avg Volume"]).replace("K", "").replace(".", "")) * 10
    else:
        return int(str(finviz.get_stock(ticker)["Avg Volume"]))


# сравнение дневного объёма со стандартным
def finviz_volume_compare(ticker):
    return finviz_volume(ticker)/finviz_avg_volume(ticker)


# редактирует введенное значение
def make_value(value):
    if "," in value:
        value = value.replace(",", ".")
    if " " in value:
        value = value.replace(" ", "")
    if "%" in value:
        value = value. replace("%", "")
    return ''.join(i for i in value if not i.isalpha())


# является ли значением
def is_value(value):
    try:
        float(make_value(value))
        return True
    except:
        return False


# дневное измененеие цены
def day_price_change(ticker):
    if ticker in tickers.moex_tickers:
        answer = requests.get(
            "https://query1.finance.yahoo.com/v10/finance/quoteSummary/" + ticker + ".ME?modules=price").content
        return float(json.loads(answer)["quoteSummary"]["result"][0]['price']['regularMarketChange']['fmt'])
    else:
        answer = requests.get(
            "https://query1.finance.yahoo.com/v10/finance/quoteSummary/" + ticker + "?modules=price").content
        return float(json.loads(answer)["quoteSummary"]["result"][0]['price']['regularMarketChange']['fmt'])


# дневное изменение цены в процентах
def day_price_change_percent(ticker):
    if ticker in tickers.moex_tickers:
        answer = requests.get(
            "https://query1.finance.yahoo.com/v10/finance/quoteSummary/" + ticker + ".ME?modules=price").content
        return float(str(json.loads(answer)["quoteSummary"]["result"][0]['price']['regularMarketChangePercent']['fmt']).replace("%",""))
    else:
        answer = requests.get(
            "https://query1.finance.yahoo.com/v10/finance/quoteSummary/" + ticker + "?modules=price").content
        return float(str(json.loads(answer)["quoteSummary"]["result"][0]['price']['regularMarketChangePercent']['fmt']).
                     replace("%",""))


# попытка сделать из числа float
def try_float(string):
    try:
        if "," in string:
            string = string.replace(",",".")
        if " " in string:
            string = string.replace(" ","")
        return float(string)
    except:
        return False


# получение отрасли по тикеру
def sector_by_ticker(ticker):
    if ticker in tickers.moex_tickers:
        answer = requests.get(
            f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}.ME?modules=assetProfile").content
        return json.loads(answer)["quoteSummary"]["result"][0]["assetProfile"]["sector"]
    else:
        answer = requests.get(
            f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=assetProfile").content
        return json.loads(answer)["quoteSummary"]["result"][0]["assetProfile"]["sector"]


# очистка кэша finviz
def finviz_clear_cache():
    finviz.main_func.STOCK_PAGE.clear()

# получение курса валюты
def currency_price(wallet):
	
	wallet_url = ''
	# Заголовки для передачи вместе с URL
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}

	current_converted_price = 0
	if wallet == "USD":
		wallet_url = 'https://www.google.com/search?sxsrf=ALeKk01NWm6viYijAo3HXYOEQUyDEDtFEw%3A1584716087546&' \
						'source=hp&ei=N9l0XtDXHs716QTcuaXoAg&q=%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80+%D0%BA+%D1%80%D1' \
						'%83%D0%B1%D0%BB%D1%8E&oq=%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80+&gs_l=psy-ab.3.0.35i39i70i258' \
						'j0i131l4j0j0i131l4.3044.4178..5294...1.0..0.83.544.7......0....1..gws-wiz.......35i39.5QL6' \
						'Ev1Kfk4'
	if wallet == "EUR":
		wallet_url = 'https://www.google.com/search?sxsrf=ALeKk01ZFuaBqz-hrNipwKI9Ay3_kxuhsw%3A1612675635328&ei' \
						'=M3ofYKi2E-zJrgS79YPICQ&q=евро+к+рублю&oq=tdhjк+рублю&gs_lcp=CgZwc3ktYWIQAxgAMgQIABANMgQIA' \
						'BANMgQIABANMgQIABANMgQIABANMgQIABANMgQIABANMgQIABANMgQIABANMgQIABANOgcIABCwAxBDOgYIABAHEB46' \
						'CAgAEAcQChAeOgQIABBDOgoIABAHEAoQHhAqUJKiB1iRtwdg0cIHaAJwAngAgAGTAYgB-AWSAQMyLjWYAQCgAQGqAQ' \
						'dnd3Mtd2l6yAEKwAEB&sclient=psy-ab'
	if wallet == "GBP":
		wallet_url = 'https://www.google.com/search?sxsrf=ALeKk02MiLG7ZghcxBO6ecMbtgqod7jACQ%3A1612675759581&ei' \
						'=r3ofYJiMI8rrrgT3-KCoCw&q=фунт+к+рублю&oq=aeynк+рублю&gs_lcp=CgZwc3ktYWIQAxgAMgQIABANMgQIA' \
						'BANMgQIABANMgQIABANMgQIABANMgQIABANMgQIABANMgQIABANMgQIABANMgQIABANOgcIABCwAxBDOgYIABAHE' \
						'B46CAgAEAcQChAeOgoIABAHEAoQHhAqULeFBljWiwZglpYGaAJwAngAgAFsiAGPBJIBAzAuNZgBAKABAaoBB2d3cy' \
						'13aXrIAQrAAQE&sclient=psy-ab'
	if wallet == "RUB":
		return float(1)	
	full_page = requests.get(wallet_url, headers=headers)

	# Разбираем через BeautifulSoup
	soup = BeautifulSoup(full_page.content, 'html.parser')

	# Получаем нужное для нас значение и возвращаем его
	convert = soup.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
	return float(convert[0].text.replace(",", "."))
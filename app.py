from sanic import Sanic
import json
from sanic.response import json
import urllib.request
from xml.dom import minidom

url = "http://www.cbr.ru/scripts/XML_daily.asp"


dict = {}
dict_kf = {'RUB': 1}


def parse():
    webFile = urllib.request.urlopen(url)
    data = webFile.read()
    UrlSplit = url.split("/")[-1]
    ExtSplit = UrlSplit.split(".")[1]
    FileName = UrlSplit.replace(ExtSplit, "xml")
    with open(FileName, "wb") as localFile:
        localFile.write(data)
        webFile.close()
    doc = minidom.parse(FileName)
    currency1 = doc.getElementsByTagName("Valute")
    for rate in currency1:
        charcode = rate.getElementsByTagName("CharCode")[0].firstChild.data
        value = round(float(rate.getElementsByTagName("Value")[0].firstChild.data.replace(",", ".")),2)
        dict.update({charcode: value})
        dict_kf.update({charcode: 1/value})


parse()

app = Sanic(__name__)


@app.route('/')
async def home(request):
    return json({"Hello":"world"})


def get_res_from_cur(cur):
    return dict[cur]


@app.route('/api/course/<currency>')
async def currency_get(request, currency):
    cur = currency
    res = get_res_from_cur(cur)
    return json({
        "currency": cur,
        "rub_course": res,
    })


def convertation(to_currency, from_currency, amount):
    return round((dict_kf[to_currency] / dict_kf[from_currency]) * amount, 2)


@app.route('/api/convert', methods=['POST'])
async def convert(request):
    from_currency = request.json.get('from_currency')
    to_currency = request.json.get('to_currency')
    amount = request.json.get('amount')
    curr = to_currency
    result = convertation(to_currency, from_currency, amount)
    return json({
        "currency": curr,
        "amount": result,
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
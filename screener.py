import requests
from bs4 import BeautifulSoup
import pandas as pd


def rowGetDataText(tr, coltag='td'):
    return [td.get_text(strip=True) for td in tr.find_all(coltag)]


class Screener:
    def __init__(self):
        self.url = ['https://finviz.com/screener.ashx?v=161&f=an_recom_buybetter,fa_pb_o1,sh_curvol_o5000,'
                    'sh_float_o10,sh_relvol_o3,ta_change_u2,ta_sma20_pa20,ta_sma200_pa50,'
                    'ta_sma50_pa30&ft=4&o=-earningsdate']
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/39.0.2171.95 Safari/537.36'
        }
        self.dict = {}
        self.__getData()
        self.dataFrame = self.__getDataFrame()

    def __getData(self):
        i = 0
        for u in self.url:
            html = requests.get(u, headers=self.headers).text
            self.dict[f'html{i}'] = BeautifulSoup(html, features="html.parser").find_all("table", attrs={
                "cellpadding": 3,
                "cellspacing": 1
            })[0]
            i += 1

    def __getDataFrame(self):
        tabela = self.__tableDataText()
        dataFrame = pd.DataFrame(tabela[1:], columns=tabela[0])
        dataFrame['Change'] = dataFrame['Change'].str.rstrip('%').astype('float') / 100.0
        return dataFrame

    def __tableDataText(self):
        rows = []
        trs = []
        for t in self.dict:
            trs.append(self.dict[t].find_all('tr'))
        headerow = rowGetDataText(trs[0][0])[0:18]
        if headerow:
            rows.append(headerow)
        print(len(self.dict))
        for tr in trs:
            tr = tr[1:]
            for t in tr:
                rows.append(rowGetDataText(t, 'td'))
        return rows

    def getCol(self, kolumna):
        return self.dataFrame[kolumna]

    def getTable(self):
        return self.dataFrame

    def getData(self):
        header = ["Ticker", "Price", "Change"]
        table = self.getTable()
        table.loc[table["Change"] < 0.2].to_csv('static/stonks.csv', columns=header)
        stronki = table.loc[table["Change"] < 0.2]
        return stronki

import fmpsdk as fmp
import datetime
import time
import pandas as pd
from tqdm import tqdm
from math import sqrt


class ScreenerAPI:
    def __init__(self):
        print('Starting...')
        self.__config = {
            'volume': 5000000,  # above
            'priceMax': 10,  # lower than
            'priceMin': 0.2,
            'percentGainMin': 2,
            'percentGainMax': 20,
            'RVOLMin': 3,
            'EMA': 20,
            'periods': self.__periodsSinceOpening()
        }
        self.__apikey = '187216e99799a61477ca9ac7dac75117'
        self.stonks = {}
        self.__periodsSinceOpening()
        self.__filterData()

    def __periodsSinceOpening(self):
        now = datetime.datetime.now()
        if now.isoweekday() <= 5 and now.hour < 21:
            opening = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
            diff = now - opening
            return (diff.total_seconds() / 60) // 5
        else:
            return 79

    def __getRawData(self):
        # Getting the company list from FMP
        companyList = fmp.stock_screener(self.__apikey,
                                         price_more_than=self.__config['priceMin'],
                                         price_lower_than=self.__config['priceMax'],
                                         exchange=['NYSE', 'NASDAQ'],
                                         limit=10000)
        print('Getting RAW data...')
        return companyList

    def __filterData(self):
        start_time = time.time()
        companyList = self.__getRawData()
        tickerList = []
        for company in companyList:
            tickerList.append(company['symbol'])
        # need to divide the list into chunks - API accepts requests with max ~1200 tickers
        tickerListChunks = (lambda lst: [lst[i:i + 1000] for i in range(0, len(lst), 1000)])(tickerList)
        j = 1
        print('Scanning chunks...')
        for chunk in tqdm(tickerListChunks):
            j += 1
            data = fmp.quote(self.__apikey, chunk)
            self.__preliminaryFilter(data)
        print('Scanning stocks...')
        for stonk in tqdm(self.stonks):
            self.stonks[stonk]['dataFull'] = fmp.technical_indicators(apikey=self.__apikey,
                                                                      symbol=stonk,
                                                                      period=self.__config['EMA'],
                                                                      time_delta='5min',
                                                                      statistics_type='ema')
            self.stonks[stonk]['data'] = self.stonks[stonk]['dataFull'][0]
        self.__checkEMA()
        self.__calculateVWAP()
        self.__checkVWAP()
        self.__removeData()  # removing dataFull, data, vwap
        print(f'Done, found {len(self.stonks)} stocks.')
        print(f"--- exec time {time.time() - start_time} seconds ---")

    def __preliminaryFilter(self, data):
        for company in data:
            try:
                if (company['volume'] >= self.__config['RVOLMin'] * company['avgVolume']) \
                        and (company['changesPercentage'] > self.__config['percentGainMin']) \
                        and (company['changesPercentage'] < self.__config['percentGainMax']):
                    self.stonks[company['symbol']] = {
                        'symbol': company['symbol'],
                        'exchange': company['exchange'],
                        'earnings': datetime.datetime.fromisoformat(company['earningsAnnouncement'][:-5]),
                        'market cap': "{:d}".format(int(company['marketCap'])),
                        'price': company['price'],
                        'change': company['change'],
                        'change percent': company['changesPercentage'],
                        'volume': company['volume'],
                        'avg volume': company['avgVolume'],
                    }
            except TypeError:
                pass

    def __checkEMA(self):
        # Checking if price is above EMA.
        x = []
        for stonk in self.stonks:
            dataFull = self.stonks[stonk]['dataFull']
            data = self.stonks[stonk]['dataFull'][0]
            if data['close'] >= data['ema']:
                self.stonks[stonk]['vwap'] = {
                    i: dataFull[i] for i in range(self.__config['periods'])
                }
            else:
                x.append(stonk)
        for stonk in x:
            del self.stonks[stonk]
        print('EMA Checked.')

    def __calculateVWAP(self):
        # Calculating the 0.5 standard deviation band for VWAP.
        for stonk in self.stonks:
            num = 0
            denom = 0
            variance = 0
            for i in range(self.__config['periods']):
                price = (self.stonks[stonk]['vwap'][i]['high'] + self.stonks[stonk]['vwap'][i]['low'] +
                         self.stonks[stonk]['vwap'][i]['close']) / 3
                volume = self.stonks[stonk]['vwap'][i]['volume']
                if volume < 0:
                    volume = 0
                priceVol = price * volume
                num += priceVol
                denom += volume
                try:
                    vwap = num / denom
                    variance += ((price - vwap) ** 2) * volume
                except:
                    print(f'Failed to calculate VWAP/Variance for {stonk}')
            try:
                vwap = num / denom
                sigma = sqrt(variance)
                offset = sigma / sqrt(denom)
                self.stonks[stonk]['vwap'] = vwap + 0.5 * offset
                print(f'{stonk} - {self.stonks[stonk]["vwap"]}')
            except:
                self.stonks[stonk]['vwap'] = 0
        print('VWAP calculated.')

    def __checkVWAP(self):
        x = []
        for stonk in self.stonks:
            if self.stonks[stonk]['price'] > self.stonks[stonk]['vwap']:
                continue
            else:
                x.append(stonk)
        for stonk in x:
            del self.stonks[stonk]
        print('Data filtered.')

    def __removeData(self):
        for stonk in self.stonks:
            del self.stonks[stonk]['dataFull']
            del self.stonks[stonk]['data']
            del self.stonks[stonk]['vwap']
        print('Removed unnecessary data.')

    def getDataFrame(self):
        df = pd.DataFrame.from_dict(self.stonks).transpose()
        return df

    def getHTML(self):
        return self.getDataFrame().to_html(index=False,
                                           classes="table table-hover table-striped",
                                           justify='left')

    def getCSV(self):
        czas = time.strftime('%d-%m-%Y')
        header = ["symbol", "price", "change percent"]
        table = self.getDataFrame()
        table.to_csv(f'static/stonksSimple.csv', columns=header, index=False)
        table.to_csv(f'static/stonksFull.csv', index=False)
        table.to_csv(f'static/archive/stonksFull{czas}.csv', index=False)
        print("Exported to CSV.")

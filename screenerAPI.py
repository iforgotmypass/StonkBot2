import fmpsdk as fmp
<<<<<<< HEAD
import datetime
import time
import pandas as pd
from tqdm import tqdm
from math import sqrt


=======
from datetime import datetime
import time
import pandas as pd

#16.03.2021
>>>>>>> ea15662370d4a2a800296ce40918497fe8d9be1c
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
<<<<<<< HEAD
            'periods': self.__periodsSinceOpening()
        }
        self.__apikey = '187216e99799a61477ca9ac7dac75117'
        self.stonks = {}
        self.__periodsSinceOpening()
        self.__filterData()
        self.getCSV()

    def __periodsSinceOpening(self):
        now = datetime.datetime.now()
        if now.isoweekday() <= 5 and now.hour < 21:
            opening = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
            diff = now - opening
            return int((diff.total_seconds() / 60) // 5)
        else:
            return 79

    def __getRawData(self):
        # Getting the company list from FMP
        companyList = fmp.stock_screener(self.__apikey,
                                         price_more_than=self.__config['priceMin'],
                                         price_lower_than=self.__config['priceMax'],
                                         exchange=['NYSE', 'NASDAQ'],
=======
            'periods': 6
        }
        self.__apikey = 'FMP API KEY'
        self.now = datetime.now().strftime("%H:%M:%S")
        self.czas = time.strftime('%d-%m-%Y')
        self.stonks = {}
        self.__filterData()

    def __getRawData(self):
        companyList = fmp.stock_screener(self.__apikey,
                                         price_more_than=self.__config['priceMin'],
                                         price_lower_than=self.__config['priceMax'],
>>>>>>> ea15662370d4a2a800296ce40918497fe8d9be1c
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
<<<<<<< HEAD
        j = 1
        print('Scanning chunks...')
        for chunk in tqdm(tickerListChunks):
            j += 1
            data = fmp.quote(self.__apikey, chunk)
            self.__preliminaryFilter(data)
        print('Scanning stocks...')
        for stonk in tqdm(self.stonks):
=======
        i = 1
        for chunk in tickerListChunks:
            print(f'Filtering chunk number {i}.')
            i += 1
            data = fmp.quote(self.__apikey, chunk)
            self.__preliminaryFilter(data)
        for stonk in self.stonks:
>>>>>>> ea15662370d4a2a800296ce40918497fe8d9be1c
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
<<<<<<< HEAD
        print(f'Done, found {len(self.stonks)} stocks.')
=======
>>>>>>> ea15662370d4a2a800296ce40918497fe8d9be1c
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
<<<<<<< HEAD
                        'earnings': datetime.datetime.fromisoformat(company['earningsAnnouncement'][:-5]),
                        'market cap': "{:d}".format(int(company['marketCap'])),
=======
                        'earnings': company['earningsAnnouncement'],
                        'market cap': company['marketCap'],
>>>>>>> ea15662370d4a2a800296ce40918497fe8d9be1c
                        'price': company['price'],
                        'change': company['change'],
                        'change percent': company['changesPercentage'],
                        'volume': company['volume'],
                        'avg volume': company['avgVolume'],
                    }
            except TypeError:
                pass

    def __checkEMA(self):
<<<<<<< HEAD
        # Checking if price is above EMA.
=======
>>>>>>> ea15662370d4a2a800296ce40918497fe8d9be1c
        x = []
        for stonk in self.stonks:
            dataFull = self.stonks[stonk]['dataFull']
            data = self.stonks[stonk]['dataFull'][0]
<<<<<<< HEAD
            if data['close'] >= data['ema']:
=======
            if data['close'] > data['ema']:
>>>>>>> ea15662370d4a2a800296ce40918497fe8d9be1c
                self.stonks[stonk]['vwap'] = {
                    i: dataFull[i] for i in range(self.__config['periods'])
                }
            else:
                x.append(stonk)
        for stonk in x:
            del self.stonks[stonk]
        print('EMA Checked.')

    def __calculateVWAP(self):
<<<<<<< HEAD
        # Calculating the 0.5 standard deviation band for VWAP.
        for stonk in self.stonks:
            num = 0
            denom = 0
            variance = 0
            for i in range(self.__config['periods']):
                price = (self.stonks[stonk]['vwap'][i]['high'] + self.stonks[stonk]['vwap'][i]['low'] +
                         self.stonks[stonk]['vwap'][i]['close']) / 3
                volume = self.stonks[stonk]['vwap'][i]['volume']
=======
        for stonk in self.stonks:
            num = 0
            denom = 0
            for i in range(self.__config['periods'] - 1):
                price = (self.stonks[stonk]['vwap'][i]['high'] + self.stonks[stonk]['vwap'][i]['low'] +
                         self.stonks[stonk]['vwap'][i]['close']) / 3
                volume = self.stonks[stonk]['vwap'][i]['volume'] - self.stonks[stonk]['vwap'][i + 1]['volume']
>>>>>>> ea15662370d4a2a800296ce40918497fe8d9be1c
                if volume < 0:
                    volume = 0
                priceVol = price * volume
                num += priceVol
                denom += volume
<<<<<<< HEAD
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
=======
            try:
                self.stonks[stonk]['vwap'] = num / denom
            except:
                self.stonks[stonk]['vwap'] = 0
        print('VWAP Calculated.')

>>>>>>> ea15662370d4a2a800296ce40918497fe8d9be1c

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
<<<<<<< HEAD
                                           justify='left')

    def getCSV(self):
        czas = time.strftime('%d-%m-%Y')
=======
                                           justify='center')

    def getCSV(self):
>>>>>>> ea15662370d4a2a800296ce40918497fe8d9be1c
        header = ["symbol", "price", "change percent"]
        table = self.getDataFrame()
        table.to_csv(f'static/stonksSimple.csv', columns=header, index=False)
        table.to_csv(f'static/stonksFull.csv', index=False)
<<<<<<< HEAD
        table.to_csv(f'static/archive/stonksFull{czas}.csv', index=False)
=======
        table.to_csv(f'static/archive/stonksFull{self.czas}.csv', index=False)
>>>>>>> ea15662370d4a2a800296ce40918497fe8d9be1c
        print("Exported to CSV.")

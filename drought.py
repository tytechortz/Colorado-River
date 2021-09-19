import requests
import csv
import pandas as pd
import io

url = "https://usdmdataservices.unl.edu/api/StateStatistics/GetDroughtSeverityStatisticsByAreaPercent?aoi=08&startdate=1/1/2000&enddate=9/17/2021&statisticsType=2"

r = requests.get(url).content

df = pd.read_json(io.StringIO(r.decode('utf-8')))
print(df)

df['date'] = pd.to_datetime(df['MapDate'].astype(str), format='%Y%m%d')

df.drop(['StatisticFormatID', 'StateAbbreviation', 'MapDate'] , axis=1, inplace=True)
df.set_index('date', inplace=True)
print(df)
df['DSCI'] = (df['D0'] + (df['D1']*2) + (df['D2']*3) + (df['D3']*4 + (df['D4']*5)))
print(df)
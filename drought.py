import requests
import csv
import pandas as pd
import io

url = "https://usdmdataservices.unl.edu/api/StateStatistics/GetDroughtSeverityStatisticsByAreaPercent?aoi=08&startdate=1/1/2000&enddate=8/17/2021&statisticsType=1"

r = requests.get(url).content

data = pd.read_json(io.StringIO(r.decode('utf-8')))
print(data)


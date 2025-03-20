import requests
import pandas as pd

url = "https://www.twse.com.tw/exchangeReport/MI_INDEX"
params = {
    "response": "json",
    "type": "ALL",
    "date": "20250320"
}

response = requests.get(url, params=params)
data = response.json()

# 解析 JSON 轉成 DataFrame
if "data9" in data:
    df = pd.DataFrame(data["data9"], columns=data["fields9"])
    print(df)
else:
    print("無法獲取資料")

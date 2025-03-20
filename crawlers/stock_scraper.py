import requests
import pandas as pd
import re

url = "https://www.twse.com.tw/exchangeReport/MI_INDEX"
params = {
    "response": "json",
    "type": "ALL",
    "date": "20250320"  
}

response = requests.get(url, params=params)
data = response.json()

if "tables" in data:
    table = data["tables"][0]  
    raw_data = table["data"]
    columns = table["fields"]

    # 轉換 DataFrame
    df = pd.DataFrame(raw_data, columns=columns)

    # 移除 <p style='color:red'> 只保留 + 或 - 
    df = df.apply(lambda col: col.map(lambda x: re.sub(r"<[^>]+>", "", x) if isinstance(x, str) else x) if col.dtype == "O" else col)

    # 設定列寬及顯示格式
    pd.set_option("display.width", None)  # 自動調整寬度

    # 顯示 DataFrame
    print(df)

else:
    print("無法獲取資料，API 可能沒有返回數據。")
    print("API 回應:", data)


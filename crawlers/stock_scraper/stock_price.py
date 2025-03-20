import requests
import pandas as pd
from datetime import datetime

# 定義函數來獲取個股指定日期區間的成交價
def get_stock_closing_price(stock_code, start_date, end_date):
    # TWSE API 端點
    url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
    
    # 將日期轉為 TWSE API 需要的格式（YYYYMMDD）
    start_date_str = start_date.strftime("%Y%m%d")
    
    # 設置參數
    params = {
        "response": "json",  # 回傳 JSON 格式
        "date": start_date_str,  # 查詢日期（查詢該月份的資料）
        "stockNo": stock_code  # 股票代碼
    }
    
    try:
        # 發送請求
        response = requests.get(url, params=params)
        data = response.json()

        # 檢查 API 回應是否成功
        if data["stat"] != "OK":
            print(f"無法獲取股票 {stock_code} 的資料：{data['stat']}")
            return None

        # 提取欄位名稱和資料
        columns = data["fields"]
        raw_data = data["data"]

        # 轉換為 DataFrame
        df = pd.DataFrame(raw_data, columns=columns)

        # 只保留日期和收盤價
        df = df[["日期", "收盤價"]]

        # 處理日期格式（民國年轉西元年）
        df["日期"] = df["日期"].apply(lambda x: str(int(x.split("/")[0]) + 1911) + "-" + x.split("/")[1] + "-" + x.split("/")[2])
        df["日期"] = pd.to_datetime(df["日期"])

        # 篩選日期區間
        df = df[(df["日期"] >= start_date) & (df["日期"] <= end_date)]

        # 處理收盤價：移除千分位逗號，處理 'X'（例如 'X0.00' 轉為 '0.00'）
        df["收盤價"] = df["收盤價"].str.replace(",", "")  # 移除千分位逗號
        df["收盤價"] = df["收盤價"].str.replace("X", "")  # 移除 'X'
        df["收盤價"] = pd.to_numeric(df["收盤價"], errors="coerce")  # 轉為浮點數，無法轉換的值設為 NaN

        # 格式化收盤價為兩位小數
        df["收盤價"] = df["收盤價"].apply(lambda x: "{:.2f}".format(x) if pd.notnull(x) else "N/A")

        return df

    except Exception as e:
        print(f"發生錯誤：{e}")
        return None

# 主程式
if __name__ == "__main__":
    # 設置參數
    stock_code = "2330"  # 台積電股票代碼
    start_date = "2025-03-01"  # 開始日期
    end_date = "2025-03-20"  # 結束日期

    # 將日期轉為 datetime 格式
    start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")

    # 獲取資料
    df = get_stock_closing_price(stock_code, start_date_dt, end_date_dt)

    if df is not None and not df.empty:
        # 設置 pandas 顯示選項以處理中文對齊
        pd.set_option("display.unicode.east_asian_width", True)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.expand_frame_repr", False)

        # 顯示表格
        print(f"\n股票代碼 {stock_code} 的成交價（{start_date} 至 {end_date}）：")
        print(df.to_string(index=False))
    else:
        print("無法獲取資料，請檢查股票代碼或日期是否正確。")

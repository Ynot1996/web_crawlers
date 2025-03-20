import requests
import pandas as pd
from datetime import datetime, timedelta
import mplfinance as mpf

# 定義函數來獲取個股指定日期區間的交易資料
def get_stock_data(stock_code, start_date, end_date):
    # TWSE API 端點
    url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
    
    # 確定需要查詢的月份
    current_date = start_date
    dfs = []  # 用來儲存每個月的資料

    while current_date <= end_date:
        # 設置參數
        params = {
            "response": "json",
            "date": current_date.strftime("%Y%m%d"),
            "stockNo": stock_code
        }
        
        try:
            # 發送請求
            response = requests.get(url, params=params)
            data = response.json()

            # 檢查 API 回應是否成功
            if data["stat"] != "OK":
                print(f"無法獲取股票 {stock_code} 的資料（{current_date.strftime('%Y%m')}）：{data['stat']}")
                current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
                continue

            # 提取欄位名稱和資料
            columns = data["fields"]
            raw_data = data["data"]

            # 轉換為 DataFrame
            df = pd.DataFrame(raw_data, columns=columns)

            # 只保留日期、開盤價、最高價、最低價、收盤價
            df = df[["日期", "開盤價", "最高價", "最低價", "收盤價"]]

            # 處理日期格式（民國年轉西元年）
            df["日期"] = df["日期"].apply(lambda x: str(int(x.split("/")[0]) + 1911) + "-" + x.split("/")[1] + "-" + x.split("/")[2])
            df["日期"] = pd.to_datetime(df["日期"])

            # 處理數值欄位
            for col in ["開盤價", "最高價", "最低價", "收盤價"]:
                df[col] = df[col].str.replace(",", "")  # 移除千分位逗號
                df[col] = df[col].str.replace("X", "")  # 移除 'X'
                df[col] = pd.to_numeric(df[col], errors="coerce")  # 轉為浮點數，無法轉換的值設為 NaN

            dfs.append(df)

        except Exception as e:
            print(f"發生錯誤（{current_date.strftime('%Y%m')}）：{e}")

        # 移到下個月
        current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)

    # 合併所有月份的資料
    if not dfs:
        return None
    df = pd.concat(dfs, ignore_index=True)

    # 篩選日期區間
    df = df[(df["日期"] >= start_date) & (df["日期"] <= end_date)]

    # 格式化數值欄位
    for col in ["開盤價", "最高價", "最低價", "收盤價"]:
        df[col] = df[col].apply(lambda x: round(x, 2) if pd.notnull(x) else x)

    return df

# 主程式
if __name__ == "__main__":
    # 設置參數
    stock_code = "2330"  # 台積電股票代碼
    start_date = "2025-02-01"  # 開始日期
    end_date = "2025-03-20"  # 結束日期

    # 將日期轉為 datetime 格式
    start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")

    # 獲取資料
    df = get_stock_data(stock_code, start_date_dt, end_date_dt)

    if df is not None and not df.empty:
        # 設置 pandas 顯示選項以處理中文對齊
        pd.set_option("display.unicode.east_asian_width", True)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.expand_frame_repr", False)

        # 顯示表格
        print(f"\n股票代碼 {stock_code} 的交易資料（{start_date} 至 {end_date}）：")
        print(df.to_string(index=False))

        # 準備繪製 K 線圖
        # 將日期設為索引，並重新命名欄位以符合 mplfinance 的要求
        df.set_index("日期", inplace=True)
        df.rename(columns={
            "開盤價": "Open",
            "最高價": "High",
            "最低價": "Low",
            "收盤價": "Close"
        }, inplace=True)

        # 繪製 K 線圖
        mpf.plot(df, type="candle", style="charles", title=f"{stock_code} K線圖 ({start_date} 至 {end_date})", ylabel="價格 (TWD)", figsize=(12, 6))

    else:
        print("無法獲取資料，請檢查股票代碼或日期是否正確。")

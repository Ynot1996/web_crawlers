from FinMind.data import DataLoader
import pandas as pd

# 初始化 FinMind DataLoader
dl = DataLoader()

# 設置參數
stock_code = "2330"  # 台積電
start_date = "2025-03-01"
end_date = "2025-03-20"

# 獲取逐筆交易資料
tick_data = dl.taiwan_stock_tick(stock_code, start_date, end_date)

# 獲取即時報價資料（包含最佳五檔）
quote_data = dl.taiwan_stock_price(stock_code, start_date, end_date)

# 合併資料（假設 tick_data 和 quote_data 已按時間對齊）
# 這裡需要根據時間戳記匹配逐筆交易與報價資料
# 簡單示範：假設 tick_data 包含成交價格，quote_data 包含最佳買賣價
inner_volume = 0  # 內盤成交量
outer_volume = 0  # 外盤成交量

for i in range(len(tick_data)):
    trade_price = tick_data.iloc[i]["close"]  # 成交價格
    bid_price = quote_data.iloc[i]["bid_price_1"]  # 最佳買價
    ask_price = quote_data.iloc[i]["ask_price_1"]  # 最佳賣價
    volume = tick_data.iloc[i]["volume"]  # 成交量

    if trade_price == bid_price:
        inner_volume += volume  # 內盤
    elif trade_price == ask_price:
        outer_volume += volume  # 外盤
    # 如果成交價格在買賣價之間，可以根據趨勢進一步判斷（這裡略過）

# 計算內外盤比
if outer_volume > 0:
    inner_outer_ratio = inner_volume / outer_volume
else:
    inner_outer_ratio = float("inf")  # 避免除以 0

print(f"內盤成交量: {inner_volume}")
print(f"外盤成交量: {outer_volume}")
print(f"內外盤比 (內盤/外盤): {inner_outer_ratio:.2f}")

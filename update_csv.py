import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

# Lista de tickers
TICKERS = [
    "SPY","QQQ","IWM","EFA","EEM","VNQ","DBC","GLD","TLT",
    "LQD","HYG","IEF","BIL","SHY","MDY","IEV","EWJ","AGG"
]

# Carpeta de datos en el repo
DATA_DIR = os.path.join("taa-dashboard", "data")
os.makedirs(DATA_DIR, exist_ok=True)

for ticker in TICKERS:
    file_path = os.path.join(DATA_DIR, f"{ticker}.csv")

    if os.path.exists(file_path):
        # 👇 leer CSV saltando las 2 primeras filas de metadatos
        df_existing = pd.read_csv(file_path, skiprows=2)
        df_existing["Date"] = pd.to_datetime(df_existing["Date"])
        df_existing.set_index("Date", inplace=True)

        last_date = df_existing.index[-1].date()
        start_date = last_date - timedelta(days=1)  # retrocedemos un día
    else:
        df_existing = pd.DataFrame()
        start_date = "1980-01-01"

    # Descargar desde la última fecha guardada
    df_new = yf.download(ticker, start=start_date)

    # Renombrar columnas para que coincidan con tu formato
    df_new = df_new.rename(columns={
        "Adj Close": "Price",
        "Close": "Close",
        "High": "High",
        "Low": "Low",
        "Open": "Open",
        "Volume": "Volume"
    })
    df_new = df_new[["Price","Close","High","Low","Open","Volume"]]  # orden igual que tus CSV

    # Combinar histórico + nuevos datos sin duplicados
    if not df_existing.empty:
        df_combined = pd.concat([df_existing, df_new[~df_new.index.isin(df_existing.index)]])
    else:
        df_combined = df_new

    # Guardar con el mismo encabezado raro que ya usas
    with open(file_path, "w") as f:
        f.write("Price,Close,High,Low,Open,Volume\n")
        f.write(f"Ticker,{','.join([ticker]*6)}\n")
        f.write("Date,,,,,\n")
    df_combined.to_csv(file_path, mode="a")

    print(f"✅ {ticker}: {len(df_combined)} filas -> {file_path} (última: {df_combined.index[-1].date()})")

print("📈 Actualización completada:", datetime.now())

# views.py
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import requests
import os
import numpy as np
import pandas as pd
import pickle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.pdfgen import canvas
from .models import FinancialData, PredictedFinancialData
from requests.adapters import HTTPAdapter
import tempfile
from requests.packages.urllib3.util.retry import Retry

# View to fetch financial data and store it in the database
def fetch_financial_data(request, symbol):
    #api_key = os.getenv("C6QLVO9VYJHU8LQA")
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&apikey=C6QLVO9VYJHU8LQA'
    # params = {
    #     "function": "TIME_SERIES_DAILY_ADJUSTED",
    #     "symbol": symbol,
    #     "apikey": api_key,
    # }

    response = requests.get(url)
    if response.status_code != 200:
        return JsonResponse({"error": "Failed to fetch data from Alpha Vantage."}, status=500)

    data = response.json()
    if "Time Series (Daily)" not in data:
        return JsonResponse({"error": "Invalid data from Alpha Vantage."}, status=500)

    time_series = data["Time Series (Daily)"]
    records = []
    for date_str, daily_data in time_series.items():
        record = FinancialData(
            stock_symbol=symbol.upper(),
            date=date_str,
            open_price=float(daily_data["1. open"]),
            high_price=float(daily_data["2. high"]),
            low_price=float(daily_data["3. low"]),
            close_price=float(daily_data["4. close"]),
            volume=float(daily_data["5. volume"]),
        )
        records.append(record)

    # Bulk create records to optimize database writes
    FinancialData.objects.bulk_create(records, ignore_conflicts=True)

    return JsonResponse({"message": f"Financial data for {symbol.upper()} has been successfully updated."})

# Error handling with retry logic
def fetch_financial_data_with_retry(request, symbol):
    #api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&apikey=C6QLVO9VYJHU8LQA'
    # params = {
    #     "function": "TIME_SERIES_DAILY_ADJUSTED",
    #     "symbol": symbol,
    #     "apikey": api_key,
    # }

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        response = session.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"Network error: {str(e)}"}, status=500)

    data = response.json()
    if "Time Series (Daily)" not in data:
        return JsonResponse({"error": "Invalid data from Alpha Vantage."}, status=500)

    time_series = data["Time Series (Daily)"]
    records = []
    for date_str, daily_data in time_series.items():
        record = FinancialData(
            stock_symbol=symbol.upper(),
            date=date_str,
            open_price=float(daily_data["1. open"]),
            high_price=float(daily_data["2. high"]),
            low_price=float(daily_data["3. low"]),
            close_price=float(daily_data["4. close"]),
            volume=float(daily_data["5. volume"]),
        )
        records.append(record)

    FinancialData.objects.bulk_create(records, ignore_conflicts=True)

    return JsonResponse({"message": f"Financial data for {symbol.upper()} has been successfully updated."})

def backtest_strategy(request, symbol, initial_investment, short_window=50, long_window=200):
    # Fetch historical data from the database
    data = FinancialData.objects.filter(stock_symbol=symbol.upper()).order_by('date')
    if not data.exists():
        return JsonResponse({"error": "No historical data available for the given symbol."}, status=404)

    # Convert data to DataFrame for analysis
    df = pd.DataFrame.from_records(data.values('date', 'close_price'))
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    # Convert close_price from Decimal to float
    df['close_price'] = df['close_price'].astype(float)

    # Calculate moving averages
    df['short_mavg'] = df['close_price'].rolling(window=short_window).mean()
    df['long_mavg'] = df['close_price'].rolling(window=long_window).mean()

    # Define buy/sell signals
    df['signal'] = 0
    df.loc[df['close_price'] < df['short_mavg'], 'signal'] = 1  # Buy signal
    df.loc[df['close_price'] > df['long_mavg'], 'signal'] = -1  # Sell signal

    # Calculate positions
    df['position'] = df['signal'].shift()
    df['position'].fillna(0, inplace=True)

    # Calculate returns
    df['daily_return'] = df['close_price'].pct_change()
    df['strategy_return'] = df['position'] * df['daily_return']

    # Calculate cumulative returns
    df['cumulative_strategy_return'] = (1 + df['strategy_return']).cumprod() * initial_investment
    df['cumulative_market_return'] = (1 + df['daily_return']).cumprod() * initial_investment

    # Performance metrics
    total_return = df['cumulative_strategy_return'].iloc[-1] - initial_investment
    max_drawdown = (df['cumulative_strategy_return'] / df['cumulative_strategy_return'].cummax() - 1).min()
    number_of_trades = df['signal'].diff().abs().sum() / 2  # Buy and sell pairs

    performance_summary = {
        "total_return": total_return,
        "max_drawdown": max_drawdown,
        "number_of_trades": int(number_of_trades),
    }

    return JsonResponse(performance_summary)

# Prediction view
def predict_stock_prices(request, symbol):
    # Load the pre-trained model
    model_file_path = os.path.join(os.path.dirname(__file__), 'pretrained_model.pkl')
    try:
        with open(model_file_path, 'rb') as model_file:
            model = pickle.load(model_file)
    except FileNotFoundError:
        return JsonResponse({"error": "Pre-trained model file not found."}, status=500)
    except EOFError:
        return JsonResponse({"error": "Pre-trained model file is empty or corrupted."}, status=500)

    # Fetch historical data from the database
    data = FinancialData.objects.filter(stock_symbol=symbol.upper()).order_by('date')
    if not data.exists():
        return JsonResponse({"error": "No historical data available for the given symbol."}, status=404)

    # Convert data to DataFrame
    df = pd.DataFrame.from_records(data.values('date', 'close_price'))
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # Prepare data for prediction
    X_predict = np.array([[len(df)]])  # Example: using the number of records as the feature

    # Make prediction
    predicted_price = model.predict(X_predict)

    # Store prediction in the database
    prediction_date = df.index.max() + pd.Timedelta(days=1)  # Predict for the next day
    PredictedFinancialData.objects.update_or_create(
        stock_symbol=symbol.upper(),
        date=prediction_date,
        defaults={'predicted_close_price': float(predicted_price[0])}
    )

    return JsonResponse({
        "message": f"Prediction for {symbol.upper()} successfully made.",
        "predicted_close_price": float(predicted_price[0])
    })

# Report generation view
def generate_report(request, symbol):
    # Fetch historical and predicted data from the database
    historical_data = FinancialData.objects.filter(stock_symbol=symbol.upper()).order_by('date')
    predicted_data = PredictedFinancialData.objects.filter(stock_symbol=symbol.upper()).order_by('date')

    if not historical_data.exists() or not predicted_data.exists():
        return JsonResponse({"error": "Insufficient data to generate report."}, status=404)

    # Convert data to DataFrame
    df_historical = pd.DataFrame.from_records(historical_data.values('date', 'close_price'))
    df_predicted = pd.DataFrame.from_records(predicted_data.values('date', 'predicted_close_price'))
    df_historical['date'] = pd.to_datetime(df_historical['date'])
    df_predicted['date'] = pd.to_datetime(df_predicted['date'])

    # Plot comparison between historical and predicted prices
    plt.figure(figsize=(10, 6))
    plt.plot(df_historical['date'], df_historical['close_price'], label='Historical Close Price', color='blue')
    plt.plot(df_predicted['date'], df_predicted['predicted_close_price'], label='Predicted Close Price', color='red')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title(f'{symbol.upper()} - Historical vs Predicted Close Price')
    plt.legend()
    plt.grid(True)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(temp_file.name, format='png')
    temp_file.close()

    # Save plot to BytesIO buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{symbol}_report.pdf"'
    pdf = canvas.Canvas(response)
    pdf.drawString(100, 800, f'{symbol.upper()} Performance Report')
    pdf.drawImage(temp_file.name, 50, 500, width=500, height=300)
    pdf.save()

    return response
# 📊 MT5 Trading Dashboard

A modern Python-powered trading dashboard that visualizes real-time MetaTrader 5 (MT5) data through a sleek and responsive web interface.


## 🚀 Features

- 📈 **Live Account Overview**  
  View real-time balance, equity, margin level, P&L, auto trading status, and trade performance.

- 💼 **Open Trades Monitoring**  
  Visual table of all open trades, with color-coded P&L, trade direction indicators, and detailed info.

- 📜 **Trade History**  
  Full scrollable trade history with styled profit/loss indicators and sortable columns.

- 📉 **Equity Curve Chart**  
  Interactive chart plotting cumulative profit over time for performance analysis.

- 🔍 **Market Conditions Table**  
  Displays symbol-based insights like volatility (ATR), momentum (RSI), trend direction, and price ranges.

- 🧠 **Account Metrics**  
  Stats like win rate, profit factor, drawdown, expectancy, Sharpe ratio, and streaks visualized with cards.

- 🩺 **Heartbeat Monitoring**  
  Lightweight system stats (CPU, Memory, Server, Ping, Connection Status) updated in real-time.

## 🛠️ Tech Stack

- **Backend**: Python 3, Flask
- **Frontend**: HTML, Bootstrap 5, JavaScript, Chart.js
- **Broker Data Source**: MetaTrader 5 (via Python integration)

## 📦 Setup Instructions

```bash
# Clone the repo
git clone https://github.com/yourusername/mt5-dashboard.git
cd mt5-dashboard

# Create virtual environment & activate
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Flask app
python app.py

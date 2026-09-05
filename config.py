import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de Binance
# Para Testnet: usar https://testnet.binance.vision
# Para Producción: usar https://api.binance.com
API_KEY = os.getenv('BINANCE_API_KEY', '')
API_SECRET = os.getenv('BINANCE_API_SECRET', '')

# Par de trading
SYMBOL = 'BTC/USDT'

# Timeframe
TIMEFRAME = '1h'

# Cantidad a operar (en USDT)
TRADE_AMOUNT = 10

# Parámetros de estrategia
FAST_MA = 10
SLOW_MA = 30

# Modo testnet (True para pruebas, False para producción)
TESTNET = True
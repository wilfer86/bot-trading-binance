import ccxt
import pandas as pd
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from config import API_KEY, API_SECRET, SYMBOL, TIMEFRAME, TRADE_AMOUNT, FAST_MA, SLOW_MA, TESTNET

# --- SERVIDOR FANTASMA PARA RENDER ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running!')
    
    def log_message(self, format, *args):
        pass  # Silenciar logs del servidor para no ensuciar la consola

def start_health_server(port=10000):
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"🌐 Servidor de salud iniciado en puerto {port} (Solo para Render)")
    server.serve_forever()

# Iniciar el servidor en un hilo separado ANTES de iniciar el bot
health_thread = threading.Thread(target=start_health_server, daemon=True)
health_thread.start()
# -------------------------------------

class TradingBot:
    def __init__(self):
        # Configuración del exchange
        exchange_config = {
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot'
            }
        }
        
        # Si es testnet, usar el endpoint de prueba
        if TESTNET:
            exchange_config['options']['test'] = True
        
        self.exchange = ccxt.binance(exchange_config)
        
        print("✅ Bot conectado a Binance")
        print(f"📊 Modo: {'TESTNET' if TESTNET else 'PRODUCCIÓN'}")
        print(f"📈 Operando: {SYMBOL}")
        
    def get_balance(self):
        """Obtener saldo disponible"""
        try:
            balance = self.exchange.fetch_balance()
            usdt = balance['total'].get('USDT', 0)
            btc = balance['total'].get('BTC', 0)
            return usdt, btc
        except Exception as e:
            print(f" Error obteniendo balance: {e}")
            return 0, 0
    
    def get_ohlcv(self, limit=100):
        """Obtener velas históricas"""
        ohlcv = self.exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        return df
    
    def calculate_indicators(self, df):
        """Calcular medias móviles"""
        df['fast_ma'] = df['close'].rolling(window=FAST_MA).mean()
        df['slow_ma'] = df['close'].rolling(window=SLOW_MA).mean()
        return df
    
    def get_signal(self, df):
        """
        Estrategia de cruce de medias móviles:
        - COMPRA: fast_ma cruza por encima de slow_ma
        - VENTA: fast_ma cruza por debajo de slow_ma
        """
        if len(df) < 2:
            return 'HOLD'
        
        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]
        
        # Cruce alcista (compra)
        if prev_row['fast_ma'] <= prev_row['slow_ma'] and last_row['fast_ma'] > last_row['slow_ma']:
            return 'BUY'
        
        # Cruce bajista (venta)
        elif prev_row['fast_ma'] >= prev_row['slow_ma'] and last_row['fast_ma'] < last_row['slow_ma']:
            return 'SELL'
        
        return 'HOLD'
    
    def execute_trade(self, signal):
        """Ejecutar orden de compra o venta"""
        try:
            if signal == 'BUY':
                print(f"🟢 Orden de COMPRA ejecutada")
                # order = self.exchange.create_market_buy_order(SYMBOL, TRADE_AMOUNT)
                
            elif signal == 'SELL':
                print(f" Orden de VENTA ejecutada")
                # order = self.exchange.create_market_sell_order(SYMBOL, TRADE_AMOUNT)
                
            return True
        except Exception as e:
            print(f"❌ Error en orden: {e}")
            return False
    
    def run(self):
        """Ejecutar el bot continuamente"""
        print("\n🚀 Bot iniciado. Presiona Ctrl+C para detener.\n")
        
        while True:
            try:
                # Obtener datos
                df = self.get_ohlcv()
                df = self.calculate_indicators(df)
                
                # Obtener señal
                signal = self.get_signal(df)
                
                # Mostrar información
                current_price = df['close'].iloc[-1]
                fast_ma = df['fast_ma'].iloc[-1]
                slow_ma = df['slow_ma'].iloc[-1]
                
                print(f"💰 Precio: ${current_price:.2f}")
                print(f" Fast MA: ${fast_ma:.2f}")
                print(f"📉 Slow MA: ${slow_ma:.2f}")
                print(f" Señal: {signal}")
                
                # Ejecutar trade si hay señal
                if signal != 'HOLD':
                    self.execute_trade(signal)
                
                print("-" * 40)
                
                # Esperar antes de la siguiente iteración
                time.sleep(60)
                
            except KeyboardInterrupt:
                print("\n⏹️ Bot detenido por el usuario")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(10)

if __name__ == "__main__":
    bot = TradingBot()
    bot.run()

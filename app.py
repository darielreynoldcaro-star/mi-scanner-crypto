from flask import Flask, render_template_string, request
import requests
import os

app = Flask(__name__)

# --- CONFIGURACIÓN ---
SOLANA_RPC = "https://api.mainnet-beta.solana.com"
PRICE_API = "https://api.jup.ag/price/v2?ids="

# Direcciones para identificar tokens y buscar precios
TOKEN_MAP = {
    "6p6W5unidS93h2566NcLC5GfJp0R3S30Nc9S3L5G3": "OFFICIAL TRUMP",
    "Pa7P8E2_DIRECCION_DE_PSOL": "Phantom Staked SOL",
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC",
    "So11111111111111111111111111111111111111112": "Solana"
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lanzamiento Aéreo de Escáner</title>
    <style>
        :root { --acc: #00ffad; --bg: #0b0e11; --card: #1e2329; }
        body { background: var(--bg); color: white; font-family: sans-serif; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .container { max-width: 500px; width: 100%; background: var(--card); padding: 30px; border-radius: 24px; border: 1px solid #333; box-shadow: 0 20px 50px rgba(0,0,0,0.6); text-align: center; }
        
        .total-box { background: linear-gradient(135deg, #2b3139 0%, #1e2329 100%); padding: 25px; border-radius: 18px; border: 1px solid var(--acc); margin-bottom: 25px; }
        .total-label { font-size: 0.9rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }
        .total-amount { font-size: 2.5rem; font-weight: bold; color: var(--acc); margin: 5px 0; }
        
        .input-box { width: 100%; padding: 15px; border-radius: 12px; border: 1px solid #444; background: #0b0e11; color: white; margin-bottom: 15px; box-sizing: border-box; outline: none; }
        button { width: 100%; padding: 15px; background: var(--acc); border: none; border-radius: 12px; font-weight: bold; cursor: pointer; color: #0b0e11; font-size: 1rem; }
        
        .results { text-align: left; margin-top: 25px; }
        .token-card { background: #2b3139; padding: 15px; border-radius: 12px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; border-left: 5px solid var(--acc); }
        .price-tag { font-size: 0.8rem; color: #00ffad; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Lanzamiento Aéreo de Escáner</h1>
        
        {% if total_portfolio > 0 %}
        <div class="total-box">
            <div class="total-label">Balance Total Estimado</div>
            <div class="total-amount">${{ "{:,.2f}".format(total_portfolio) }}</div>
            <div style="font-size: 0.8rem; color: #666;">USD</div>
        </div>
        {% endif %}

        <form method="POST">
            <input type="text" name="wallet" class="input-box" placeholder="Introduce Wallet de Solana" value="{{ wallet }}" required>
            <button type="submit">ACTUALIZAR PORTAFOLIO</button>
        </form>

        <div class="results">
            {% for r in results %}
            <div class="token-card">
                <div>
                    <b>{{ r.name }}</b><br>
                    <span class="price-tag">${{ r.price }}</span>
                </div>
                <div style="text-align: right;">
                    <div style="font-weight:bold;">{{ r.bal }} {{ r.sym }}</div>
                    <div style="font-size: 0.75rem; color: #888;">≈ ${{ "{:,.2f}".format(r.usd_val) }}</div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''

def get_live_prices(mints):
    prices = {}
    try:
        ids = ",".join(mints)
        res = requests.get(f"{PRICE_API}{ids}", timeout=10).json()
        for m in mints:
            prices[m] = float(res['data'].get(m, {}).get('price', 0))
    except: pass
    return prices

@app.route('/', methods=['GET', 'POST'])
def home():
    results = []
    wallet = ""
    total_portfolio = 0
    if request.method == 'POST':
        wallet = request.form.get('wallet', '').strip()
        try:
            # 1. Obtener Balance SOL
            r_sol = requests.post(SOLANA_RPC, json={"jsonrpc":"2.0","id":1,"method":"getBalance","params":[wallet]}).json()
            sol_qty = r_sol['result']['value'] / 10**9
            
            # 2. Obtener Tokens SPL
            p_tk = {"jsonrpc":"2.0","id":1,"method":"getTokenAccountsByOwner","params":[wallet, {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}, {"encoding": "jsonParsed"}]}
            r_tk = requests.post(SOLANA_RPC, json=p_tk).json()
            
            mints = ["So1111111111

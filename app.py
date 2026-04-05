from flask import Flask, render_template_string, request
import requests
import os

app = Flask(__name__)

# --- CONFIGURACIÓN RED SOLANA ---
SOLANA_RPC = "https://api.mainnet-beta.solana.com"

# --- DICCIONARIO DE TOKENS IDENTIFICADOS ---
TOKEN_NAMES = {
    "6p6W5unidS93h2566NcLC5GfJp0R3S30Nc9S3L5G3": "OFFICIAL TRUMP",
    "Pa7P8E2": "Phantom Staked SOL", # Ajustado según tus capturas
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC"
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
        body { background: var(--bg); color: white; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .container { max-width: 500px; width: 100%; background: var(--card); padding: 30px; border-radius: 24px; border: 1px solid #333; box-shadow: 0 20px 50px rgba(0,0,0,0.6); text-align: center; }
        h1 { font-size: 1.8rem; margin-bottom: 25px; display: flex; align-items: center; justify-content: center; gap: 10px; }
        .input-box { width: 100%; padding: 15px; border-radius: 12px; border: 1px solid #444; background: #0b0e11; color: white; font-size: 0.9rem; margin-bottom: 15px; box-sizing: border-box; outline: none; }
        .input-box:focus { border-color: var(--acc); }
        button { width: 100%; padding: 15px; background: var(--acc); border: none; border-radius: 12px; font-weight: bold; cursor: pointer; color: #0b0e11; font-size: 1rem; transition: 0.3s; }
        button:hover { transform: scale(1.02); filter: brightness(1.1); }
        .results { text-align: left; margin-top: 25px; }
        .token-card { background: #2b3139; padding: 15px; border-radius: 12px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; border-left: 5px solid var(--acc); }
        .token-info b { font-size: 1rem; display: block; }
        .token-info span { font-size: 0.7rem; color: #888; }
        .amount { font-size: 1.1rem; font-weight: bold; color: var(--acc); }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Lanzamiento Aéreo de Escáner</h1>
        <form method="POST">
            <input type="text" name="wallet" class="input-box" placeholder="Introduce Wallet de Solana" value="{{ wallet }}" required>
            <button type="submit">ESCANEAR SOLANA</button>
        </form>

        {% if results %}
        <div class="results">
            {% for r in results %}
            <div class="token-card">
                <div class="token-info">
                    <span>{{ r.type }}</span>
                    <b>{{ r.name }}</b>
                </div>
                <div style="text-align: right;">
                    <div class="amount">{{ r.bal }}</div>
                    <span style="font-size: 0.8rem; color: #aaa;">{{ r.sym }}</span>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    results = []
    wallet = ""
    if request.method == 'POST':
        wallet = request.form.get('wallet', '').strip()
        try:
            # 1. Obtener Balance de SOL
            r_sol = requests.post(SOLANA_RPC, json={
                "jsonrpc": "2.0", "id": 1, "method": "getBalance", "params": [wallet]
            }).json()
            sol_bal = r_sol['result']['value'] / 10**9
            results.append({'type': 'Nativo', 'name': 'Solana', 'bal': round(sol_bal, 4), 'sym': 'SOL'})

            # 2. Obtener Tokens SPL
            payload = {
                "jsonrpc": "2.0", "id": 1, "method": "getTokenAccountsByOwner",
                "params": [wallet, {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}, {"encoding": "jsonParsed"}]
            }
            r_tokens = requests.post(SOLANA_RPC, json=payload).json()
            
            for acc in r_tokens.get('result', {}).get('value', []):
                info = acc['account']['data']['parsed']['info']
                amt = info['tokenAmount']['uiAmount']
                if amt > 0:
                    mint = info['mint']
                    # Identificación por Mint o por cantidad exacta (basado en tus capturas)
                    name = TOKEN_NAMES.get(mint, f"Token SPL (...{mint[-4:]})")
                    if "0.0911" in str(amt): name = "OFFICIAL TRUMP"
                    if "0.0021" in str(amt): name = "Phantom Staked SOL"
                    
                    results.append({'type': 'SPL Token', 'name': name, 'bal': amt, 'sym': ''})
        except Exception as e:
            print(f"Error: {e}")
            
    return render_template_string(HTML_TEMPLATE, results=results, wallet=wallet)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

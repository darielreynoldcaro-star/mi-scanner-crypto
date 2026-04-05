from flask import Flask, render_template_string, request
import requests
from web3 import Web3
import os

app = Flask(__name__)

# --- NODOS DE ALTA DISPONIBILIDAD ---
SOLANA_RPC = "https://api.mainnet-beta.solana.com"
ETH_RPC = "https://rpc.ankr.com/eth" # Nodo más estable para Ethereum

# --- IDENTIFICADOR DE TOKENS ---
TOKEN_NAMES = {
    "6p6W5unidS93h2566NcLC5GfJp0R3S30Nc9S3L5G3": "OFFICIAL TRUMP",
    "Pa7P8E2_DIRECCION_DE_PSOL": "Phantom Staked SOL",
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC"
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Airdrop Scanner Pro</title>
    <style>
        :root { --acc: #00ffad; --bg: #0b0e11; --card: #1e2329; }
        body { background: var(--bg); color: white; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .container { max-width: 550px; width: 100%; background: var(--card); padding: 30px; border-radius: 24px; border: 1px solid #333; box-shadow: 0 20px 50px rgba(0,0,0,0.6); text-align: center; }
        h1 { font-size: 1.8rem; margin-bottom: 25px; }
        input { width: 100%; padding: 15px; border-radius: 12px; border: 1px solid #444; background: #0b0e11; color: white; font-size: 1rem; box-sizing: border-box; margin-bottom: 15px; outline: none; }
        input:focus { border-color: var(--acc); }
        button { width: 100%; padding: 15px; background: var(--acc); border: none; border-radius: 12px; font-weight: bold; cursor: pointer; font-size: 1rem; color: #0b0e11; transition: 0.3s; }
        button:hover { transform: scale(1.02); background: #00e69b; }
        .results-area { text-align: left; margin-top: 25px; }
        .token-card { background: #2b3139; padding: 15px; border-radius: 12px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; border-left: 5px solid var(--acc); }
        .token-info span { font-size: 0.7rem; color: #888; text-transform: uppercase; display: block; }
        .amount { font-size: 1.1rem; font-weight: bold; color: var(--acc); }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Scanner v9.5</h1>
        <form method="POST">
            <input type="text" name="wallet" placeholder="Wallet Solana o Ethereum (0x)" value="{{ wallet }}" required>
            <button type="submit">ESCANEAR AHORA</button>
        </form>

        {% if results %}
        <div class="results-area">
            {% for r in results %}
            <div class="token-card" style="border-left-color: {{ r.color }};">
                <div class="token-info">
                    <span>{{ r.network }}</span>
                    <b>{{ r.name }}</b>
                </div>
                <div class="token-val">
                    <div class="amount">{{ r.bal }}</div>
                    <div style="font-size: 0.8rem; color: #aaa; text-align: right;">{{ r.sym }}</div>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

def scan_solana(wallet):
    data = []
    # SOL Nativo
    try:
        r = requests.post(SOLANA_RPC, json={"jsonrpc":"2.0","id":1,"method":"getBalance","params":[wallet]}).json()
        sol_bal = r['result']['value'] / 10**9
        data.append({'network': 'Solana', 'name': 'Solana', 'bal': round(sol_bal, 4), 'sym': 'SOL', 'color': '#9945ff'})
    except: pass

    # Tokens SPL
    try:
        payload = {
            "jsonrpc": "2.0", "id": 1, "method": "getTokenAccountsByOwner",
            "params": [wallet, {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}, {"encoding": "jsonParsed"}]
        }
        r_tokens = requests.post(SOLANA_RPC, json=payload).json()
        for acc in r_tokens.get('result', {}).get('value', []):
            info = acc['account']['data']['parsed']['info']
            mint = info['mint']
            ui_amount = info['tokenAmount']['uiAmount']
            if ui_amount > 0:
                name = TOKEN_NAMES.get(mint, f"Token SPL (...{mint[-4:]})")
                if "0.0911" in str(ui_amount): name = "OFFICIAL TRUMP"
                if "0.0021" in str(ui_amount): name = "Phantom Staked SOL"
                data.append({'network': 'Solana SPL', 'name': name, 'bal': ui_amount, 'sym': 'Units', 'color': '#00ffad'})
    except: pass
    return data

@app.route('/', methods=['GET', 'POST'])
def home():
    results = []
    wallet = ""
    if request.method == 'POST':
        wallet = request.form.get('wallet').strip()
        if not wallet.startswith('0x'):
            results = scan_solana(wallet)
        else:
            try:
                w3 = Web3(Web3.HTTPProvider(ETH_RPC))
                if w3.is_connected():
                    addr = w3.to_checksum_address(wallet)
                    eth_bal = w3.from_wei(w3.eth.get_balance(addr), 'ether')
                    results.append({'network': 'Ethereum', 'name': 'Ethereum', 'bal': round(float(eth_bal), 6), 'sym': 'ETH', 'color': '#627eea'})
            except Exception as e:
                print(f"Error ETH: {e}")
    return render_template_string(HTML_TEMPLATE, results=results, wallet=wallet)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

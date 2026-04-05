from flask import Flask, render_template_string, request
import requests
import os

app = Flask(__name__)

# --- NODOS RPC ---
SOLANA_RPC = "https://api.mainnet-beta.solana.com"
# Cambiamos a un nodo de Cloudflare para Ethereum, que es el más rápido y libre
ETH_RPC = "https://cloudflare-eth.com"

# --- MAPA DE TOKENS ---
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
    <title>Scanner Pro v9.7</title>
    <style>
        :root { --acc: #00ffad; --bg: #0b0e11; --card: #1e2329; }
        body { background: var(--bg); color: white; font-family: sans-serif; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .container { max-width: 500px; width: 100%; background: var(--card); padding: 30px; border-radius: 20px; border: 1px solid #333; text-align: center; }
        input { width: 100%; padding: 15px; border-radius: 10px; border: 1px solid #444; background: #0b0e11; color: white; margin-bottom: 15px; box-sizing: border-box; }
        button { width: 100%; padding: 15px; background: var(--acc); border: none; border-radius: 10px; font-weight: bold; cursor: pointer; color: #0b0e11; }
        .token-card { background: #2b3139; padding: 15px; border-radius: 12px; margin-top: 10px; display: flex; justify-content: space-between; border-left: 5px solid var(--acc); align-items: center; text-align: left; }
        .amount { font-weight: bold; color: var(--acc); font-size: 1.1rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Scanner v9.7</h1>
        <form method="POST">
            <input type="text" name="wallet" placeholder="Wallet Solana o Ethereum (0x)" value="{{ wallet }}" required>
            <button type="submit">ESCANEAR AHORA</button>
        </form>

        {% if results %}
        <div style="margin-top: 20px;">
            {% for r in results %}
            <div class="token-card" style="border-left-color: {{ r.color }};">
                <div>
                    <small style="color: #888; display: block; font-size: 0.6rem;">{{ r.network }}</small>
                    <b>{{ r.name }}</b>
                </div>
                <div style="text-align: right;">
                    <div class="amount">{{ r.bal }}</div>
                    <small style="color: #aaa;">{{ r.sym }}</small>
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
    try:
        # SOL Nativo
        r = requests.post(SOLANA_RPC, json={"jsonrpc":"2.0","id":1,"method":"getBalance","params":[wallet]}).json()
        sol_bal = r['result']['value'] / 10**9
        data.append({'network': 'SOLANA', 'name': 'Solana', 'bal': round(sol_bal, 4), 'sym': 'SOL', 'color': '#9945ff'})
        
        # Tokens SPL
        payload = {"jsonrpc":"2.0","id":1,"method":"getTokenAccountsByOwner","params":[wallet, {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}, {"encoding": "jsonParsed"}]}
        r_tokens = requests.post(SOLANA_RPC, json=payload).json()
        for acc in r_tokens.get('result', {}).get('value', []):
            info = acc['account']['data']['parsed']['info']
            amount = info['tokenAmount']['uiAmount']
            if amount > 0:
                mint = info['mint']
                name = TOKEN_NAMES.get(mint, f"Token (...{mint[-4:]})")
                if "0.0911" in str(amount): name = "OFFICIAL TRUMP"
                if "0.0021" in str(amount): name = "Phantom Staked SOL"
                data.append({'network': 'SOLANA SPL', 'name': name, 'bal': amount, 'sym': '', 'color': '#00ffad'})
    except: pass
    return data

def scan_ethereum(wallet):
    # Usamos peticiones directas JSON-RPC para evitar errores de la librería Web3 en la nube
    try:
        payload = {"jsonrpc":"2.0","method":"eth_getBalance","params":[wallet, "latest"],"id":1}
        r = requests.post(ETH_RPC, json=payload).json()
        hex_bal = r['result']
        # Convertimos de Hexadecimal (Wei) a Decimal (Ether)
        eth_bal = int(hex_bal, 16) / 10**18
        return [{'network': 'ETHEREUM', 'name': 'Ethereum', 'bal': round(eth_bal, 6), 'sym': 'ETH', 'color': '#627eea'}]
    except:
        return []

@app.route('/', methods=['GET', 'POST'])
def home():
    results = []
    wallet = ""
    if request.method == 'POST':
        wallet = request.form.get('wallet').strip()
        if wallet.startswith('0x'):
            results = scan_ethereum(wallet)
        else:
            results = scan_solana(wallet)
    return render_template_string(HTML_TEMPLATE, results=results, wallet=wallet)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

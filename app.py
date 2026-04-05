from flask import Flask, render_template_string, request
import requests
import os

app = Flask(__name__)

# --- NODOS RPC ---
SOLANA_RPC = "https://api.mainnet-beta.solana.com"
ETH_RPC = "https://cloudflare-eth.com"

# --- MAPA DE TOKENS ---
TOKEN_NAMES = {
    "6p6W5unidS93h2566NcLC5GfJp0R3S30Nc9S3L5G3": "OFFICIAL TRUMP",
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC"
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scanner Pro</title>
    <style>
        body { background: #0b0e11; color: white; font-family: sans-serif; text-align: center; padding: 20px; }
        .container { max-width: 450px; margin: auto; background: #1e2329; padding: 25px; border-radius: 20px; border: 1px solid #333; }
        input { width: 90%; padding: 12px; border-radius: 8px; border: 1px solid #444; background: #0b0e11; color: white; margin-bottom: 10px; }
        button { width: 95%; padding: 12px; background: #00ffad; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; color: #0b0e11; }
        .card { background: #2b3139; padding: 15px; border-radius: 10px; margin-top: 10px; display: flex; justify-content: space-between; border-left: 4px solid #00ffad; text-align: left; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🚀 Multi-Scanner v9.9</h2>
        <form method="POST">
            <input type="text" name="wallet" placeholder="Wallet Solana o ETH (0x)" value="{{ wallet }}" required>
            <button type="submit">ESCANEAR</button>
        </form>
        {% if results %}
            {% for r in results %}
            <div class="card">
                <div><small style="color: #888;">{{ r.net }}</small><br><b>{{ r.name }}</b></div>
                <div style="text-align: right;"><b>{{ r.bal }}</b><br><small>{{ r.sym }}</small></div>
            </div>
            {% endfor %}
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
            if wallet.startswith('0x'):
                # ESCANEO ETHEREUM DIRECTO
                p = {"jsonrpc":"2.0","method":"eth_getBalance","params":[wallet, "latest"],"id":1}
                r = requests.post(ETH_RPC, json=p).json()
                if 'result' in r:
                    val = int(r['result'], 16) / 10**18
                    results.append({'net': 'ETHEREUM', 'name': 'Ethereum', 'bal': round(val, 6), 'sym': 'ETH'})
            else:
                # ESCANEO SOLANA DIRECTO
                r_sol = requests.post(SOLANA_RPC, json={"jsonrpc":"2.0","id":1,"method":"getBalance","params":[wallet]}).json()
                sol_bal = r_sol['result']['value'] / 10**9
                results.append({'net': 'SOLANA', 'name': 'Solana', 'bal': round(sol_bal, 4), 'sym': 'SOL'})
                
                # TOKENS SOLANA
                p_tk = {"jsonrpc":"2.0","id":1,"method":"getTokenAccountsByOwner","params":[wallet, {"programId":

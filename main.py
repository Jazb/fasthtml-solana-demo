from fasthtml.common import *
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey
import base58

app, rt = fast_app(secret_key="tu_clave_secreta_aqui", session_cookie="session")
solana = Client("https://api.devnet.solana.com")

class WalletManager:
    def __init__(self):
        self.wallets = {}

    def create_new(self, session):
        if 'wallet' in session:
            return session['wallet']['pubkey']
        
        keypair = Keypair()
        pubkey = str(keypair.pubkey())
        self.wallets[pubkey] = bytes(keypair).hex()
        session['wallet'] = {'pubkey': pubkey, 'private_key': self.wallets[pubkey]}
        return pubkey

wallet_manager = WalletManager()

@rt('/')
def get_root():
    return Div(
        H1("Solana Blockchain Demo"),
        Div(
            Button("Create Wallet", hx_post="/create_wallet"),
            id="wallet-section",
            class_="box"
        ),
        Div(id="actions", class_="box hidden"),
        Script("""
            htmx.on('htmx:afterSwap', function(evt) {
                if(evt.detail.target.id === 'wallet-section') {
                    document.getElementById('actions').classList.remove('hidden');
                }
            });
        """)
    )

@rt('/create_wallet')
def post(session):
    if 'wallet' in session:
        return Div(
            P("¡Ya tienes una wallet!"),
            Button("Recrear Wallet", hx_post="/recreate_wallet",
                   hx_target="#wallet-section", hx_swap="outerHTML"),
            class_="existing-wallet"
        )
    
    pubkey = wallet_manager.create_new(session)
    return Div(
        H3("Nueva Wallet Creada"),
        Pre(f"Llave pública: {pubkey}"),
        Button("Ver Balance", hx_get=f"/balance/{pubkey}"),
        Form(
            Input(type="text", name="to", placeholder="Destino"),
            Input(type="number", name="amount", placeholder="Cantidad SOL", step="0.000001"),
            Button("Enviar SOL", hx_post=f"/send/{pubkey}")
        )
    )

@rt('/recreate_wallet')
def post(session):
    if 'wallet' in session:
        del session['wallet']
    
    pubkey = wallet_manager.create_new(session)
    return Div(
        H3("Nueva Wallet Creada"),
        Pre(f"Llave pública: {pubkey}"),
        Button("Ver Balance", hx_get=f"/balance/{pubkey}"),
        Form(
            Input(type="text", name="to", placeholder="Destino"),
            Input(type="number", name="amount", placeholder="Cantidad SOL", step="0.000001"),
            Button("Enviar SOL", hx_post=f"/send/{pubkey}")
        )
    )

@rt('/balance/{pubkey}')
def get_balance(pubkey: str):
    balance = solana.get_balance(Pubkey.from_string(pubkey)).value / 1e9
    return P(f"Balance: {balance:.6f} SOL")

@rt('/send/{pubkey}')
def post(pubkey: str, to: str = Form(), amount: float = Form()):
    try:
        keypair = Keypair.from_bytes(bytes.fromhex(wallet_manager.wallets[pubkey]))
        tx = solana.transfer(
            keypair,
            Pubkey.from_string(to),
            int(amount * 1e9)
        )
        return Div(
            P(f"Sent {amount} SOL to {to}"),
            Pre(f"Transaction Hash: {tx.value}")
        )
    except Exception as e:
        return P(f"Error: {str(e)}", style="color: red")

serve()

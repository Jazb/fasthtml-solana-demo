from fasthtml.common import *
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey
import base58

app, rt = fast_app()
solana = Client("https://api.devnet.solana.com")

class WalletManager:
    def __init__(self):
        self.wallets = {}
        
    def create_new(self):
        keypair = Keypair()
        pubkey = str(keypair.pubkey())
        self.wallets[pubkey] = bytes(keypair).hex()
        return pubkey

wallet_manager = WalletManager()

@rt('/')
def get():
    return Div(
        H1("Solana Blockchain Demo"),
        Div(
            Button("Create Wallet", hx_post="/create_wallet"),
            id="wallet-section",
            class_="box"
        ),
        Div(id="actions", class_="box hidden"),
        script=Script("""
            htmx.on('htmx:afterSwap', function(evt) {
                if(evt.detail.target.id === 'wallet-section') {
                    document.getElementById('actions').classList.remove('hidden');
                }
            });
        """)
    )

@rt('/create_wallet', method='POST')
def create_wallet():
    pubkey = wallet_manager.create_new()
    return Div(
        H3("New Wallet Created"),
        Pre(f"Public Key: {pubkey}"),
        Button("Check Balance", hx_get=f"/balance/{pubkey}"),
        Form(
            Input(type="text", name="to", placeholder="Destination Public Key"),
            Input(type="number", name="amount", placeholder="Amount in SOL", step="0.000001"),
            Button("Send SOL"),
            hx_post=f"/send/{pubkey}"
        )
    )

@rt('/balance/{pubkey}')
def get_balance(pubkey: str):
    balance = solana.get_balance(Pubkey.from_string(pubkey)).value / 1e9
    return P(f"Balance: {balance:.6f} SOL")

@rt('/send/{pubkey}', method='POST')
def send_sol(pubkey: str, to: str = Form(), amount: float = Form()):
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

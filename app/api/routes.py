from fasthtml.common import *
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from .dependencies import get_solana_client, get_wallet_manager
from core.config import get_settings

settings = get_settings()

def setup_routes(rt):
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
        wallet_manager = get_wallet_manager()
        if 'wallet' in session:
            return Div(
                P("¡Ya tienes una wallet!"),
                Button("Recrear Wallet", hx_post="/recreate_wallet",
                       hx_target="#wallet-section", hx_swap="outerHTML"),
                class_="existing-wallet"
            )
        
        pubkey = wallet_manager.create_new(session)
        return _render_wallet_section(pubkey)

    @rt('/recreate_wallet')
    def post(session):
        wallet_manager = get_wallet_manager()
        if 'wallet' in session:
            del session['wallet']
        
        pubkey = wallet_manager.create_new(session)
        return _render_wallet_section(pubkey)

    @rt('/balance/{pubkey}')
    def get_balance(pubkey: str):
        solana = get_solana_client()
        balance = solana.get_balance(Pubkey.from_string(pubkey)).value / 1e9
        return P(f"Balance: {balance:.6f} SOL")

    @rt('/send/{pubkey}')
    def post(pubkey: str, to: str = Form(), amount: float = Form()):
        try:
            wallet_manager = get_wallet_manager()
            solana = get_solana_client()
            keypair = wallet_manager.get_keypair(pubkey)
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

def _render_wallet_section(pubkey: str):
    return Div(
        H3("Nueva Wallet Creada"),
        Pre(f"Llave pública: {pubkey}"),
        Button("Ver Balance", hx_get=f"/balance/{pubkey}"),
        Form(
            Input(type="text", name="to", placeholder="Destino"),
            Input(type="number", name="amount", placeholder="Cantidad SOL", step="0.000001"),
            Div(
                Button("Enviar SOL", hx_post=f"/send/{pubkey}"),
                Button("Recrear Wallet", hx_post="/recreate_wallet",
                      hx_target="#wallet-section", hx_swap="outerHTML"),
                style="display: flex; gap: 10px;"
            )
        )
    )

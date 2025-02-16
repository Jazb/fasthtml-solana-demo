from functools import lru_cache
from solana.rpc.api import Client
from core.config import get_settings
from services.wallet_service import WalletManager

@lru_cache()
def get_solana_client():
    settings = get_settings()
    return Client(settings.SOLANA_RPC_URL)

@lru_cache()
def get_wallet_manager():
    return WalletManager()

 # services/wallet_service.py
from core.config import get_settings
from core.security import EncryptionService
from solders.keypair import Keypair
from pydantic import BaseModel
from fasthtml.common import database

settings = get_settings()

class WalletSchema(BaseModel):
    public_key: str
    encrypted_private_key: bytes

class WalletManager:
    def __init__(self):
        self.wallets = {}
        
    def create_new(self, session):
        """Create a new wallet and store it in session"""
        try:
            if 'wallet' in session:
                return session['wallet']['pubkey']
            
            keypair = Keypair()
            pubkey = str(keypair.pubkey())
            self.wallets[pubkey] = bytes(keypair).hex()
            session['wallet'] = {'pubkey': pubkey, 'private_key': self.wallets[pubkey]}
            return pubkey
        except Exception as e:
            raise ValueError(f"Failed to create wallet: {str(e)}")
            
    def get_keypair(self, pubkey: str) -> Keypair:
        """Get keypair for a public key"""
        try:
            return Keypair.from_bytes(bytes.fromhex(self.wallets[pubkey]))
        except KeyError:
            raise ValueError(f"Wallet not found for pubkey: {pubkey}")
        except Exception as e:
            raise ValueError(f"Failed to get keypair: {str(e)}")

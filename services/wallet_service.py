 # services/wallet_service.py
  from core.config import config
  from core.security import EncryptionService
  from solders.keypair import Keypair
  from pydantic import BaseModel
  from fasthtml.common import database

  class WalletSchema(BaseModel):
      public_key: str
      encrypted_private_key: bytes

  class WalletService:
      def __init__(self):
          self.db = database(config.DB_PATH)
          self.crypto = EncryptionService(config.ENCRYPTION_KEY)
          self._init_db()

      def _init_db(self):
          if 'wallets' not in self.db.t:
              self.db.create('wallets',
                           public_key=str,
                           encrypted_private_key=bytes)

      def create_wallet(self, session) -> WalletSchema:
          keypair = Keypair()

          wallet = WalletSchema(
              public_key=str(keypair.pubkey()),
              encrypted_private_key=self.crypto.encrypt_key(
                  bytes(keypair)
              )
          )

          self.db.t.wallets.insert(wallet.dict())
          session['wallet'] = {"public_key": wallet.public_key}
          return wallet

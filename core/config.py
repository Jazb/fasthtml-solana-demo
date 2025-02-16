from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Solana Wallet Demo"
    DEBUG: bool = False
    SECRET_KEY: str = "tu_clave_secreta_aqui"
    SESSION_COOKIE: str = "session"
    
    # Solana settings
    SOLANA_RPC_URL: str = "https://api.devnet.solana.com"
    SOLANA_NETWORK: str = "devnet"
    SOLANA_RPC: str = "https://api.mainnet-beta.solana.com"
    MAX_SOL: str = "100"
    
    # Security
    ENCRYPTION_KEY: str = "your-encryption-key-here"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

@lru_cache()
def get_settings():
    return Settings()

# Create required directories
def create_dirs():
    Path("data").mkdir(exist_ok=True)
    
create_dirs()

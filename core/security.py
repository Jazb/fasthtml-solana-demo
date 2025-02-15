 # core/security.py
  from cryptography.fernet import Fernet
  from fasthtml.common import Middleware

  class EncryptionService:
      def __init__(self, encryption_key: str):
          self.cipher = Fernet(encryption_key.encode())

      def encrypt_key(self, private_key: bytes) -> bytes:
          return self.cipher.encrypt(private_key)

      def decrypt_key(self, encrypted_key: bytes) -> bytes:
          return self.cipher.decrypt(encrypted_key)

  class SecurityMiddleware(Middleware):
      async def __call__(self, scope, receive, send):
          async def secure_send(message):
              if message["type"] == "http.response.start":
                  headers = {
                      b"Content-Security-Policy": b"default-src 'self'",
                      b"X-Content-Type-Options": b"nosniff",
                      b"Strict-Transport-Security": b"max-age=63072000; includeSubDomains"
                  }
                  message.setdefault("headers", []).extend(headers.items())
              await send(message)

          await self.app(scope, receive, secure_send)

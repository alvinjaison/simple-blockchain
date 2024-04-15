import ecdsa
import hashlib
import base58

class Wallet:
    def __init__(self):
        # Generate a new private key
        self.private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        # Derive the corresponding public key from the private key
        self.public_key = self.private_key.get_verifying_key()

    def get_address(self):
        # Serialize the public key and hash it with SHA-256
        public_key_bytes = self.public_key.to_string()
        sha256_hash = hashlib.sha256(public_key_bytes).digest()
        # Perform RIPEMD-160 hash on the SHA-256 hash
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
        # Add version byte (0x00 for Bitcoin mainnet)
        extended_hash = b'\x00' + ripemd160_hash
        # Perform double SHA-256 hash to create checksum
        checksum = hashlib.sha256(hashlib.sha256(extended_hash).digest()).digest()[:4]
        # Concatenate the extended hash and checksum
        binary_address = extended_hash + checksum
        # Encode the binary address using Base58 encoding
        address = base58.b58encode(binary_address)
        return address.decode('utf-8')

# Example usage:
wallet = Wallet()
print("Private Key:", wallet.private_key.to_string().hex())
print("Public Key:", wallet.public_key.to_string().hex())
print("Wallet Address:", wallet.get_address())



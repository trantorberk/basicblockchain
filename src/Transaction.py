
from datetime import datetime
from Crypto.Hash import SHA256
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as signer
import base64

# Transaction class handles transaction data between
# peers. It also provides digital signatures for each
# transaction.


class Transaction():
    source = ''
    destination = ''
    coins = 0
    transactionHash = ''
    transactionSignature = ''
    validationTime = None

    @classmethod
    def initializeTransaction(self, source, destination, coins, transactionHash, transactionSignature, validationTime):
        self.source = source
        self.destination = destination
        self.coins = coins
        self.transactionHash = transactionHash
        self.transactionSignature = transactionSignature
        self.validationTime = validationTime
        return self

    def __init__(self, source, destination, coins, sourcePrivateKey):
        self.source = source
        self.destination = destination
        self.coins = coins
        self.setTransaction(sourcePrivateKey)

    def setTransaction(self, sourcePrivateKey):
        self.validationTime = datetime.now().strftime("%H:%M:%S")
        self.generateTransactionHash()

        transactionSigner = TransactionSignature()
        self.transactionSignature = transactionSigner.signTransaction(
            self.transactionHash, sourcePrivateKey)

    def generateTransactionHash(self):
        stream = self.source + self.destination + \
            str(self.coins) + self.validationTime
        self.transactionHash = SHA256.new(stream.encode("utf-8"))

    def approve(self):
        self.transactionHash = self.transactionHash.hexdigest()
        self.transactionSignature = base64.b64encode(
            self.transactionSignature).decode("ascii")


# We need digital signatures to validate our transactions.
# We can use any asymetric encryption algorithm. For my
# implementation, I will use RSA algorithm.
# ----
# For each transaction, we will encrypt the transaction
# hash with the source's private key and send it to the handler.
# Handler will validate transaction by decrypting the hash
# with the source's public key and compare it with the original
# transaction hash. If they are same, then validation will be done.


class TransactionSignature:
    def __init__(self):
        pass

    def signTransaction(self, transactionHash, privateKey) -> bytes:
        privateKey = self.decodeKeyPairs(privateKey)
        signature = signer.new(RSA.importKey(privateKey)).sign(transactionHash)
        return signature

    def validateTransaction(self, transactionHash, signedTransactionHash, publicKey) -> bool:
        publicKey = self.decodeKeyPairs(publicKey)
        validator = signer.new(RSA.importKey(publicKey)).verify(
            transactionHash, signedTransactionHash)
        return validator

    def decodeKeyPairs(self, key) -> bytes:
        return base64.b64decode(key)


def generateGenesisSignKeyPair() -> list:
    randomGenerator = Random.new().read
    keyPair = RSA.generate(1024, randomGenerator)
    privateKey = keyPair.exportKey('PEM')
    privateKey = base64.b64encode(privateKey).decode("ascii")

    publicKey = keyPair.publickey().exportKey('PEM')
    publicKey = base64.b64encode(publicKey).decode("ascii")

    return [publicKey, privateKey]
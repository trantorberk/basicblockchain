# This is my first blockchain implementation.
# There can be many bugs or wrong approaches,
# please check the potential bugs before using!
# Developed by Berk Kırtay

'''
MIT License

Copyright (c) 2021 Berk Kırtay

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from Crypto.Hash import SHA256
from datetime import datetime
import random
import string

from Transaction import TransactionSignature, Transaction, generateGenesisSignKeyPair


class GenesisBlockKeyProvider():
    GENESIS_BLOCK_PRIVATE_KEY = ""
    GENESIS_BLOCK_PUBLIC_KEY = ""

    def __init__(self):
        key_pair = generateGenesisSignKeyPair()
        self.GENESIS_BLOCK_PUBLIC_KEY = key_pair[0]
        self.GENESIS_BLOCK_PRIVATE_KEY = key_pair[1]

    def private_key(self) -> str:
        return self.GENESIS_BLOCK_PRIVATE_KEY

    def public_key(self) -> str:
        return self.GENESIS_BLOCK_PUBLIC_KEY


KEY_PAIR = None

# Every block keeps previous block's hash for validation between blocks.
# We create a hash code based on previous block's hash,
# block's validation time and transactions.
# This method is basically bitcoin's consensus approach


class Block():
    previousBlockHash = ''
    blockHash = ''
    blockMineSize = 0
    hashDifficulty = 0
    validationTime = None
    blockTransactionCapacity = 1000
    blockTransactions = []

    # Each block has its unique hash string which is being generated
    # with all the essential information in the block.

    def __init__(self, previousBlockHash, hashDifficulty, blockTransactions):
        self.hashDifficulty = hashDifficulty
        self.previousBlockHash = previousBlockHash
        self.blockTransactions = blockTransactions
        self.validationTime = datetime.now().strftime("%H:%M:%S")
        self.generateBlockHash()
        self.proofOfWork()

    def generateBlockHash(self):
        stream = str(self.previousBlockHash) + self.validationTime + \
            str(self.blockTransactions) + str(self.blockMineSize)
        self.blockHash = SHA256.new(stream.encode('utf-8')).hexdigest()

    # This is the block mining section. It generates hashes according to the difficulty
    # and guarantees the security of the blockchain with the work done.
    # This section can be improved since continuous increments of blockMineSize
    # is a poor way to generate different hash every turn.

    def proofOfWork(self):
        initialTime = datetime.now()
        while self.blockHash[len(self.blockHash) - self.hashDifficulty:] != "0" * self.hashDifficulty:
            self.generateBlockHash()
            self.blockMineSize += 1

        finalTime = datetime.now() - initialTime
        print(
            f"Block hash = {self.blockHash}\nis mined in {finalTime.total_seconds()} seconds.\n")


class Blockchain():
    blockchain = []
    hashDifficulty = 0
    miningReward = 0
    chainSize = 0
    transactions = []
    lastBlockLog = ''

    # We set blockchain's general features.

    def __init__(self, hashDifficulty, miningReward):
        self.hashDifficulty = hashDifficulty
        self.miningReward = miningReward
        self.blockchain = [self.createGenesisBlock()]
        print("Blockchain has been initialized...")
        print(
            f"Block mining difficulty is {hashDifficulty}.\nMiner reward per block is {miningReward}.")
        print(
            f"Block Transaction capacity is {self.blockchain[-1].blockTransactionCapacity}")

        print("Genesis block is initialized successfully.")

    # Genesis block is the first node of the blockchain,
    # so, we generated a random string for the starting point(hash).

    def createGenesisBlock(self):
        randomKey = ''.join(random.choice(string.ascii_lowercase)
                            for i in range(30))

       # genericTransactions = [Transaction("null", "null", 0)]

        global KEY_PAIR
        KEY_PAIR = GenesisBlockKeyProvider()
        # First transaction of the blockchain.
        genericTransactions = []

        self.validationFlag = True
        return Block(SHA256.new(randomKey.encode('utf-8')).hexdigest(),
                     self.hashDifficulty, genericTransactions)

    def getCurrentBlock(self):
        return self.blockchain[-1]

    def newBlock(self, transactions):
        self.insertBlockAndReevaluateDifficulty(
            Block(self.getCurrentBlock().blockHash, self.hashDifficulty, transactions))

        self.validateBlockchain()

    # Blockchain will make mining harder as it has more blocks.
    # This is a similar procedure for all other famous blockchain applications.
    # To be more precise, this implementation should be changed based on
    # peer numbers who actively mine blocks. I will change this
    # feature once I implement peer to peer network properly.

    def insertBlockAndReevaluateDifficulty(self, newBlock):
        self.blockchain.append(newBlock)
        self.chainSize += 1
        if self.hashDifficulty == 0:
            return

        while True:
            difficultyDeterminer = (self.chainSize / self.hashDifficulty) / 10
            if difficultyDeterminer < 10:
                break
            else:
                self.hashDifficulty += 1

    # To secure our blocks, we need to validate our blockchain.
    # We do that by simply checking hash data of the blocks.

    def validateBlockchain(self):
        for i in range(len(self.blockchain) - 1):
            if self.blockchain[i].blockHash != self.blockchain[i + 1].previousBlockHash:
                print("Blockchain isn't valid!!!.\n")
                self.validationFlag = False
                self.handleInvalidBlock()
        self.validationFlag = True

    def handleInvalidBlock(self):
        while self.validationFlag == False:
            try:
                self.blockchain.pop()
                print(
                    f"Trying to recover the blockchain to the previous version. Last block index is {len(self.blockchain)}\n")
                self.validateBlockchain()
            except:
                print("There is no block left! Creating a new genesis block..")
                self.blockchain = [self.createGenesisBlock()]
                break
        return

    # This function is responsible for adding transactions to
    # the blockchain and checking them if they are valid.

    def addTransaction(self, newTransaction):
        transactionCoins = self.getBalance(newTransaction.source)

        if newTransaction.coins <= 0:
            self.lastBlockLog = f"Transaction amount can't be a negative value!"
            print(self.lastBlockLog)
            return False

        if transactionCoins < newTransaction.coins:
            self.lastBlockLog = f"Insufficient coins in the source! {newTransaction.source} needs: {newTransaction.coins - transactionCoins}"
            print(self.lastBlockLog)
            return False

        self.transactions.append(newTransaction)

        # ***Activate this to get only one transaction per block.***
        # self.handleTransaction("null")

        return True

    def addText(self, newText):
        self.transactions.append(newText)

    # Forcing transactions is only for testing. It creates a
    # transaction with the genesis block's signature.

    def forceTransaction(self, publicAddress, coins):
        newTransaction = Transaction(KEY_PAIR.public_key(),
                                     publicAddress,
                                     coins,
                                     KEY_PAIR.private_key())

        self.transactions.append(newTransaction)
        print(f"A forced transaction is added to the chain. Amount: {coins}")

    # When there is pending transactions, those transactions
    # should be handled by a miner. This is implemented in the
    # function below.

    def handleTransaction(self, miningRewardAddress):
        work = len(self.transactions)

        # Every block has a limited space for the transactions.
        blockRewards = []
        while not len(self.transactions) == 0:
            limitedTransactions = []
            transactionsSize = 0
            if self.getCurrentBlock().blockTransactionCapacity > len(self.transactions):
                transactionsSize = len(self.transactions)
            else:
                transactionsSize = self.getCurrentBlock().blockTransactionCapacity

            for i in range(transactionsSize):
                nextTransaction = self.transactions.pop()
                isValid = self.validateTransaction(
                    nextTransaction, nextTransaction.source)

                if isValid == True:
                    nextTransaction.approve()
                    limitedTransactions.append(nextTransaction)

                    # Block rewards are being paid from transaction fees.
                    blockRewards.append(Transaction(
                        KEY_PAIR.public_key(), miningRewardAddress, self.miningReward, KEY_PAIR.private_key()))

            # Create a genesis private key to sign block rewards!
            self.newBlock(limitedTransactions.copy())

        self.transactions.clear()
        self.transactions = blockRewards.copy()

    def validateTransaction(self, newTransaction, publicKey):
        transactionSigner = TransactionSignature()
        validator = transactionSigner.validateTransaction(
            newTransaction.transactionHash, newTransaction.transactionSignature, publicKey)

        if validator == True:
            print(
                f'Transaction is validated! -> {newTransaction.transactionHash.hexdigest()}')
            return True
        return False

    # This function gets the balance of specified address
    # with checking all Transactions within the blockchain.

    def getBalance(self, addressofBalance):
        availableCoins = 0

        # With try/catch block, we prevent chat and balance
        # blocks to mix (We cannot mix integers and strings).

        for i in range(len(self.blockchain)):
            for j in range(len(self.blockchain[i].blockTransactions)):
                try:
                    if self.blockchain[i].blockTransactions[j].destination == addressofBalance:
                        availableCoins += self.blockchain[i].blockTransactions[j].coins
                    if self.blockchain[i].blockTransactions[j].source == addressofBalance:
                        availableCoins -= self.blockchain[i].blockTransactions[j].coins
                except:
                    continue

        return availableCoins

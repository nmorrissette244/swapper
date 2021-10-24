from web3 import Web3
from web3.middleware import geth_poa_middleware, http_retry_request_middleware
from ABIs import *
import os
import datetime
import time


def deadline():
    deadline = int(time.time()) + (10 * 60)
    return deadline


w3 = Web3(
    Web3.HTTPProvider(
        "https://rpc-mainnet.maticvigil.com/v1/9b81d85e98230a25fb6d807bb2d2dfa73c30dbbf"
    )
)
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.middleware_onion.add(http_retry_request_middleware)
print(w3.isConnected())
myAddress = "0x67CE9115e45510c567C3B53626Cdb02BB96cA887"
balance = w3.eth.get_balance(myAddress)
matic_balance = float(Web3.fromWei(balance, "ether"))
# print(matic_balance)
chainID = 137
nonce = w3.eth.getTransactionCount(myAddress)

swap_contract = w3.eth.contract(
    address="0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff", abi=quickRouterABI
)

usdc_contract = w3.eth.contract(
    address="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", abi=usdc_abi
)
usdt_contract = w3.eth.contract(
    address="0xc2132D05D31c914a87C6611C10748AEb04B58e8F", abi=usdt_abi
)

spender = "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"
amount = 5000000

private_key = os.getenv("PRIVATE_KEY")
print(private_key)

account = w3.eth.account.from_key(private_key)

print(account.address)

timestamp = datetime.datetime.now()
print(timestamp)

# First we have to approve USDC
# Need approval transaction parameters to build txn

approve_txn_params = {
    "chainId": chainID,
    "from": myAddress,
    "nonce": nonce + 1,
    "gasPrice": 40000000000,
    "gas": 1000000,
}

# Create TXN
approve_txn = usdc_contract.functions.approve(
    Web3.toChecksumAddress(spender), amount
).buildTransaction(approve_txn_params)

# Sign TXN
signed_approve_txn = w3.eth.account.sign_transaction(
    approve_txn, private_key=str(private_key)
)

# Send TXN
approve_txn_hash = w3.eth.send_raw_transaction(signed_approve_txn.rawTransaction)
# tx_receipt = w3.eth.wait_for_transaction_receipt(approve_txn_hash)

count = 0
# if tx_receipt is None and (count < 30):
# time.sleep(1)
# tx_receipt = w3.eth.getTransactionReceipt(txn_hash)


print("Approve happened")


# Now we have approved USDC, we can swap
# Need to create the swap transaction
swap_build_params = {"chainId": chainID, "from": myAddress, "nonce": nonce}

txn_params = [
    1000000,
    997788,
    [
        "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
        "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
    ],
    myAddress,
    deadline(),
]

swap = swap_contract.functions.swapExactTokensForTokens(
    1000000,
    997000,
    [
        "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
        "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
    ],
    myAddress,
    deadline(),
)

swap_txn = swap.buildTransaction(swap_build_params)

signed_swap_txn = w3.eth.account.sign_transaction(swap_txn, private_key=private_key)

swap_txn_hash = w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)

tx_receipt = w3.eth.wait_for_transaction_receipt(swap_txn_hash)

print(tx_receipt)

"""
# Working with deployed Contracts
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print(f"Initial Stored Value {simple_storage.functions.retrieve().call()}")
greeting_transaction = simple_storage.functions.store(15).buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)
signed_greeting_txn = w3.eth.account.sign_transaction(
    greeting_transaction, private_key=private_key
)
tx_greeting_hash = w3.eth.send_raw_transaction(signed_greeting_txn.rawTransaction)
print("Updating stored Value...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_greeting_hash)

print(simple_storage.functions.retrieve().call())"""

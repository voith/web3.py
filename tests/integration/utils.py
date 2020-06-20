from eth_utils import (
    is_dict,
    is_same_address,
)

from tests.integration.generate_fixtures import common
from web3._utils.module_testing.emitter_contract import (
    CONTRACT_EMITTER_ABI,
    CONTRACT_EMITTER_CODE,
    EMITTER_ENUM,
)

from web3._utils.module_testing.math_contract import (
    MATH_ABI,
    MATH_BYTECODE,
)


def setup_chain_state(web3):
    coinbase = web3.eth.coinbase

    assert is_same_address(coinbase, common.COINBASE)

    #
    # Math Contract
    #
    math_contract_factory = web3.eth.contract(
        abi=MATH_ABI,
        bytecode=MATH_BYTECODE,
    )
    math_deploy_receipt = common.deploy_contract(web3, 'math', math_contract_factory)
    assert is_dict(math_deploy_receipt)

    #
    # Emitter Contract
    #
    emitter_contract_factory = web3.eth.contract(
        abi=CONTRACT_EMITTER_ABI,
        bytecode=CONTRACT_EMITTER_CODE,
    )
    emitter_deploy_receipt = common.deploy_contract(web3, 'emitter', emitter_contract_factory)
    emitter_contract = emitter_contract_factory(emitter_deploy_receipt['contractAddress'])

    txn_hash_with_log = emitter_contract.functions.logDouble(
        which=EMITTER_ENUM['LogDoubleWithIndex'], arg0=12345, arg1=54321,
    ).transact({
        'from': web3.eth.coinbase,
    })
    print('TXN_HASH_WITH_LOG:', txn_hash_with_log)
    txn_receipt_with_log = common.mine_transaction_hash(web3, txn_hash_with_log)
    block_with_log = web3.eth.getBlock(txn_receipt_with_log['blockHash'])
    print('BLOCK_HASH_WITH_LOG:', block_with_log['hash'])

    #
    # Empty Block
    #
    empty_block_number = common.mine_block(web3)
    print('MINED_EMPTY_BLOCK')
    empty_block = web3.eth.getBlock(empty_block_number)
    assert is_dict(empty_block)
    assert not empty_block['transactions']
    print('EMPTY_BLOCK_HASH:', empty_block['hash'])

    #
    # Block with Transaction
    #
    web3.geth.personal.unlock_account(coinbase, common.KEYFILE_PW)
    web3.geth.miner.start(1)
    mined_txn_hash = web3.eth.sendTransaction({
        'from': coinbase,
        'to': coinbase,
        'value': 1,
        'gas': 21000,
        'gas_price': web3.eth.gasPrice,
    })
    mined_txn_receipt = common.mine_transaction_hash(web3, mined_txn_hash)
    print('MINED_TXN_HASH:', mined_txn_hash)
    block_with_txn = web3.eth.getBlock(mined_txn_receipt['blockHash'])
    print('BLOCK_WITH_TXN_HASH:', block_with_txn['hash'])

    fixture = {
        'math_deploy_txn_hash': math_deploy_receipt['transactionHash'],
        'math_address': math_deploy_receipt['contractAddress'],
        'emitter_deploy_txn_hash': emitter_deploy_receipt['transactionHash'],
        'emitter_address': emitter_deploy_receipt['contractAddress'],
        'txn_hash_with_log': txn_hash_with_log,
        'block_hash_with_log': block_with_log['hash'],
        'empty_block_hash': empty_block['hash'],
        'mined_txn_hash': mined_txn_hash,
        'block_with_txn_hash': block_with_txn['hash'],
    }
    return fixture

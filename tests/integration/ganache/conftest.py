import pytest

from eth_utils import (
    is_checksum_address,
    is_dict,
)

from tests.integration.parity.utils import get_process, wait_for_http
from tests.integration.utils import setup_chain_state
from tests.utils import get_open_port
from web3 import Web3


COINBASE = '0xdc544d1aa88ff8bbd2f2aec754b1f1e99e1812fd'
COINBASE_PK = '0x58d23b55bc9cdce1f18c2500f40ff4ab7245df9a89505e9b1fa4851f623d241d'

KEYFILE_DATA = '{"address":"dc544d1aa88ff8bbd2f2aec754b1f1e99e1812fd","crypto":{"cipher":"aes-128-ctr","ciphertext":"52e06bc9397ea9fa2f0dae8de2b3e8116e92a2ecca9ad5ff0061d1c449704e98","cipherparams":{"iv":"aa5d0a5370ef65395c1a6607af857124"},"kdf":"scrypt","kdfparams":{"dklen":32,"n":262144,"p":1,"r":8,"salt":"9fdf0764eb3645ffc184e166537f6fe70516bf0e34dc7311dea21f100f0c9263"},"mac":"4e0b51f42b865c15c485f4faefdd1f01a38637e5247f8c75ffe6a8c0eba856f6"},"id":"5a6124e0-10f1-4c1c-ae3e-d903eacb740a","version":3}'  # noqa: E501

KEYFILE_PW = 'web3py-test'
KEYFILE_FILENAME = 'UTC--2017-08-24T19-42-47.517572178Z--dc544d1aa88ff8bbd2f2aec754b1f1e99e1812fd'  # noqa: E501

RAW_TXN_ACCOUNT_PK = '0xcf4b7e0aedcdfbe5d3571ed774ca08e3ad2b1f24104edb24c25331f7aa18cd43'
RAW_TXN_ACCOUNT = '0xdC726c28B91f4eE755Bf9ABB17d7E9F3E6C09597'

UNLOCKABLE_PRIVATE_KEY = '0x392f63a79b1ff8774845f3fa69de4a13800a59e7083f5187f1558f0797ad0f01'
UNLOCKABLE_ACCOUNT = '0x12efdc31b1a8fa1a1e756dfd8a1601055c971e13'


@pytest.fixture(scope="module")
def rpc_port():
    return get_open_port()


@pytest.fixture(scope="module")
def endpoint_uri(rpc_port):
    return 'http://localhost:{0}'.format(rpc_port)


@pytest.fixture(scope="module")
def ganache_process(rpc_port):
    arguments = (
        'ganache-cli',
        '--port', rpc_port,
        '--account', f'{COINBASE_PK},1000000000000000000000000000',
        '--account', f'{UNLOCKABLE_PRIVATE_KEY},1000000000000000000000000000',
        '--account', f'{RAW_TXN_ACCOUNT_PK},1000000000000000000000000000',
    )
    yield from get_process(arguments)


@pytest.fixture(scope="module")
def web3(ganache_process, endpoint_uri):
    wait_for_http(endpoint_uri)
    w3 = Web3(Web3.HTTPProvider(endpoint_uri))
    return w3


@pytest.fixture(scope="module")
def ganache_fixture(web3):
    return setup_chain_state(web3)


@pytest.fixture(scope='module')
def coinbase(web3):
    return web3.eth.coinbase


@pytest.fixture(scope="module")
def math_contract_deploy_txn_hash(ganache_fixture):
    return ganache_fixture['math_deploy_txn_hash']


@pytest.fixture(scope="module")
def math_contract(web3, math_contract_factory, ganache_fixture):
    return math_contract_factory(address=ganache_fixture['math_address'])


@pytest.fixture()
def math_contract_address(math_contract, address_conversion_func):
    return address_conversion_func(math_contract.address)


@pytest.fixture(scope="module")
def emitter_contract(web3, emitter_contract_factory, ganache_fixture):
    return emitter_contract_factory(address=ganache_fixture['emitter_address'])


@pytest.fixture()
def emitter_contract_address(emitter_contract, address_conversion_func):
    return address_conversion_func(emitter_contract.address)


@pytest.fixture(scope="module")
def unlocked_account(web3, unlockable_account, unlockable_account_pw):
    yield unlockable_account


@pytest.fixture(scope='module')
def unlockable_account_pw():
    return KEYFILE_PW


@pytest.fixture(scope="module")
def unlockable_account(web3, coinbase):
    yield coinbase


@pytest.fixture()
def unlockable_account_dual_type(unlockable_account, address_conversion_func):
    return address_conversion_func(unlockable_account)


@pytest.fixture
def unlocked_account_dual_type(unlockable_account_dual_type):
    return unlockable_account_dual_type


@pytest.fixture(scope="module")
def funded_account_for_raw_txn(ganache_fixture):
    account = ganache_fixture['raw_txn_account']
    assert is_checksum_address(account)
    return account


@pytest.fixture(scope="module")
def empty_block(web3, ganache_fixture):
    block = web3.eth.getBlock(ganache_fixture['empty_block_hash'])
    assert is_dict(block)
    return block


@pytest.fixture(scope="module")
def block_with_txn(web3, ganache_fixture):
    block = web3.eth.getBlock(ganache_fixture['block_with_txn_hash'])
    assert is_dict(block)
    return block


@pytest.fixture(scope="module")
def mined_txn_hash(parity_fixture_data):
    return parity_fixture_data['mined_txn_hash']


@pytest.fixture(scope="module")
def block_with_txn_with_log(web3, ganache_fixture):
    block = web3.eth.getBlock(ganache_fixture['block_hash_with_log'])
    assert is_dict(block)
    return block


@pytest.fixture(scope="module")
def txn_hash_with_log(ganache_fixture):
    return ganache_fixture['txn_hash_with_log']


@pytest.fixture(scope="module")
def txn_filter_params(coinbase):
    return {
        "fromBlock": "earliest",
        "toBlock": "latest",
        "fromAddress": [coinbase],
    }

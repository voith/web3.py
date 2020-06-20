import contextlib
import json
import os
import pprint
import shutil
import sys


from eth_utils.toolz import (
    merge,
)

import common
from tests.utils import (
    get_open_port,
)
from web3 import Web3


# this script is used for generating the parity fixture
# to generate geth fixtures use tests/generate_go_ethereum_fixture.py


def generate_go_ethereum_fixture(destination_dir):
    with contextlib.ExitStack() as stack:
        datadir = stack.enter_context(common.tempdir())

        keystore_dir = os.path.join(datadir, 'keystore')
        common.ensure_path_exists(keystore_dir)
        keyfile_path = os.path.join(keystore_dir, common.KEYFILE_FILENAME)
        with open(keyfile_path, 'w') as keyfile:
            keyfile.write(common.KEYFILE_DATA)
        genesis_file_path = os.path.join(datadir, 'genesis.json')
        with open(genesis_file_path, 'w') as genesis_file:
            genesis_file.write(json.dumps(common.GENESIS_DATA))

        geth_ipc_path_dir = stack.enter_context(common.tempdir())
        geth_ipc_path = os.path.join(geth_ipc_path_dir, 'geth.ipc')

        geth_port = get_open_port()
        geth_binary = common.get_geth_binary()

        geth_proc = stack.enter_context(common.get_geth_process(  # noqa: F841
            geth_binary=geth_binary,
            datadir=datadir,
            genesis_file_path=genesis_file_path,
            ipc_path=geth_ipc_path,
            port=geth_port,
            networkid=str(common.GENESIS_DATA['config']['chainId'])
        ))

        common.wait_for_socket(geth_ipc_path)
        web3 = Web3(Web3.IPCProvider(geth_ipc_path))
        chain_data = setup_chain_state(web3)
        static_data = {
            'raw_txn_account': common.RAW_TXN_ACCOUNT,
            'keyfile_pw': common.KEYFILE_PW,
        }
        pprint.pprint(merge(chain_data, static_data))

        shutil.make_archive(destination_dir, 'zip', datadir)


if __name__ == '__main__':
    fixture_dir = sys.argv[1]
    generate_go_ethereum_fixture(fixture_dir)

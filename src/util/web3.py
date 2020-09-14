from collections import defaultdict
from logging import Logger
from typing import Union, List, Tuple

from eth_typing import HexStr, Hash32
from hexbytes import HexBytes
from web3 import Web3
from web3.datastructures import AttributeDict

from src.contracts.secret_contract import tx_args
from src.util.secretcli import create_unsigined_tx


def web3_provider(address_: str) -> Web3:
    if address_.startswith('http'):  # HTTP
        return Web3(Web3.HTTPProvider(address_))
    elif address_.startswith('ws'):  # WebSocket
        return Web3(Web3.WebsocketProvider(address_))
    else:  # IPC
        return Web3(Web3.IPCProvider(address_))


def extract_tx_by_address(address, block) -> list:
    # Note: block attribute dict has to be generated with full_transactions=True flag
    return [tx for tx in block.transactions if tx.to and address.lower() == tx.to.lower()]


def event_log(tx_hash: Union[Hash32, HexBytes, HexStr], events: List[str], provider: Web3, contract) -> \
        Union[Tuple[str, AttributeDict], None]:
    """
    Extracts logs of @event from tx_hash if present
    :param tx_hash:
    :param events: Case sensitive events name
    :param provider:
    :param contract: Web3 Contract
    :return: logs represented in 'AttributeDict' or 'None' if not found
    """
    receipt = provider.eth.getTransactionReceipt(tx_hash)
    for event in events:
        log = getattr(contract.events, event)().processReceipt(receipt)
        if log:
            data_index = 0
            return event, log[data_index]


def normalize_address(address: str):
    """Converts address to address acceptable by web3"""
    try:
        return Web3.toChecksumAddress(address.lower())
    except:
        return address


def generate_unsigned_tx(secret_contract_address, log, chain_id, enclave_key, enclave_hash,
                         multisig_acc_addr: str):
    """Extracts the data from the web3 log objects and creates unsigned_tx acceptable by SCRT network"""
    # TODO: change
    return create_unsigined_tx(
        secret_contract_address,
        tx_args(
            log.args.value,
            log.transactionHash.hex(),
            log.args.recipient.decode()),
        chain_id,
        enclave_key,
        enclave_hash,
        multisig_acc_addr)


def contract_event_in_range(logger: Logger, provider: Web3, contract, event: str, from_block: int = 0,
                            to_block: Union[int, str] = 'latest'):
    """
    scans the blockchain, and yields blocks that has contract tx with the provided event

    Note: Be cautions with the range provided, as the logic creates query for each block which could be a buttel neck.
    :param from_block: starting block, defaults to 0
    :param to_block: end block, defaults to 'latest'
    :param event: name of the contract emit event you wish to be notified of
    """
    if to_block == 'latest':
        to_block = provider.eth.getBlock('latest').number

    for block_num in range(from_block, to_block):
        try:
            block = provider.eth.getBlock(block_num, full_transactions=True)
            contract_transactions = extract_tx_by_address(contract.address, block)

            if not contract_transactions:
                continue

            for tx in contract_transactions:
                _, log = event_log(tx_hash=tx.hash, event=[event], provider=provider, contract=contract.contract)

                if not log:
                    continue

                yield log
        except Exception as e:
            logger.error(msg=e)


def send_contract_tx(logger: Logger, provider: Web3, contract, function_name: str, from_acc: str, private_key: str,
                     *args, gas: int = 0):
    submit_tx = getattr(contract.contract.functions, function_name)(*args). \
        buildTransaction(
        {
            'from': from_acc,
            'chainId': provider.eth.chainId,
            'gasPrice': provider.eth.gasPrice if not gas else gas,
            'nonce': provider.eth.getTransactionCount(from_acc),
        })
    signed_txn = provider.eth.account.sign_transaction(submit_tx, private_key)
    try:
        provider.eth.sendRawTransaction(signed_txn.rawTransaction)
    except Exception as e:
        logger.error(msg=e)

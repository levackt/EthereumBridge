import json
from collections import namedtuple
from typing import Dict

from mongoengine import signals
from web3 import Web3

from src.contracts.contract import Contract
from src.db.collections.eth_swap import ETHSwap, Status
from src.db.collections.log import Logs
from src.db.collections.signatures import Signatures
from src.util.common import temp_file
from src.util.exceptions import catch_and_log
from src.util.logger import get_logger
from src.util.secretcli import sign_tx as secretcli_sign, decrypt
from src.util.web3 import event_log

MultiSig = namedtuple('MultiSig', ['multisig_acc_addr', 'signer_acc_name'])


class Signer:
    """Verifies Ethereum tx in SWAP_STATUS_UNSIGNED and adds it's signature"""

    def __init__(self, provider: Web3, multisig_: MultiSig, contract: Contract, config):
        self.provider = provider
        self.multisig = multisig_
        self.contract = contract

        signals.post_save.connect(self._new_tx_signal, sender=ETHSwap)
        self.logger = get_logger(db_name=config.db_name, logger_name=config.db_name)
        self.catch_up()

    def catch_up(self):
        for tx in ETHSwap.objects(status=Status.SWAP_STATUS_UNSIGNED.value):
            try:
                self._sign_tx(tx)
            except Exception as e:
                self.logger.error(msg=e)

    # noinspection PyUnusedLocal
    def _new_tx_signal(self, sender, document, **kwargs):
        if not document.status == Status.SWAP_STATUS_UNSIGNED.value:
            return
        try:
            self._sign_tx(document)
        except Exception as e:
            self.logger.error(msg=e)

    def _sign_tx(self, tx: ETHSwap):
        if self.is_signed(tx):
            Logs(log=f"Tried to sign an already signed tx. Signer:\n {self.multisig.signer_acc_name}.\ntx id:{tx.id}.")
            return

        if not self.is_valid(tx):
            Logs(log=f"Validation failed. Signer:\n {self.multisig.signer_acc_name}.\ntx id:{tx.id}.")
            return

        # noinspection PyBroadException
        signed_tx, success = catch_and_log(self.logger, self._sign_with_secret_cli, tx.unsigned_tx)

        if success:
            Signatures(tx_id=tx.id, signer=self.multisig.signer_acc_name, signed_tx=signed_tx).save()

    def is_signed(self, tx: ETHSwap) -> bool:
        """ Returns True if tx was already signed, else False """
        return Signatures.objects(tx_id=tx.id, signer=self.multisig.signer_acc_name).count() > 0

    def is_valid(self, tx: ETHSwap) -> bool:
        """Assert that the data in the unsigned_tx matches the tx on the chain"""
        log = event_log(tx.tx_hash, 'Swap', self.provider, self.contract.contract)
        unsigned_tx = json.loads(tx.unsigned_tx)
        try:
            res, success = catch_and_log(self.logger, self.decrypt, unsigned_tx)
            if not success:
                return False
            json_start_index = res.find('{')
            json_end_index = res.rfind('}') + 1
            decrypted_data = json.loads(res[json_start_index:json_end_index])
            assert decrypted_data['mint']['eth_tx_hash'] == log.transactionHash.hex()
            assert decrypted_data['mint']['amount_seth'] == log.args.value
            assert decrypted_data['mint']['to'] == log.args.recipient.decode()
        except AssertionError as e:
            Logs(log=repr(e)).save()
            return False

        return True

    def _sign_with_secret_cli(self, unsigned_tx: str) -> str:
        with temp_file(unsigned_tx) as unsigned_tx_path:
            res = secretcli_sign(unsigned_tx_path, self.multisig.multisig_acc_addr, self.multisig.signer_acc_name)

        return res

    @staticmethod
    def decrypt(unsigned_tx: Dict):
        msg = unsigned_tx['value']['msg'][0]['value']['msg']
        return decrypt(msg)

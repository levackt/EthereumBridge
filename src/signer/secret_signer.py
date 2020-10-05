import json
from collections import namedtuple
from threading import Thread
from time import sleep
from typing import Dict

from mongoengine import OperationError

from src.contracts.ethereum.ethr_contract import EthereumContract
from src.db.collections.eth_swap import Swap, Status
from src.db.collections.signatures import Signatures
from src.util.common import temp_file
from src.util.config import Config
from src.util.logger import get_logger
from src.util.secretcli import sign_tx as secretcli_sign, decrypt

SecretAccount = namedtuple('SecretAccount', ['address', 'name'])


class SecretSigner(Thread):
    """Signs on the SCRT side, after verifying Ethereum tx stored in the db"""

    def __init__(self, multisig: SecretAccount, contract: EthereumContract, config: Config, **kwargs):
        self.multisig = multisig
        self.contract = contract
        self.config = config

        self.logger = get_logger(db_name=config['db_name'],
                                 logger_name=config.get('logger_name', self.__class__.__name__))
        self.setDaemon(True)
        super().__init__(group=None, name=f"SecretSigner-{self.multisig.name}", target=self.run, **kwargs)
        # signals.post_init.connect(self._tx_signal, sender=ETHSwap)  # TODO: test this with deployed db on machine

    def run(self):
        """Scans the db for unsigned swap tx and signs them"""
        while True:
            for tx in Swap.objects(status=Status.SWAP_STATUS_UNSIGNED):
                try:
                    self._validate_and_sign(tx)
                except ValueError as e:
                    self.logger.error(f'Failed to sign transaction: {tx} error: {e}')
            sleep(self.config['sleep_interval'])

    def _validate_and_sign(self, tx: Swap):
        """
        Makes sure that the tx is valid and signs it

        :raises: ValueError
        """
        if self._is_signed(tx):
            self.logger.warning(f"Tried to sign an already signed tx. Signer:"
                                f" {self.multisig.address}.tx id:{tx.id}. This could happen due to catch up or tests")
            return

        if not self._is_valid(tx):
            self.logger.error(f"Validation failed. Signer: {self.multisig.name}. Tx id:{tx.id}.")
            return

        try:
            signed_tx = self._sign_with_secret_cli(tx.unsigned_tx)
        except RuntimeError as e:
            raise ValueError from e

        try:
            Signatures(tx_id=tx.id, signer=self.multisig.name, signed_tx=signed_tx).save()
        except OperationError as e:
            self.logger.error(f'Failed to save tx in database: {tx}')
            raise ValueError from e

    def _is_signed(self, tx: Swap) -> bool:
        """ Returns True if tx was already signed, else False """
        return Signatures.objects(tx_id=tx.id, signer=self.multisig.name).count() > 0

    def _is_valid(self, tx: Swap) -> bool:
        """Assert that the data in the unsigned_tx matches the tx on the chain"""
        log = self.contract.get_events_by_tx(tx.src_tx_hash)
        if not log:  # because for some reason event_log can return None???
            return False

        try:
            unsigned_tx = json.loads(tx.unsigned_tx)
        except json.JSONDecodeError:
            self.logger.error(f'Tried to load tx with hash: {tx.src_tx_hash} '
                              f'but got raw data as invalid json')
            return False

        try:
            res = self._decrypt(unsigned_tx)
            self.logger.debug(f'Decrypted unsigned tx successfully {res}')
            json_start_index = res.find('{')
            json_end_index = res.rfind('}') + 1
            decrypted_data = json.loads(res[json_start_index:json_end_index])
            # assert decrypted_data['mint']['eth_tx_hash'] == log.transactionHash.hex()
            assert int(decrypted_data['mint']['amount']) == self.contract.extract_amount(log)
            assert decrypted_data['mint']['address'] == self.contract.extract_addr(log)
        except (json.JSONDecodeError, AssertionError) as e:
            self.logger.error(f"Failed to validate tx data: {tx}. Error: {e}")
            return False

        return True

    def _sign_with_secret_cli(self, unsigned_tx: str) -> str:
        with temp_file(unsigned_tx) as unsigned_tx_path:
            res = secretcli_sign(unsigned_tx_path, self.multisig.address, self.multisig.name)

        return res

    @staticmethod
    def _decrypt(unsigned_tx: Dict):
        msg = unsigned_tx['value']['msg'][0]['value']['msg']
        return decrypt(msg)

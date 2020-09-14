from threading import Thread, Event

from web3.datastructures import AttributeDict

from src.contracts.contract import Contract
from src.contracts.secret_contract import unsigned_mint_tx
from src.db.collections.eth_swap import ETHSwap, Status
from src.db.collections.moderator import Management, Source
from src.db.collections.signatures import Signatures
from src.event_listener import EventListener
from src.signers import MultiSig
from src.util.exceptions import catch_and_log
from src.util.logger import get_logger
from src.util.secretcli import create_unsigined_tx


class Manager:
    """Accepts new swap events and manages the tx status in db"""

    def __init__(self, event_listener: EventListener, contract: Contract, multisig: MultiSig, config):
        self.contract = contract
        self.config = config
        self.multisig = multisig
        self.event_listener = event_listener

        self.logger = get_logger(db_name=self.config.db_name, logger_name=self.config.logger_name)
        self.stop_signal = Event()

        event_listener.register(self._handle, ['Swap'], self.config.blocks_confirmation_required)
        Thread(target=self.run).start()
        Thread(target=self.catch_up).start()

    # noinspection PyUnresolvedReferences
    def run(self):
        """Scans for signed transactions and updates status if multisig threshold achieved"""
        while not self.stop_signal.is_set():
            for transaction in ETHSwap.objects(status=Status.SWAP_STATUS_UNSIGNED.value):
                if Signatures.objects(tx_id=transaction.id).count() >= self.config.signatures_threshold:
                    transaction.status = Status.SWAP_STATUS_SIGNED.value
                    transaction.save()
            self.stop_signal.wait(self.config.manager_sleep_time_seconds)

    # TODO: test
    def catch_up(self):
        from_block = Management.last_block(Source.eth.value, self.logger) + 1
        to_block = self.event_listener.provider.eth.getBlock('latest').number - self.config.blocks_confirmation_required

        if to_block <= 0:
            return

        for event in self.event_listener.events_in_range('Swap', from_block, to_block):
            self._handle(event)

    def _handle(self, transaction: AttributeDict):
        """Registers transaction to the db"""
        self._handle_swap_events(transaction)

    def _handle_swap_events(self, event: AttributeDict):
        """Extracts tx of event 'swap' and saves to db"""
        unsigned_tx, success = catch_and_log(self.logger,
                                             create_unsigined_tx,
                                             self.config.secret_contract_address,
                                             unsigned_mint_tx(
                                                 event.args.value,
                                                 event.transactionHash.hex(),
                                                 event.args.recipient.decode()),
                                             self.config.chain_id, self.config.enclave_key,
                                             self.config.enclave_hash, self.multisig.multisig_acc_addr)
        if success:
            ETHSwap.save_web3_tx(event, unsigned_tx)

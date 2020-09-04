import os
from shutil import copy, rmtree
from time import sleep

from brownie import project, network, accounts
from pytest import fixture

import src.contracts as contracts_package
import tests.integration as integration_package
from src.contracts.contract import Contract
from src.event_listener import EventListener
from src.leader import Leader
from src.manager import Manager
from src.util.common import module_dir

contracts_folder = module_dir(contracts_package)
brownie_project_folder = os.path.join(module_dir(integration_package), 'brownie_project')


@fixture(scope="module")
def make_project():
    # init brownie project structure
    project.new(brownie_project_folder)

    # copy contracts to brownie contract folder
    for contract in filter(lambda p: p.endswith(".sol"), os.listdir(contracts_folder)):
        copy(os.path.join(contracts_folder, contract), os.path.join(brownie_project_folder, 'contracts', contract))

    # load and compile contracts to project
    brownie_project = project.load(brownie_project_folder, name="Swap")
    brownie_project.load_config()

    # noinspection PyUnresolvedReferences
    from brownie.project.Swap import EthSwap
    network.connect('development')  # connect to ganache cli  # TODO: Consider if network reset required
    # EthSwap.deploy("EthSwap Token", "EST", 18, 1e20, {'from': accounts[0]})
    swap_contract = EthSwap.deploy({'from': accounts[0]})

    yield brownie_project, swap_contract, network, accounts

    # cleanup
    del brownie_project
    sleep(1)
    rmtree(brownie_project_folder, ignore_errors=True)


@fixture(scope="module")
def brownie_project(make_project):
    p, _, _, _ = make_project
    return p


@fixture(scope="module")
def swap_contract(make_project):
    _, contract, _, _ = make_project
    return contract


@fixture(scope="module")
def brownie_network(make_project):
    _, _, net, _ = make_project
    return net


@fixture(scope="module")
def ganache_accounts(make_project):
    _, _, _, acc = make_project
    return acc


@fixture(scope="module")
def web3_provider(brownie_network):
    return brownie_network.web3


@fixture(scope="module")
def contract(web3_provider, swap_contract):
    contract_address = swap_contract.address  # TODO: validate
    return Contract(web3_provider, contract_address)


@fixture(scope="module")
def manager(event_listener, contract, web3_provider, multisig_account, test_configuration):
    manager = Manager(event_listener, contract, web3_provider, multisig_account, test_configuration)
    yield manager
    manager.stop_signal.set()


@fixture(scope="module")
def leader(multisig_account, test_configuration):
    leader = Leader(multisig_account, multisig_account)
    yield leader
    leader.stop_event.set()


@fixture(scope="module")
def event_listener(contract, web3_provider):
    yield EventListener(contract, web3_provider)


def test(manager, leader, signer_accounts):
    brownie_project, swap_contract, network, accounts = make_project

    pass

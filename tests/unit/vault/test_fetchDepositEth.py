from brownie import reverts, web3 as w3
from consts import *


def test_fetchDepositEth(a, cf, DepositEth):
    # Get the address to deposit to and deposit
    depositAddr = getCreate2Addr(cf.vault.address, JUNK_HEX, DepositEth, "")
    cf.DEPLOYER.transfer(depositAddr, TEST_AMNT)

    assert cf.vault.balance() == 0

    # Sign the tx without a msgHash or sig
    callDataNoSig = cf.vault.fetchDepositEth.encode_input(NULL_SIG_DATA, JUNK_HEX)

    # Fetch the deposit
    cf.vault.fetchDepositEth(AGG_SIGNER_1.getSigData(callDataNoSig), JUNK_HEX)
    assert w3.eth.getBalance(w3.toChecksumAddress(depositAddr)) == 0
    assert cf.vault.balance() == TEST_AMNT


def test_fetchDepositEth_rev_swapID(cf):
    callDataNoSig = cf.vault.fetchDepositEth.encode_input(NULL_SIG_DATA, "")

    with reverts(REV_MSG_NZ_BYTES32):
        cf.vault.fetchDepositEth(AGG_SIGNER_1.getSigData(callDataNoSig), "")



def test_fetchDepositEth_rev_msgHash(cf):
    callDataNoSig = cf.vault.fetchDepositEth.encode_input(NULL_SIG_DATA, JUNK_HEX)

    sigData = AGG_SIGNER_1.getSigData(callDataNoSig)
    sigData[0] += 1
    # Fetch the deposit
    with reverts(REV_MSG_MSGHASH):
        cf.vault.fetchDepositEth(sigData, JUNK_HEX)


def test_fetchDepositEth_rev_sig(cf):
    callDataNoSig = cf.vault.fetchDepositEth.encode_input(NULL_SIG_DATA, JUNK_HEX)

    sigData = AGG_SIGNER_1.getSigData(callDataNoSig)
    sigData[1] += 1
    # Fetch the deposit
    with reverts(REV_MSG_SIG):
        cf.vault.fetchDepositEth(sigData, JUNK_HEX)

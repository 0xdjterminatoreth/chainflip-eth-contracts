import sys
import os
import json

sys.path.append(os.path.abspath("tests"))
from consts import *
from brownie import accounts, Token, TokenMessengerMock, network, MessageTransmitter
from deploy import deploy_set_Chainflip_contracts

import requests
import time

# NOTE: When forking a network (in another terminal) it spins a copy of the network
# with the default hardhat chain id 31337. Another option is to declare the network
# in hardhat.config.js, but we would need to add that manually as all the networks
# that we support are via brownie. Then brownie might not play well with that.
# Therefore we just spin the forks in another terminal via hardhat command.


AUTONOMY_SEED = os.environ["SEED"]
cf_accs = accounts.from_mnemonic(AUTONOMY_SEED, count=10)
DEPLOYER_ACCOUNT_INDEX = int(os.environ.get("DEPLOYER_ACCOUNT_INDEX") or 0)

DEPLOYER = cf_accs[DEPLOYER_ACCOUNT_INDEX]
print(f"DEPLOYER = {DEPLOYER}")

# Set the priority fee for all transactions
network.priority_fee("1 gwei")

# Only run in AVAX or AVAX fork.
# Spin AVAX-TEST fork on a separate terminal and run script:
#   npx hardhat node --fork https://api.avax-test.network/ext/bc/C/rpc
#   brownie run cctp avax-to-eth --network hardhat
# Run it on real avax-test:
#   brownie run cctp-avax-to-eth --network avax-test
def avax_to_eth():

    # Test AVAX to ETH
    # user_address = "0x37876B47DEE43492DAC3d87F7682df52dDBC65Ca"
    # This user address should have some AVAX and USDC

    tokenMessengerCCTP_avax_address = "0xeb08f243e5d3fcff26a9e38ae5520a669f4019d0"

    tokensToTransfer = 1 * 10**6
    ETH_DESTINATION_DOMAIN = 0
    deployedVaultGoerli = "0x123"
    USDC_AVAX_CONTRACT_ADDRESS = "0x5425890298aed601595a70AB815c96711a31Bc65"
    tokenMessengerCCTP_goerli = "0xd0c3da58f55358142b8d3e06c1c30c5c6114efe8"

    usdc_avax = Token.at(USDC_AVAX_CONTRACT_ADDRESS)
    # assert(cf.safekeeper == "0x37876B47DEE43492DAC3d87F7682df52dDBC65Ca")
    print(usdc_avax.balanceOf("0x37876B47DEE43492DAC3d87F7682df52dDBC65Ca"))
    print(tokensToTransfer)

    usdc_avax.approve(
        tokenMessengerCCTP_avax_address, tokensToTransfer, {"from": DEPLOYER}
    )

    # Make a call from an EOA to the Circle contract and get the messageHash
    tokenMessengerCCTP_avax = TokenMessengerMock.at(tokenMessengerCCTP_avax_address)
    tx = tokenMessengerCCTP_avax.depositForBurn(
        tokensToTransfer,
        ETH_DESTINATION_DOMAIN,
        deployedVaultGoerli,
        USDC_AVAX_CONTRACT_ADDRESS,
        {"from": DEPLOYER},
    )

    # Check DepositForBurn event
    assert tx.events["DepositForBurn"]["nonce"] != 0
    assert tx.events["DepositForBurn"]["burnToken"] == USDC_AVAX_CONTRACT_ADDRESS
    assert tx.events["DepositForBurn"]["amount"] == tokensToTransfer
    assert tx.events["DepositForBurn"]["depositor"] == DEPLOYER
    assert tx.events["DepositForBurn"]["mintRecipient"] == deployedVaultGoerli
    assert tx.events["DepositForBurn"]["destinationDomain"] == ETH_DESTINATION_DOMAIN
    assert (
        tx.events["DepositForBurn"]["destinationTokenMessenger"]
        == tokenMessengerCCTP_goerli
    )
    assert tx.events["DepositForBurn"]["destinationCaller"] == "0x0"

    assert tx.events["MessageSent"]["message"] != "0x1234"

    message = tx.events["MessageSent"]["message"]
    messageHash = web3.keccak(message)

    print("message: ", message)
    print("messageHash: ", messageHash)

    # We can now fetch the attestation from cirleci. We probably do this in different functions
    # with a real attestation.
    # fetch(`https://iris-api-sandbox.circle.com/attestations/${messageHash}`);


# Only run this on Goerli or Goerli fork.
# Spin Goerli fork on a separate terminal and run script:
#   npx hardhat node --fork https://goerli.infura.io/v3/<INFURA_API>
#   brownie run cctp avax-to-eth --network hardhat
# Run it on real Goerli:
#   brownie run cctp-avax-to-eth --network goerli
def eth_to_avax():

    cf = deploy_set_Chainflip_contracts(
        DEPLOYER, KeyManager, Vault, StakeManager, FLIP, os.environ
    )

    # Check we are in a Goerli fork
    # print(web3.eth.get_balance("0xc6e2459991BfE27cca6d86722F35da23A1E4Cb97"))
    # print(web3.eth.get_balance("0x37876B47DEE43492DAC3d87F7682df52dDBC65Ca"))

    ## Fund the Vault with our initial USDC
    # user_address = "0x37876B47DEE43492DAC3d87F7682df52dDBC65Ca"
    # This user address should have some AVAX and USDC

    usdc_goerli = Token.at("0x07865c6e87b9f70255377e024ace6630c1eaa37f")

    print("DEPLOYER: ", DEPLOYER)

    # We have a balance of 10*10**6
    # We force the transaction to be sent by the user but in reality we would
    # need to intput the SEED and sign it from there.
    initialBalance = usdc_goerli.balanceOf(DEPLOYER)
    tokensToTransfer = 1 * 10**6
    assert initialBalance > tokensToTransfer
    usdc_goerli.transfer(cf.vault.address, tokensToTransfer, {"from": DEPLOYER})

    assert usdc_goerli.balanceOf(cf.vault.address) == tokensToTransfer
    assert usdc_goerli.balanceOf(DEPLOYER) == initialBalance - tokensToTransfer

    # Craft a transaction to the CCTP address. For now using this instead of Brownie
    # encode_input because I want to avoid needing the contract here.
    tokenMessengerCCTP_goerli = TokenMessengerMock.at(
        "0xd0c3da58f55358142b8d3e06c1c30c5c6114efe8"
    )
    tokenMessengerCCTP_avax_address = "0xeb08f243e5d3fcff26a9e38ae5520a669f4019d0"

    calldata0 = usdc_goerli.approve.encode_input(
        tokenMessengerCCTP_goerli.address, tokensToTransfer
    )
    AVAX_DESTINATION_DOMAIN = 1
    destinationAddressInBytes32 = JUNK_HEX
    USDC_ETH_CONTRACT_ADDRESS = usdc_goerli
    calldata1 = tokenMessengerCCTP_goerli.depositForBurn.encode_input(
        tokensToTransfer,
        AVAX_DESTINATION_DOMAIN,
        destinationAddressInBytes32,
        USDC_ETH_CONTRACT_ADDRESS,
    )

    args = [[usdc_goerli, 0, calldata0], [tokenMessengerCCTP_goerli, 0, calldata1]]
    callDataNoSig = cf.vault.executeActions.encode_input(
        agg_null_sig(cf.keyManager.address, chain.id), args
    )
    tx = cf.vault.executeActions(
        AGG_SIGNER_1.getSigData(callDataNoSig, cf.keyManager.address),
        args,
        {"from": DEPLOYER},
    )

    assert usdc_goerli.balanceOf(cf.vault.address) == 0

    print("Interacting address: ", tokenMessengerCCTP_goerli)

    # Check DepositForBurn event
    assert tx.events["DepositForBurn"]["nonce"] != 0
    assert tx.events["DepositForBurn"]["burnToken"] == usdc_goerli
    assert tx.events["DepositForBurn"]["amount"] == tokensToTransfer
    assert tx.events["DepositForBurn"]["depositor"] == cf.vault.address
    assert tx.events["DepositForBurn"]["mintRecipient"] == destinationAddressInBytes32
    assert tx.events["DepositForBurn"]["destinationDomain"] == AVAX_DESTINATION_DOMAIN
    assert (
        tx.events["DepositForBurn"]["destinationTokenMessenger"]
        == tokenMessengerCCTP_avax_address
    )
    assert tx.events["DepositForBurn"]["destinationCaller"] == "0x0"

    assert tx.events["MessageSent"]["message"] != JUNK_HEX

    message = tx.events["MessageSent"]["message"]
    messageHash = web3.keccak(message)


def getAttestation(message):
    message_hash = web3.solidityKeccak(["bytes"], [message]).hex()
    # messageHash = "0xc9ac14d7c51d474215d3c01e024926d23c79a34816ecdc2cb81f685c1b1a1fbc"

    attestation_response = {"status": "pending"}
    while attestation_response["status"] != "complete":
        response = requests.get(
            f"https://iris-api-sandbox.circle.com/attestations/{message_hash}"
        )
        attestation_response = json.loads(response.text)
        time.sleep(2)

    # attestation_response = {'status': ... , 'attestation': ...}
    # attestation_response['attestation'] = '0x5c858ef0d057a12a309ddbe682d138f00ceae129377edc48b3e7cf050d74b34413729de6ce81fb05ceb3cdb50e689754d02134295fe84ff4d3e06df58f4a59751bf44e0efd9e56c7de548a98e95bc06995cd0fd3fb539bb13362230430e26944210d797913e10ca73d4814beba039a8f2328f806fffa4b9cea95f8e0e71aee4dab1c'
    print(attestation_response)
    return attestation_response["attestation"]


def submitAttestation():
    # Submit attestation. The hardcoded ones are to goerli
    AUTONOMY_SEED = os.environ["SEED"]
    cf_accs = accounts.from_mnemonic(AUTONOMY_SEED, count=10)
    DEPLOYER_ACCOUNT_INDEX = int(os.environ.get("DEPLOYER_ACCOUNT_INDEX") or 0)

    DEPLOYER = cf_accs[DEPLOYER_ACCOUNT_INDEX]
    print(f"DEPLOYER = {DEPLOYER}")

    # Set the priority fee for all transactions
    network.priority_fee("1 gwei")

    # Get attestation (hardcoding message for now)
    message = "0x000000000000000100000000000000000000a01b000000000000000000000000eb08f243e5d3fcff26a9e38ae5520a669f4019d0000000000000000000000000d0c3da58f55358142b8d3e06c1c30c5c6114efe80000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000005425890298aed601595a70ab815c96711a31bc65000000000000000000000000000000000000000000000000000000000000012300000000000000000000000000000000000000000000000000000000000f424000000000000000000000000037876b47dee43492dac3d87f7682df52ddbc65ca"

    attestation_response = getAttestation(message)

    messageTransmitterCCTP_goerli = MessageTransmitter.at(
        "0x26413e8157cd32011e726065a5462e97dd4d03d9"
    )
    tx = messageTransmitterCCTP_goerli.receiveMessage(
        message, attestation_response, {"from": DEPLOYER}
    )

    print(tx.events)
    # TODO: Check against ingress values. To do proper values.
    assert tx.events["MessageReceived"]["caller"] == DEPLOYER
    assert tx.events["MessageReceived"]["sourceDomain"] == 1
    assert tx.events["MessageReceived"]["nonce"] != 0
    # Should it be the vault on the ingress?
    assert tx.events["MessageReceived"]["sender"] != "0x123456"
    assert tx.events["MessageReceived"]["messageBody"] != "0x0"

    assert (
        tx.events["MintAndWithdraw"]["mintRecipient"]
        == "0x0000000000000000000000000000000000000123"
    )
    assert tx.events["MintAndWithdraw"]["amount"] == 1 * 10**6
    assert (
        tx.events["MintAndWithdraw"]["mintToken"]
        == "0x07865c6e87b9f70255377e024ace6630c1eaa37f"
    )

    assert False

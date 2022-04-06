from consts import *
from shared_tests import *
from brownie import reverts, web3, chain
from brownie.test import given, strategy


def test_flip_constructor(cf):
    assert cf.flip.getLastSupplyUpdateBlockNumber() == 0
    assert cf.flip.totalSupply() == INIT_SUPPLY
    assert cf.flip.balanceOf(cf.stakeManager) == STAKEMANAGER_INITIAL_BALANCE


def test_flip_constructor_reverts_nz(cf, FLIP):

    with reverts(REV_MSG_NZ_UINT):
        cf.DEPLOYER.deploy(
            FLIP,
            0,
            cf.numGenesisValidators,
            cf.genesisStake,
            cf.stakeManager.address,
            cf.keyManager,
        )

    with reverts(REV_MSG_NZ_ADDR):
        cf.DEPLOYER.deploy(
            FLIP,
            INIT_SUPPLY,
            cf.numGenesisValidators,
            cf.genesisStake,
            ZERO_ADDR,
            cf.keyManager,
        )

    with reverts(REV_MSG_NZ_ADDR):
        cf.DEPLOYER.deploy(
            FLIP,
            INIT_SUPPLY,
            cf.numGenesisValidators,
            cf.genesisStake,
            cf.stakeManager.address,
            ZERO_ADDR,
        )


@given(
    flipTotalSupply=strategy(
        "uint", min_value=INIT_SUPPLY / 2, max_value=INIT_SUPPLY * 2
    ),
    numGenesisValidators=strategy(
        "uint", min_value=NUM_GENESIS_VALIDATORS, max_value=NUM_GENESIS_VALIDATORS * 10
    ),
    genesisStake=strategy(
        "uint", min_value=GENESIS_STAKE, max_value=GENESIS_STAKE * 10**4
    ),
)
def test_flip_constructor_minting(
    a, maths, FLIP, flipTotalSupply, numGenesisValidators, genesisStake
):
    deployer = a[0]
    receiverGenesisValidatorFlip = a[1]
    keyManProxy = a[2]

    if numGenesisValidators * genesisStake > flipTotalSupply:
        with reverts(REV_MSG_INTEGER_OVERFLOW):
            deployer.deploy(
                FLIP,
                flipTotalSupply,
                numGenesisValidators,
                genesisStake,
                receiverGenesisValidatorFlip,
                keyManProxy,
            )
    else:
        flip = deployer.deploy(
            FLIP,
            flipTotalSupply,
            numGenesisValidators,
            genesisStake,
            receiverGenesisValidatorFlip,
            keyManProxy,
        )
        genesisValidatorFlip, remainder = maths.calculateFlipGenesis(
            flipTotalSupply, numGenesisValidators, genesisStake
        )
        assert flip.totalSupply() == flipTotalSupply
        assert flip.balanceOf(receiverGenesisValidatorFlip) == genesisValidatorFlip
        assert flip.balanceOf(deployer) == remainder

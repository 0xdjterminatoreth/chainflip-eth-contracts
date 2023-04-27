# Chainflip Ethereum Contracts

This repository contains the Ethereum smart contracts which are used to handle deposits and withdrawals based on signatures submitted via the vault nodes.

Additional information can be found in the [Ethereum Research](https://github.com/chainflip-io/ethereum-research) repository.

## Dependencies

- Python 2.7 or 3.5+
  For Ubuntu `sudo apt-get install python3 python-dev python3-dev build-essential`
- [Poetry (Python dependency manager)](https://python-poetry.org/docs/)

## Setup

First, ensure you have [Poetry](https://python-poetry.org), [Yarn](https://yarnpkg.com) and Ganache (`npm install -g ganache-cli`) are installed.

```bash
git clone git@github.com:chainflip-io/chainflip-eth-contracts.git
cd chainflip-eth-contracts
yarn
poetry shell
poetry install
brownie pm install OpenZeppelin/openzeppelin-contracts@4.0.0
pre-commit install
```

Then, create a `.env` file using `.env.example` as a reference. ~~You will need an infura key to run the tests~~, and a seed to run the deploy script on a live network.

### Running Tests

We use the `hardhat` EVM for testing, since we use EIP1559 opcodes.

```bash
# Run without the stateful tests, because they take hours
brownie test --network hardhat --stateful false
```

Run tests with additional features:

```bash
brownie test <test-name> -s --network hardhat --stateful <BOOL> --coverage --gas --hypothesis-seed <SEED>
```

Flags:

- `<test-name>` - Run a specific test. If no test-name is provided all tests are run.
- `-s`- Runs with the `print` outputs in tests.
- `--stateful <BOOL>` - Runs (or not) stateful tests. Stateful tests might take several hours so it is recommended to set it to false.
- `--gas` - generates a gas profile report
- `--coverage` - generates and updates the test coverage report under reports/coverage.json
- `--hypothesis-seed <SEED>` - Inputs a seed (int) to the hypothesis strategies. Useful to deterministically reproduce tests failures and for accurate gas comparisons when doing gas optimizations.

### Static Analysis

Slither is used for static analysis. Inside the poetry shell:

```bash
slither .
```

In the event of the command failing, try removing the `build/` directory and run it again.

### Linter

We use solhint and prettier for the solidity code and black for the python code. A general check is performed also in CI.

To locally do a general check on both solidity and python code: (please ensure you have poetry installed)

```bash
yarn lint
```

Format the solidity and python code:

```bash
yarn format
```

To format them separately run `yarn format-sol` or `yarn format-py`

## Fuzzing

Echidna is used for fuzzing the contracts. Make sure to follow Echidna's installation instructions or simply download the compiled binary. For Ubuntu:

```bash
curl -fL https://github.com/crytic/echidna/releases/download/v2.0.2/echidna-test-2.0.2-Ubuntu-18.04.tar.gz -o echidna-test-2.0.2-Ubuntu-18.04.tar.gz
tar -xvf echidna-test-2.0.2-Ubuntu-18.04.tar.gz
```

Make sure solc is installed with the latest versions with support to at least Solidity 0.8.0. To install:

`sudo snap install solc --edge`

Then Echidna can be run as normal. Echidna is not capable of reading the inherited contracts from packages under node_modules and needs an extra remapping in the config files. So always specify one of the echidna.config.yml files. There are different configuration files that can be specified for the different test modes.

```bash
./echidna-test contracts/echidna/tests/TestEchidna.sol --contract TestEchidna --config contracts/echidna/tests/echidna-assertion.config.yml
```

### Pre-commit hook

Pre-commit is part of the poetry virtual environment. Therefore, ensure that poetry is installed when commiting.

Current pre-commit hooks implemented:

- lint

To perform a commit without running the pre-commits, add the --no-verify flag to the git commit command. (not recommended)

### Generating Docs

Requires [Yarn](https://yarnpkg.com).

```bash
yarn docgen
```

## Notes

Brownie and `solidity-docgen` don't play very nice with each other. For this reason we've installed the OpenZeppelin contracts through both the brownie package manager (because it doesn't like node_modules when compiling internally), and `yarn` (because `solc` doesn't search the `~/.brownie` folder for packages).

This isn't an ideal solution but it'll do for now.

## Deploy the contracts

The deploying account will be allocated all the FLIP on a testnet (90M)

Inside the poetry shell:

### Local Test network

```bash
# if you haven't already started a hardhat node
npx hardhat node
# Instead, to run with interval mining - so the node continues mining blocks periodically
npx hardhat node --config hardhat-interval-mining.config.js
# If brownie fails to connect to the hardhat node check ip and run with the adequate hostname address. For instance:
npx hardhat node --hostname 127.0.0.1
# deploy the contracts - they will be deployed by acct #1 on the hardhat pre-seeded accounts
brownie run deploy_and
```

### Live Test network

```bash
# get this id from Infura and/or Alchemy
export WEB3_INFURA_PROJECT_ID=<Infura project id>
export WEB3_ALCHEMY_PROJECT_ID=<Infura project id>
# ensure that the ETH account associated with this seed has ETH on that network
export SEED="<your seed phrase>"
# Set an aggregate key, a governance address and a community address that you would like to use
export AGG_KEY=<agg key with leading parity byte, hex format, no leading 0x>
export GOV_KEY=<gov address with leading parity byte, hex format, with leading 0x>
export COMM_KEY=<comm address, hex format, with leading 0x>
# Set genesis parameters
export GENESIS_STAKE=<the stake each node should have at genesis> (default = 500000000000000000000000)
export NUM_GENESIS_VALIDATORS=<number of genesis validators in the chainspec you expect to start against this contract> (default = 5)

# deploy the contracts to rinkeby.
brownie run deploy_contracts --network rinkeby
# default configuratin uses Infura. To use Alchemy instead
brownie run deploy_contracts --network rinkeby-alchemy
```

## Useful commands

`brownie test -s` - runs with the `print` outputs in tests. Currently there are only `print` outputs in the stateful test so one can visually verify that most txs are valid and not reverting

`brownie test --stateful false` runs all tests EXCEPT stateful tests

`brownie test --stateful true` runs ONLY the stateful tests

`brownie run deploy_and all_events` will deploy the contracts and submit transactions which should emit the full suite of events

## Dev Tool

A dev tool is available ease development and debugging. It can be used on live networks (goerli, mainnet..), private networks and locally deployed networks (hardhat). To use it, first ensure that you have been through the setup process and you are inside the poetry shell.

The tool runs within the brownie framework and acts as a console-like client.

```bash
# To connect to a locally deployed network (hardhat), no endpoint is required.
# To connect to a public network just set your provider as normal
export WEB3_INFURA_PROJECT_ID=<Infura project id>
# or
export WEB3_ALCHEMY_PROJECT_ID=<Infura project id>

# Instead, to connect to a private network, import the network config file and
# set the RPC_URL that should be used to access the chain
brownie networks import ./network-config.yaml
export RPC_URL=<your_rpc_url>

# ensure that the ETH account associated with this seed has ETH on that network
export SEED="<your seed phrase>"
# set the required deployed contract addresses. All in hex format, with leading 0x
export FLIP_ADDRESS=<Address of the deployed FLIP contract>
export GATEWAY_ADDRESS=<Address of the deployed StateChain Gateway contract>
export VAULT_ADDRESS=<Address of the deployed Vault contract>
# Optional: only required when running USDC-related commands
export USDC_ADDRESS=<Address of the deployed Mock USDC contract>
# Optional - if not provided the tool will automatically obtain it
export KEY_MANAGER_ADDRESS=<Address of the deployed KeyManager contract>


# Run the tool specifying which network to use (private/goerli/hardhat)
brownie run devtool --network private-testnet

# When running the tool:
# Run `help` to display all supported commands
>> help

# Display user address
>> user

# Example of checking the ETH balance of the State Chain Gateway
>> balanceEth gateway

# Example of staking 2k FLIP for nodeId 0xDEADBEEF to the State Chain Gateway
>> fund 2000 0xDEADBEEF

# To eventually exit the tool
>> exit
```

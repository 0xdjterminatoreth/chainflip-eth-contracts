# Chainflip Ethereum Contracts

This repository contains the Ethereum smart contracts which are used to handle deposits and withdrawals based on signatures submitted via the vault nodes.

Additional information can be found in the [Ethereum Research](https://github.com/chainflip-io/ethereum-research) repository.


## Dependencies

- [Poetry (Python dependency manager)](https://python-poetry.org/docs/)

## Usage

First, ensure you have Poetry installed.

```
git clone git@github.com:chainflip-io/chainflip-eth-contracts.git
cd chainflip-eth-contracts
poetry shell
poetry install
brownie pm install OpenZeppelin/openzeppelin-contracts@3.3.0-solc-0.7
brownie test
```

### Generating Docs

Requires [Yarn](https://yarnpkg.com) and [NPX](https://www.npmjs.com/package/npx) to be installed.

```
yarn
npx solidity-docgen --solc-module solc-0.7
```

## Notes

Brownie and `solidity-docgen` don't play very nice with each other. For this reason we've installed the OpenZeppelin contracts through both the brownie package manager (because it doesn't like node_modules when compiling internally), and `yarn` (because `solc` doesn't search the `~/.brownie` folder for packages).

This isn't an ideal solution but it'll do for now.
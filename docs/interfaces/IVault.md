# `IVault`

  The interface for functions Vault implements

## `allBatch(struct IShared.SigData sigData, bytes32[] fetchSwapIDs, contract IERC20[] fetchTokens, contract IERC20[] tranTokens, address payable[] tranRecipients, uint256[] tranAmounts)` (external)

No description

## `transfer(struct IShared.SigData sigData, contract IERC20 token, address payable recipient, uint256 amount)` (external)

No description

## `transferBatch(struct IShared.SigData sigData, contract IERC20[] tokens, address payable[] recipients, uint256[] amounts)` (external)

No description

## `fetchDepositEth(struct IShared.SigData sigData, bytes32 swapID)` (external)

No description

## `fetchDepositEthBatch(struct IShared.SigData sigData, bytes32[] swapIDs)` (external)

No description

## `fetchDepositToken(struct IShared.SigData sigData, bytes32 swapID, contract IERC20 token)` (external)

No description

## `fetchDepositTokenBatch(struct IShared.SigData sigData, bytes32[] swapIDs, contract IERC20[] tokens)` (external)

No description

## `govWithdraw(contract IERC20[] tokens)` (external)

No description

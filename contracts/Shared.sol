pragma solidity ^0.7.0;


import "./interfaces/IShared.sol";


/**
* @title    Shared contract
* @notice   Holds constants and modifiers that are used in multiple contracts
* @dev      It would be nice if this could be a library, but modifiers can't be exported :(
* @author   Quantaf1re (James Key)
*/
contract Shared is IShared {
    /// @dev The address used to indicate whether transfer should send ETH or a token
    address constant internal _ETH_ADDR = 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE;
    address constant internal _ZERO_ADDR = address(0);
    bytes32 constant internal _NULL = "";


    /// @dev Checks that a uint isn't nonzero/empty
    modifier nzUint(uint u) {
        require(u != 0, "Vault: uint input is empty");
        _;
    }

    /// @dev Checks that an address isn't nonzero/empty
    modifier nzAddr(address a) {
        require(a != _ZERO_ADDR, "Vault: address input is empty");
        _;
    }

    /// @dev Checks that a bytes32 isn't nonzero/empty
    modifier nzBytes32(bytes32 b) {
        require(b != _NULL, "Vault: bytes32 input is empty");
        _;
    }

}
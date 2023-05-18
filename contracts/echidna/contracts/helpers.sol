// SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

interface IHevm {
    // Set block.timestamp to newTimestamp
    function warp(uint256 newTimestamp) external;

    // Set block.number to newNumber
    function roll(uint256 newNumber) external;

    // Loads a storage slot from an address
    function load(address where, bytes32 slot) external returns (bytes32);

    // Stores a value to an address' storage slot
    function store(address where, bytes32 slot, bytes32 value) external;

    // Signs data (privateKey, digest) => (r, v, s)
    function sign(
        uint256 privateKey,
        bytes32 digest
    ) external returns (uint8 r, bytes32 v, bytes32 s);

    // Gets address for a given private key
    function addr(uint256 privateKey) external returns (address addr);

    // Performs a foreign function call via terminal
    function ffi(
        string[] calldata inputs
    ) external returns (bytes memory result);

    // Performs the next smart contract call with specified `msg.sender`
    function prank(address newSender) external;
}

IHevm constant hevm = IHevm(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

function addressToString(address value) pure returns (string memory str) {
    bytes memory s = new bytes(40);
    for (uint i = 0; i < 20; i++) {
        bytes1 b = bytes1(
            uint8(uint(uint160(value)) / (2 ** (8 * (19 - i))))
        );
        bytes1 hi = bytes1(uint8(b) / 16);
        bytes1 lo = bytes1(uint8(b) - 16 * uint8(hi));
        s[2 * i] = char(hi);
        s[2 * i + 1] = char(lo);
    }
    return string(s);
}

function char(bytes1 b) pure returns (bytes1 c) {
    if (uint8(b) < 10) return bytes1(uint8(b) + 0x30);
    else return bytes1(uint8(b) + 0x57);
}

function bytesToString(bytes memory data) pure returns(string memory) {
    uint256 len = 2*data.length;
    bytes memory out = new bytes(len);
    bytes memory hexdigits = "0123456789abcdef";
    
    for (uint i = 0; i < data.length; i++) {
        out[i*2] = hexdigits[uint(uint8(data[i]) >> 4)];
        out[i*2+1] = hexdigits[uint(uint8(data[i]) & 0x0f)];
    }
    return string(out);
}


function toString(uint256 value) pure returns (string memory str) {
    /// @solidity memory-safe-assembly
    assembly {
        // The maximum value of a uint256 contains 78 digits (1 byte per digit), but we allocate 160 bytes
        // to keep the free memory pointer word aligned. We'll need 1 word for the length, 1 word for the
        // trailing zeros padding, and 3 other words for a max of 78 digits. In total: 5 * 32 = 160 bytes.
        let newFreeMemoryPointer := add(mload(0x40), 160)

        // Update the free memory pointer to avoid overriding our string.
        mstore(0x40, newFreeMemoryPointer)

        // Assign str to the end of the zone of newly allocated memory.
        str := sub(newFreeMemoryPointer, 32)

        // Clean the last word of memory it may not be overwritten.
        mstore(str, 0)

        // Cache the end of the memory to calculate the length later.
        let end := str

        // We write the string from rightmost digit to leftmost digit.
        // The following is essentially a do-while loop that also handles the zero case.
        // prettier-ignore
        for { let temp := value } 1 {} {
            // Move the pointer 1 byte to the left.
            str := sub(str, 1)

            // Write the character to the pointer.
            // The ASCII index of the '0' character is 48.
            mstore8(str, add(48, mod(temp, 10)))

            // Keep dividing temp until zero.
            temp := div(temp, 10)

                // prettier-ignore
            if iszero(temp) { break }
        }

        // Compute and cache the final total length of the string.
        let length := sub(end, str)

        // Move the pointer 32 bytes leftwards to make room for the length.
        str := sub(str, 32)

        // Store the string's length at the start of memory allocated for our string.
        mstore(str, length)
    }
}
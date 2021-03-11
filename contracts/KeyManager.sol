pragma solidity ^0.8.0;


import "./interfaces/IKeyManager.sol";
import "./abstract/SchnorrSECP256K1.sol";
import "./abstract/Shared.sol";


/**
* @title    KeyManager contract
* @notice   Holds the aggregate and governance keys, functions to update them, 
*           and isValidSig so other contracts can verify signatures and updates _lastValidateTime
* @author   Quantaf1re (James Key)
*/
contract KeyManager is SchnorrSECP256K1, Shared, IKeyManager {

    uint constant private _AGG_KEY_TIMEOUT = 2 days;

    /// @dev    Used to get the key with the keyID. This prevents isValidSig being called
    ///         by keys that aren't the aggKey or govKey, which prevents outsiders being
    ///         able to change _lastValidateTime
    mapping(KeyID => Key) private _keyIDToKey;
    /// @dev    The last time that a sig was verified (used for a dead man's switch)
    uint private _lastValidateTime;
    // Can't enable this line because the compiler errors
    // with "Constants of non-value type not yet implemented."
    // SigData private constant _NULL_SIG_DATA = SigData(0, 0);


    event KeyChange(
        bool signedByAggKey,
        Key oldKey,
        Key newKey
    );


    constructor(Key memory aggKey, Key memory govKey) {
        _keyIDToKey[KeyID.Agg] = aggKey;
        _keyIDToKey[KeyID.Gov] = govKey;
        _lastValidateTime = block.timestamp;
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                  State-changing functions                //
    //                                                          //
    //////////////////////////////////////////////////////////////

    /**
     * @notice  Checks the validity of a signature and msgHash, then updates _lastValidateTime
     * @dev     It would be nice to split this up, but these checks
     *          need to be made atomicly always. This needs to be available
     *          in this contract and in the Vault etc
     * @param contractMsgHash   The hash of the thing being signed but generated by the contract
     *                  to check it against the hash in sigData (bytes32) (here that's normally
     *                  a hash over the calldata to the function with an empty sigData)
     * @param sigData   The keccak256 hash over the msg (uint) (here that's normally
     *                  a hash over the calldata to the function with an empty sigData) and 
     *                  sig over that hash (uint) from the key input
     * @param keyID     The KeyID that indicates which key to verify the sig with. Ensures that
     *                  only 'registered' keys can be used to successfully call this fcn and change
     *                  _lastValidateTime
     * @return          Bool used by caller to be absolutely sure that the function hasn't reverted
     */
    function isValidSig(
        SigData calldata sigData,
        bytes32 contractMsgHash,
        KeyID keyID
    ) public override returns (bool) {
        Key memory key = _keyIDToKey[keyID];
        require(sigData.msgHash == uint(contractMsgHash), "KeyManager: invalid msgHash");
        require(
            verifySignature(
                sigData.msgHash,
                sigData.sig,
                key.pubKeyX,
                key.pubKeyYParity,
                key.nonceTimesGAddr
            ),
            "KeyManager: Sig invalid"
        );
        
        _lastValidateTime = block.timestamp;
        return true;
    }

    /**
     * @notice  Set a new aggregate key. Requires a signature from the current aggregate key
     * @param sigData   The keccak256 hash over the msg (uint) (which is the calldata
     *                  for this function with empty msgHash and sig) and sig over that hash
     *                  from the current aggregate key (uint)
     * @param newKey    The new aggregate key to be set. The x component of the pubkey (uint),
     *                  the parity of the y component (uint8), and the nonce times G (address)
     */
    function setAggKeyWithAggKey(
        SigData calldata sigData,
        Key calldata newKey
    ) external override nzKey(newKey) validSig(
        sigData,
        keccak256(abi.encodeWithSelector(
            this.setAggKeyWithAggKey.selector,
            SigData(0, 0),
            newKey
        )),
        KeyID.Agg
    ) {
        emit KeyChange(true, _keyIDToKey[KeyID.Agg], newKey);
        _keyIDToKey[KeyID.Agg] = newKey;
    }

    /**
     * @notice  Set a new aggregate key. Requires a signature from the current governance key
     * @param sigData   The keccak256 hash over the msg (uint) (which is the calldata
     *                  for this function with empty msgHash and sig) and sig over that hash
     *                  from the current governance key (uint)
     * @param newKey    The new aggregate key to be set. The x component of the pubkey (uint),
     *                  the parity of the y component (uint8), and the nonce times G (address)
     */
    function setAggKeyWithGovKey(
        SigData calldata sigData,
        Key calldata newKey
    ) external override nzKey(newKey) validTime validSig(
        sigData,
        keccak256(abi.encodeWithSelector(
            this.setAggKeyWithGovKey.selector,
            SigData(0, 0),
            newKey
        )),
        KeyID.Gov
    ) {
        emit KeyChange(false, _keyIDToKey[KeyID.Agg], newKey);
        _keyIDToKey[KeyID.Agg] = newKey;
    }

    /**
     * @notice  Set a new governance key. Requires a signature from the current governance key
     * @param sigData   The keccak256 hash over the msg (uint) (which is the calldata
     *                  for this function with empty msgHash and sig) and sig over that hash
     *                  from the current governance key (uint)
     * @param newKey    The new governance key to be set. The x component of the pubkey (uint),
     *                  the parity of the y component (uint8), and the nonce times G (address)
     */
    function setGovKeyWithGovKey(
        SigData calldata sigData,
        Key calldata newKey
    ) external override nzKey(newKey) validSig(
        sigData,
        keccak256(abi.encodeWithSelector(
            this.setGovKeyWithGovKey.selector,
            SigData(0, 0),
            newKey
        )),
        KeyID.Gov
    ) {
        emit KeyChange(false, _keyIDToKey[KeyID.Gov], newKey);
        _keyIDToKey[KeyID.Gov] = newKey;
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                  Non-state-changing functions            //
    //                                                          //
    //////////////////////////////////////////////////////////////


    /**
     * @notice  Get the current aggregate key
     * @return  The Key struct for the aggregate key
     */
    function getAggregateKey() external override view returns (Key memory) {
        return (_keyIDToKey[KeyID.Agg]);
    }

    /**
     * @notice  Get the current governance key
     * @return  The Key struct for the governance key
     */
    function getGovernanceKey() external override view returns (Key memory) {
        return (_keyIDToKey[KeyID.Gov]);
    }

    /**
     * @notice  Get the last time that a function was called which
                required a signature from _aggregateKeyData or _governanceKeyData
     * @return  The last time isValidSig was called, in unix time (uint)
     */
    function getLastValidateTime() external override view returns (uint) {
        return _lastValidateTime;
    }



    //////////////////////////////////////////////////////////////
    //                                                          //
    //                          Modifiers                       //
    //                                                          //
    //////////////////////////////////////////////////////////////

    /// @dev    Check that enough time has passed for setAggKeyWithGovKey. Needs
    ///         to be done as a modifier so that it can happen before validSig
    modifier validTime() {
        require(block.timestamp - _lastValidateTime >= _AGG_KEY_TIMEOUT, "KeyManager: not enough delay");
        _;
    }

    /// @dev    Call isValidSig
    modifier validSig(
        SigData calldata sigData,
        bytes32 contractMsgHash,
        KeyID keyID
    ) {
        require(isValidSig(sigData, contractMsgHash, keyID));
        _;
    }
}

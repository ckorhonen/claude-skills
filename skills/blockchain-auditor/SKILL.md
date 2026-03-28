---
name: blockchain-auditor
description: Security audit smart contracts for exploitable vulnerabilities from an unprivileged context. Use when analyzing Solidity contracts, reviewing bytecode, testing exploits on forks, or searching for ways to extract funds without owner access. Covers verified and unverified contracts, bytecode disassembly, vulnerability ranking, proof-of-concept exploit generation, DeFi protocol attacks, and cross-chain bridge security.
---

# Blockchain Security Auditor

Systematically audit smart contracts to identify exploitable vulnerabilities that allow an unprivileged account to extract funds or gain unauthorized access.

## Quick Start

```bash
# For verified contracts (Etherscan source available)
cast etherscan-source <address> --chain mainnet

# For unverified contracts (bytecode only)
cast code <address> --rpc-url $ETH_RPC_URL
cast disassemble <bytecode>

# Fork testing
forge test --fork-url $ETH_RPC_URL -vvv

# Static analysis
slither . --checklist
```

## Audit Methodology

### Phase 1: Reconnaissance

1. **Gather contract information**:
   ```bash
   # Check balance
   cast balance <address> --rpc-url $ETH_RPC_URL

   # Get bytecode
   cast code <address> --rpc-url $ETH_RPC_URL

   # Check if verified on Etherscan
   curl "https://api.etherscan.io/api?module=contract&action=getsourcecode&address=<address>&apikey=$ETHERSCAN_API_KEY"

   # Check for proxy implementation
   cast storage <address> 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc --rpc-url $ETH_RPC_URL
   ```

2. **Identify contract type**:
   - Multi-sig wallet (addOwner, execute, confirmTransaction)
   - Token contract (transfer, approve, balanceOf)
   - DeFi protocol (deposit, withdraw, swap, liquidate)
   - Lending/borrowing (Compound/Aave-style)
   - AMM/DEX (Uniswap v2/v3-style with liquidity pools)
   - Proxy pattern (EIP-1967, UUPS, Transparent, Beacon)
   - Vault/yield aggregator (ERC-4626)
   - Cross-chain bridge (lock/mint, burn/release)
   - NFT contract (ERC-721, ERC-1155)

### Phase 2: Source Code Analysis (Verified Contracts)

1. **Identify high-risk functions**:
   - `selfdestruct` / `suicide` - can drain all ETH
   - `delegatecall` - can execute arbitrary code
   - `call` with user-controlled data - arbitrary calls
   - `transfer` / `send` without checks - reentrancy
   - `withdraw` / `claim` / `redeem` - fund extraction points
   - `initialize` / `init` - proxy initialization (can it be called twice?)
   - `permit` / `permitAll` - off-chain approval bypass
   - `flash` / `flashLoan` - flash loan entry points

2. **Check access control patterns**:
   ```solidity
   // Weak patterns to look for:
   require(tx.origin == owner);     // tx.origin bypass
   require(msg.sender == owner);    // Check if owner is compromised
   // Missing modifier on sensitive function
   function withdraw() public {     // No onlyOwner!
       payable(msg.sender).transfer(address(this).balance);
   }
   // Proxy: unprotected initialize
   function initialize(address _owner) public {  // Missing initializer modifier!
       owner = _owner;
   }
   ```

3. **Known vulnerability patterns**:
   - Reentrancy (state change after external call)
   - Integer overflow/underflow (Solidity < 0.8.0)
   - Unchecked return values
   - Front-running susceptibility
   - Flash loan attacks (price manipulation in single tx)
   - Price oracle manipulation (spot vs TWAP)
   - Permit/EIP-2612 signature replay
   - ERC777 callback reentrancy
   - Read-only reentrancy (view functions misused in logic)
   - Donation attacks (token balance inflation)
   - First depositor share inflation (ERC-4626 vaults)

### Phase 3: DeFi-Specific Attack Vectors

For DeFi protocols, these vectors are highest-value and commonly exploitable:

1. **Price Oracle Manipulation**:
   ```solidity
   // Vulnerable: spot price used as oracle
   function getPrice() public view returns (uint256) {
       (uint112 reserve0, uint112 reserve1,) = IUniswapV2Pair(pool).getReserves();
       return reserve1 * 1e18 / reserve0;  // Manipulable in a single tx!
   }
   // Attack: flash loan → manipulate pool → call vulnerable function → repay
   ```
   - Check if protocol uses spot prices anywhere
   - TWAP oracles are safe; Chainlink feeds are safe (within heartbeat)
   - Look for `getReserves()`, `slot0()`, direct AMM pool queries

2. **Flash Loan Attack Surface**:
   - Can any state-changing function be called with borrowed funds?
   - Check: borrow large amount → do something → repay in same tx
   - Key question: does the protocol measure prices/balances before or after user deposits?

3. **Reentrancy Variants**:
   ```solidity
   // Cross-function reentrancy
   function withdraw() external {
       // State updated after transfer → reenter via deposit()
       IERC20(token).safeTransfer(msg.sender, amounts[msg.sender]);
       amounts[msg.sender] = 0;  // Too late!
   }

   // Read-only reentrancy (in Curve, Balancer)
   // Attack: during callback, totalSupply() returns old value
   // Another protocol reads it via getVirtualPrice() during the callback
   ```

4. **ERC-4626 Vault Inflation Attack**:
   - First depositor can inflate share price by donating tokens
   - Target: protocols that mint shares = `(deposit * totalShares) / totalAssets`
   - If `totalShares = 0`, first depositor gets `deposit` shares; then donate to inflate

5. **Signature/Permit Vulnerabilities**:
   ```solidity
   // EIP-2612 permit can be front-run
   // Front-runner takes the permit, uses it themselves before victim's tx
   // Safe if permit is used atomically in the same tx
   
   // Check: does permit use chainId? (cross-chain replay)
   // Check: does it use nonces? (replay protection)
   ```

6. **Governance/Timelock Attacks**:
   - Can governance propose and execute malicious upgrades?
   - Is there a timelock? How long?
   - Can flash loan voting power bypass quorum?

### Phase 4: Bytecode Analysis (Unverified Contracts)

1. **Disassemble bytecode**:
   ```bash
   cast disassemble <bytecode> > contract.asm
   ```

2. **Extract function selectors**:
   ```bash
   # Look for PUSH4 followed by 4 bytes
   grep -oE '63[0-9a-f]{8}' contract.asm | cut -c3-10 | sort -u
   ```

3. **Look up signatures**:
   ```bash
   curl "https://www.4byte.directory/api/v1/signatures/?hex_signature=0x<selector>"
   # Also try openchain.xyz/signature-database
   ```

4. **Identify dangerous opcodes**:
   | Opcode | Hex | Risk |
   |--------|-----|------|
   | SELFDESTRUCT | `ff` | Critical - destroys contract |
   | DELEGATECALL | `f4` | High - arbitrary code execution |
   | CALL | `f1` | Medium - external calls |
   | CALLCODE | `f2` | High - deprecated, dangerous |
   | CREATE2 | `f5` | Medium - deterministic deployment |
   | TLOAD/TSTORE | `5c/5d` | New in EIP-1153 - transient storage |

5. **Analyze control flow**:
   - Find JUMPDEST locations for function entry points
   - Trace CALLER/ORIGIN checks for access control
   - Look for SLOAD/SSTORE patterns for state access

### Phase 5: Vulnerability Ranking

Rate each finding by exploitation likelihood given current blockchain state:

| Rating | Criteria | Action |
|--------|----------|--------|
| **Critical** | Directly exploitable now, high value | Immediate PoC |
| **High** | Exploitable with specific conditions met | Fork test |
| **Medium** | Requires unlikely conditions | Document |
| **Low** | Theoretical, conditions very unlikely | Note only |

**Factors affecting likelihood**:
- Current blockchain state (owner keys, time locks, balances)
- Required preconditions (deposits, approvals, block numbers)
- Gas costs vs potential gain
- MEV/frontrunning risks (can an attacker sandwich?)
- Flashbots private mempool availability

### Phase 6: Fork Validation

1. **Set up Foundry test**:
   ```solidity
   // test/Exploit.t.sol
   pragma solidity ^0.8.20;
   import "forge-std/Test.sol";
   import "forge-std/interfaces/IERC20.sol";

   interface IFlashLoanProvider {
       function flashLoan(uint256 amount) external;
   }

   contract ExploitTest is Test {
       address target = 0x<TARGET_ADDRESS>;
       address attacker;

       function setUp() public {
           // Fork at specific block for determinism
           vm.createSelectFork(vm.envString("ETH_RPC_URL"), <BLOCK_NUMBER>);
           attacker = makeAddr("attacker");
           vm.deal(attacker, 1 ether);
       }

       function test_exploit() public {
           uint256 balanceBefore = attacker.balance;

           vm.prank(attacker);
           (bool success,) = target.call(abi.encodeWithSelector(0x<SELECTOR>));

           uint256 balanceAfter = attacker.balance;

           // CRITICAL: Verify actual fund extraction
           assertGt(balanceAfter, balanceBefore, "Exploit failed - no funds extracted");
       }

       // Flash loan exploit template
       function test_flashLoanExploit() public {
           uint256 targetBalanceBefore = IERC20(token).balanceOf(target);

           vm.prank(attacker);
           FlashLoanAttacker exploitContract = new FlashLoanAttacker(target);
           exploitContract.attack();

           assertLt(IERC20(token).balanceOf(target), targetBalanceBefore, "No drain");
           assertGt(IERC20(token).balanceOf(attacker), 0, "No profit");
       }
   }
   ```

2. **Run on fork**:
   ```bash
   forge test --fork-url $ETH_RPC_URL -vvvv --match-test "test_exploit"
   ```

3. **Verify fund extraction** (not just call success):
   - Check attacker balance increased
   - Verify target balance decreased
   - Confirm contract state changed as expected
   - **Call success does NOT mean exploit success**

### Phase 7: Report Generation

For confirmed vulnerabilities, create a report:

```markdown
# Vulnerability Report: [Contract Address]

## Summary
- **Severity**: Critical/High/Medium/Low
- **Type**: [Reentrancy/Access Control/Oracle Manipulation/etc.]
- **Impact**: [Amount at risk, what attacker gains]
- **Exploitable**: Yes/No (with current blockchain state)
- **Block confirmed**: [Block number of fork test]

## Vulnerable Function
\`\`\`solidity
function vulnerableFunction() public {
    // Vulnerable code
}
\`\`\`

## Attack Vector
1. Attacker calls function X with parameter Y
2. Contract fails to check Z
3. Funds transferred to attacker

## Proof of Concept
\`\`\`solidity
// Foundry test that demonstrates the exploit
function test_exploit() public {
    // Setup and exploit code
}
\`\`\`

## Execution Script (if confirmed)
\`\`\`bash
cast send <target> "vulnerableFunction()" --rpc-url $ETH_RPC_URL --private-key $PRIVATE_KEY
\`\`\`

## Remediation
- Add access control modifier
- Implement checks-effects-interactions pattern
- Use SafeMath for arithmetic (or upgrade to Solidity >= 0.8.0)
- Replace spot price with TWAP oracle
```

## Common Vulnerability Checklist

### Access Control
- [ ] All sensitive functions have proper modifiers
- [ ] Owner/admin addresses are not compromised
- [ ] Multi-sig requires sufficient confirmations
- [ ] Time locks are enforced
- [ ] No tx.origin authentication
- [ ] Proxy initializer cannot be called twice
- [ ] UUPS upgrade function is access-controlled
- [ ] Governance quorum cannot be bypassed with flash loans

### Reentrancy
- [ ] State changes before external calls (CEI pattern)
- [ ] ReentrancyGuard used on fund transfers
- [ ] No callbacks to untrusted contracts
- [ ] ERC-777 tokensReceived hook considered
- [ ] Cross-function reentrancy checked
- [ ] Read-only reentrancy checked (getVirtualPrice, exchange rate)

### Arithmetic (Solidity < 0.8.0)
- [ ] SafeMath used for all operations
- [ ] No unchecked blocks with user input
- [ ] Proper bounds checking
- [ ] **Check for 0.5.x - 0.6.x overflow vulnerabilities**

### Oracle / Price Manipulation
- [ ] No spot price oracles (flash-loan manipulable)
- [ ] TWAP used where applicable
- [ ] Chainlink heartbeat freshness checked
- [ ] Multi-oracle aggregation for critical paths
- [ ] Pool balances not used as price source

### Flash Loans
- [ ] State cannot be manipulated then read in same tx
- [ ] No price/ratio checks after untrusted external calls
- [ ] Reentrancy guard on all flash-loan-callable functions

### DeFi-Specific
- [ ] ERC-4626 first-depositor share inflation protected (virtual shares/assets)
- [ ] Permit/EIP-2612 replay protection (nonce, chainId)
- [ ] Donation attack protection for balance-based accounting
- [ ] MEV sandwich protection where relevant
- [ ] Cross-chain bridge: message replay protection

### External Calls
- [ ] Return values checked
- [ ] Gas limits set appropriately
- [ ] Fallback/receive functions handled

### Solidity Version-Specific Issues

| Version | Issue | Check |
|---------|-------|-------|
| < 0.8.0 | Integer overflow/underflow | SafeMath usage |
| < 0.6.0 | Constructor name confusion | `constructor()` keyword |
| < 0.5.0 | Uninitialized storage pointers | Variable declarations |
| Any | tx.origin authentication | Access control patterns |
| Any | Proxy storage collision | EIP-1967 slots used |

## False Positive Indicators

Be aware of patterns that look exploitable but aren't:

1. **Multi-sig pending transactions**: `kill()` succeeds but requires N-of-M confirmations
2. **User-specific balances**: `withdraw()` only returns caller's deposited amount
3. **Time-locked releases**: Funds go to hardcoded address, not caller
4. **Proxy patterns**: Implementation has checks even if proxy doesn't
5. **Call success without transfer**: Function completes but no ETH moves
6. **Flash loan with immediate repayment check**: Can't exploit if balance is verified at end
7. **Pausable contracts**: Admin can pause, but that's by design

**ALWAYS verify actual fund movement on fork before concluding exploitability.**

## Tools Reference

| Tool | Purpose | Command |
|------|---------|---------|
| cast | RPC calls, disassembly | `cast code/call/send/disassemble` |
| forge | Fork testing | `forge test --fork-url` |
| anvil | Local fork node | `anvil --fork-url $RPC` |
| slither | Static analysis | `slither . --checklist` |
| 4byte.directory | Selector lookup | API or web |
| openchain.xyz | Selector lookup | API or web |
| Etherscan | Source code, ABI | API or web |
| Mythril | Symbolic execution | `myth analyze` |
| Tenderly | Transaction simulation | Web UI |
| Dedaub | Decompiler for bytecode | dedaub.com |

## Environment Setup

Required environment variables:
```bash
export ETH_RPC_URL="https://eth-mainnet.g.alchemy.com/v2/<KEY>"
export ETHERSCAN_API_KEY="<KEY>"
```

Required tools:
```bash
# Foundry (forge, cast, anvil)
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Slither
pip3 install slither-analyzer

# Node.js (for Hardhat if needed)
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
```

## Example Workflow

```bash
# 1. Check contract value and code
cast balance 0x<address> --rpc-url $ETH_RPC_URL
cast code 0x<address> --rpc-url $ETH_RPC_URL > bytecode.hex

# 2. Check for proxy (EIP-1967 slot)
cast storage 0x<address> 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc --rpc-url $ETH_RPC_URL

# 3. Disassemble if unverified
cast disassemble $(cat bytecode.hex) > contract.asm

# 4. Extract and lookup selectors
grep -oE '63[0-9a-f]{8}' contract.asm | cut -c3-10 | sort -u | while read sel; do
  sig=$(curl -s "https://www.4byte.directory/api/v1/signatures/?hex_signature=0x$sel" | jq -r '.results[0].text_signature // "unknown"')
  echo "0x$sel: $sig"
done

# 5. Run slither on source (if available)
slither . --checklist 2>&1 | head -100

# 6. Create and run fork test
forge test --fork-url $ETH_RPC_URL -vvvv

# 7. Verify fund extraction (not just call success!)

# 8. Generate report if confirmed exploitable
```

## Database Integration

When auditing multiple contracts, track findings in SQLite:

```sql
CREATE TABLE contracts (
  address TEXT PRIMARY KEY,
  balance_usd REAL,
  is_verified INTEGER,
  exploitable INTEGER DEFAULT 0,
  attack_type TEXT,
  notes TEXT
);

-- Update after analysis
UPDATE contracts SET
  exploitable = 0,
  notes = 'Multi-sig wallet. kill() requires confirmations. NOT exploitable.'
WHERE address = '0x...';
```

## Security & Legal Notes

- Only test on forks, never mainnet without explicit authorization
- Document all findings, including false positives
- Consider responsible disclosure for live vulnerabilities
- Be aware of legal implications of exploit execution
- This skill is for authorized security research only
- Immunefi, Code4rena, Sherlock — report via official bug bounty channels

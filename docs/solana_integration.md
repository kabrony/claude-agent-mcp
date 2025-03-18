# OrganiX Solana Blockchain Integration

## Overview

OrganiX provides advanced blockchain integration capabilities, with a specific focus on the Solana ecosystem. This integration enables querying blockchain data, connecting with wallets, managing NFTs, and utilizing zero-knowledge proofs for privacy-preserving operations.

This document outlines the Solana integration features, explains how to use them, and provides examples of implementation in various contexts.

## Key Features

- **Solana Account Management**: Query balance, token holdings, and account information
- **NFT Support**: Find, display, and analyze NFTs on Solana
- **Phantom Wallet Integration**: Connect to Phantom wallet for authentications and transactions
- **Transaction Analysis**: Examine and interpret transaction data
- **Zero-Knowledge Proofs**: Create and verify privacy-preserving ZK proofs

## Getting Started

### Configuration

To use the Solana integration, set the following environment variables in your `.env` file:

```
SOLANA_NETWORK=mainnet-beta
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_PRIVATE_KEY=your_optional_private_key_for_signing
ENABLE_ZK_PROOFS=true
```

### Basic Usage

```python
from blockchain_integration import solana_integration, zk_proofs

# Get Solana account balance
async def check_balance(address):
    balance = await solana_integration.get_solana_balance(address)
    print(f"SOL Balance: {balance['balance']['sol']}")
    return balance

# Get NFTs owned by an address
async def get_nfts(address):
    nfts = await solana_integration.get_nfts_by_owner(address)
    print(f"Found {len(nfts['nfts'])} NFTs")
    return nfts
```

## Solana Account Management

### Getting Account Information

```python
async def get_account_info(address):
    account = await solana_integration.get_solana_account(address)
    
    if account["success"]:
        print(f"Account owner: {account['account'].get('owner')}")
        print(f"Account data size: {len(account['account'].get('data', []))}")
    else:
        print(f"Error: {account['message']}")
```

### Checking SOL Balance

```python
async def check_sol_balance(address):
    balance = await solana_integration.get_solana_balance(address)
    
    if balance["success"]:
        print(f"SOL Balance: {balance['balance']['sol']}")
        print(f"Lamports: {balance['balance']['lamports']}")
    else:
        print(f"Error: {balance['message']}")
```

### Retrieving Token Accounts

```python
async def get_token_holdings(address):
    tokens = await solana_integration.get_solana_token_accounts(address)
    
    if tokens["success"]:
        for account in tokens["token_accounts"]:
            mint = account.get("account", {}).get("data", {}).get("parsed", {}).get("info", {}).get("mint")
            amount = account.get("account", {}).get("data", {}).get("parsed", {}).get("info", {}).get("tokenAmount", {}).get("uiAmount")
            print(f"Token: {mint}, Amount: {amount}")
    else:
        print(f"Error: {tokens['message']}")
```

## NFT Integration

### Finding NFTs by Owner

```python
async def find_nfts(address):
    nfts = await solana_integration.get_nfts_by_owner(address)
    
    if nfts["success"]:
        for nft in nfts["nfts"]:
            name = nft.get("content", {}).get("metadata", {}).get("name", "Unnamed NFT")
            collection = nft.get("content", {}).get("metadata", {}).get("collection", {}).get("name", "Unknown Collection")
            print(f"NFT: {name}, Collection: {collection}")
    else:
        print(f"Error: {nfts['message']}")
```

### Displaying NFT Metadata

```python
async def show_nft_details(nft_item):
    """Display detailed information about an NFT"""
    metadata = nft_item.get("content", {}).get("metadata", {})
    attributes = metadata.get("attributes", [])
    
    print(f"Name: {metadata.get('name', 'Unnamed')}")
    print(f"Description: {metadata.get('description', 'No description')}")
    print(f"Symbol: {metadata.get('symbol', 'No symbol')}")
    print(f"Creator: {metadata.get('properties', {}).get('creators', [{}])[0].get('address', 'Unknown')}")
    
    if attributes:
        print("\nAttributes:")
        for attr in attributes:
            print(f"  {attr.get('trait_type')}: {attr.get('value')}")
```

## Phantom Wallet Integration

### Creating a Connect Button

```python
def get_wallet_connect_button(dapp_name="OrganiX", theme="dark"):
    """Generate HTML for a Phantom wallet connect button"""
    html = solana_integration.create_agent_wallet_button_html(dapp_name, theme)
    return html
```

### Generating Connection URLs

```python
def generate_connect_url(dapp_url, redirect_url=None):
    """Generate a URL for connecting to Phantom wallet"""
    result = solana_integration.generate_phantom_connection_url(dapp_url, redirect_url)
    
    if result["success"]:
        print(f"Connection URL: {result['connection_url']}")
        print(f"QR Code URL: {result['qr_code_url']}")
    else:
        print(f"Error: {result['message']}")
```

## Transaction Analysis

### Getting Recent Transactions

```python
async def get_recent_transactions(address, limit=10):
    """Get recent transactions for an address"""
    txs = await solana_integration.get_recent_solana_transactions(address, limit)
    
    if txs["success"]:
        for tx in txs["transactions"]:
            signature = tx.get("signature")
            slot = tx.get("slot")
            time = tx.get("blockTime")
            print(f"Tx: {signature}, Slot: {slot}, Time: {time}")
    else:
        print(f"Error: {txs['message']}")
```

## Zero-Knowledge Proofs

OrganiX implements several types of zero-knowledge proofs that enable privacy-preserving operations on blockchain data.

### Proof of Knowledge

```python
async def create_knowledge_proof(data):
    """Create a proof that you know some data without revealing it"""
    proof = await zk_proofs.create_proof_of_knowledge(data)
    
    if proof["success"]:
        print(f"Proof created: {proof['proof']['data_hash']}")
        return proof["proof"]
    else:
        print(f"Error: {proof['message']}")
```

### Proof of Ownership

```python
async def create_ownership_proof(address, asset_id):
    """Create a proof that you own an asset without revealing your identity"""
    proof = await zk_proofs.create_proof_of_ownership(address, asset_id)
    
    if proof["success"]:
        print(f"Proof created: {proof['proof']['asset_hash']}")
        return proof["proof"]
    else:
        print(f"Error: {proof['message']}")
```

### Verifying Proofs

```python
def verify_proof(proof):
    """Verify a ZK proof"""
    result = zk_proofs.verify_proof(proof)
    
    if result["success"]:
        if result["verified"]:
            print("Proof verified successfully")
        else:
            print("Proof verification failed")
    else:
        print(f"Error: {result['message']}")
```

## Advanced Use Cases

### Multi-Account Portfolio Analysis

```python
async def analyze_portfolio(addresses):
    """Analyze a portfolio across multiple Solana addresses"""
    total_sol = 0
    total_tokens = 0
    total_nfts = 0
    
    for address in addresses:
        # Get SOL balance
        balance = await solana_integration.get_solana_balance(address)
        if balance["success"]:
            total_sol += balance["balance"]["sol"]
            
        # Get token accounts
        tokens = await solana_integration.get_solana_token_accounts(address)
        if tokens["success"]:
            total_tokens += len(tokens["token_accounts"])
            
        # Get NFTs
        nfts = await solana_integration.get_nfts_by_owner(address)
        if nfts["success"]:
            total_nfts += len(nfts["nfts"])
    
    print(f"Portfolio Summary:")
    print(f"Total SOL: {total_sol}")
    print(f"Total Token Types: {total_tokens}")
    print(f"Total NFTs: {total_nfts}")
```

### Privacy-Preserving Verification

```python
async def verify_asset_ownership_privately(user_address, asset_id, verifier_function):
    """Verify asset ownership without revealing the user's address"""
    # Create a ZK proof of ownership
    proof = await zk_proofs.create_proof_of_ownership(user_address, asset_id)
    
    if not proof["success"]:
        return {"success": False, "message": "Failed to create proof"}
    
    # The verifier can check the proof without knowing the address
    verification = verifier_function(proof["proof"])
    
    return {
        "success": True,
        "verification_result": verification,
        "proof": proof["proof"]
    }
```

## Integration with Agent System

The Solana integration works seamlessly with the OrganiX multi-agent system:

### Blockchain Specialist Agent

```python
# Initialize the blockchain specialist agent
blockchain_agent = coordinator.agents.get("blockchain")

if blockchain_agent:
    # Process blockchain-related queries through the specialized agent
    result = await coordinator.process_with_agent(
        "blockchain", 
        "What are the top NFT collections on Solana right now?"
    )
    print(result["response"])
```

### Tool Registration with MCP

```python
# Register Solana tools with MCP Manager
mcp.register_tool(
    "get_sol_balance",
    "Get the SOL balance for a Solana address",
    solana_integration.get_solana_balance
)

mcp.register_tool(
    "get_nfts",
    "Get NFTs owned by a Solana address",
    solana_integration.get_nfts_by_owner
)
```

## Web Dashboard Integration

The Solana integration includes components for web dashboard integration:

### Wallet Connect Button

```html
<div class="wallet-section">
    <!-- Generated by solana_integration.create_agent_wallet_button_html() -->
    <button 
        class="phantom-button phantom-button-dark" 
        onclick="window.open('https://phantom.app/ul/v1/connect?app_url=OrganiX%20Dashboard', '_blank')">
        <img src="https://phantom.app/img/logo.png" alt="Phantom" width="20" height="20">
        Connect to Phantom
    </button>
</div>
```

### NFT Display Grid

```html
<!-- NFT Display Example -->
<div class="nft-grid">
    <div class="nft-card">
        <img src="https://arweave.net/example_nft_image" alt="NFT Image">
        <h3>Example NFT</h3>
        <p>Collection: Example Collection</p>
    </div>
    <!-- More NFT cards -->
</div>
```

## Troubleshooting

### Common Issues

1. **RPC Connection Failures**
   - **Problem**: Unable to connect to Solana RPC
   - **Solution**: Check your SOLANA_RPC_URL and ensure you have internet connectivity

2. **Rate Limiting**
   - **Problem**: Too many RPC requests leading to rate limiting
   - **Solution**: Implement caching and pagination for large data requests

3. **Invalid Address Format**
   - **Problem**: Solana address format is incorrect
   - **Solution**: Validate addresses before sending to the API, ensure they're base58 encoded

4. **ZK Proof Creation Failures**
   - **Problem**: Zero-knowledge proofs fail to generate
   - **Solution**: Ensure ENABLE_ZK_PROOFS=true in your environment and check input data formats

## Best Practices

1. **Cache Blockchain Data**: Minimize RPC calls by caching results that don't change frequently
2. **Use Pagination**: For large datasets like NFT collections, implement pagination
3. **Handle Rate Limits**: Implement exponential backoff for RPC request retries
4. **Secure Private Keys**: Never expose private keys in client-side code or logs
5. **Validate Inputs**: Always validate addresses and other inputs before sending to blockchain APIs

## Conclusion

The OrganiX Solana integration provides comprehensive capabilities for interacting with the Solana blockchain ecosystem. By combining these features with the advanced agent architecture, you can create sophisticated applications that leverage blockchain data, wallet connections, and privacy-preserving operations to deliver powerful user experiences.

Through the Model Context Protocol (MCP), these capabilities are accessible to the broader agent system, allowing for seamless integration of blockchain functionality into complex workflows and interactions.

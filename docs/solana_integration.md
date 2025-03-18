# OrganiX Solana Integration

## Overview

OrganiX features comprehensive integration with the Solana blockchain, providing capabilities for wallet connectivity, balance checking, token management, NFT interactions, and zero-knowledge operations. This document details how to leverage these features in your applications.

## Table of Contents

1. [Setup and Configuration](#setup-and-configuration)
2. [Basic Operations](#basic-operations)
3. [Phantom Wallet Integration](#phantom-wallet-integration)
4. [NFT Operations](#nft-operations)
5. [Zero-Knowledge Integration](#zero-knowledge-integration)
6. [Solana Tool Suite](#solana-tool-suite)
7. [Usage Examples](#usage-examples)
8. [Security Considerations](#security-considerations)

## Setup and Configuration

### Environment Variables

Configure your `.env` file with the following Solana-related variables:

```
# Solana Configuration
SOLANA_NETWORK=mainnet-beta
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_PRIVATE_KEY=your_base64_encoded_private_key

# Zero-Knowledge Proofs
ENABLE_ZK_PROOFS=true
```

### Import and Initialization

```python
# Import components
from blockchain_integration import solana_integration, zk_proofs

# Check if blockchain features are available
if solana_integration.solana_configured:
    print("Solana integration is ready")
else:
    print("Solana integration not configured")
```

## Basic Operations

### Get Account Balance

```python
# Get SOL balance for an address
address = "FxsqrtTMuAKYgNwiGRD3FwVr1FtsrfUJMPWq49dZVERP"
balance = await solana_integration.get_solana_balance(address)

# Access balance in SOL
sol_amount = balance["balance"]["sol"]
print(f"Balance: {sol_amount} SOL")
```

### Get Token Accounts

```python
# Get token accounts for an address
token_accounts = await solana_integration.get_solana_token_accounts(address)

# Process token accounts
for account in token_accounts["token_accounts"]:
    mint = account["account"]["data"]["parsed"]["info"]["mint"]
    amount = account["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"]
    print(f"Token: {mint}, Amount: {amount}")
```

### Get Recent Transactions

```python
# Get recent transactions for an address
transactions = await solana_integration.get_recent_solana_transactions(address, limit=5)

# Process transactions
for tx in transactions["transactions"]:
    signature = tx["signature"]
    timestamp = tx["blockTime"]
    print(f"Transaction: {signature}, Time: {timestamp}")
```

## Phantom Wallet Integration

### Generate Connection URL

```python
# Generate URL for connecting to Phantom
connection_info = solana_integration.generate_phantom_connection_url(
    dapp_url="https://myapp.com",
    redirect_url="https://myapp.com/callback"
)

connection_url = connection_info["connection_url"]
qr_code_url = connection_info["qr_code_url"]
```

### Create Connect Button

```python
# Generate HTML for a Phantom wallet connect button
button_html = solana_integration.create_agent_wallet_button_html(
    dapp_name="OrganiX Dashboard",
    theme="dark"  # or "light"
)

# Use the HTML in your web application
print(button_html)
```

### Connection Workflow

The typical Phantom wallet connection workflow is:

1. Generate and display the connection URL or button
2. User clicks the button to open Phantom wallet
3. User approves the connection in their wallet
4. Phantom redirects back to your application
5. Your application receives the user's public key

## NFT Operations

### Get NFTs by Owner

```python
# Get NFTs owned by an address
nfts = await solana_integration.get_nfts_by_owner(address)

# Process NFT information
for nft in nfts["nfts"]:
    name = nft.get("content", {}).get("metadata", {}).get("name", "Unnamed NFT")
    collection = nft.get("grouping", [{}])[0].get("group_value", "No collection")
    print(f"NFT: {name}, Collection: {collection}")
```

### NFT Metadata Retrieval

The NFT data includes:

- Basic information (name, symbol, description)
- Content (image URL, animation URL, metadata)
- Royalty information
- Creator details
- Collection information

Example accessing metadata:

```python
nft = nfts["nfts"][0]  # First NFT
name = nft.get("content", {}).get("metadata", {}).get("name")
image = nft.get("content", {}).get("links", {}).get("image")
description = nft.get("content", {}).get("metadata", {}).get("description")
```

## Zero-Knowledge Integration

OrganiX includes zero-knowledge proof functionality for privacy-preserving operations.

### Creating Proofs

```python
# Create a proof of knowledge (knowing data without revealing it)
knowledge_proof = await zk_proofs.create_proof_of_knowledge("sensitive data")

# Create a proof of ownership (owning an asset without revealing identity)
ownership_proof = await zk_proofs.create_proof_of_ownership(
    address="your_wallet_address",
    asset_id="asset_identifier"
)
```

### Verifying Proofs

```python
# Verify a proof
verification = zk_proofs.verify_proof(proof)

if verification["verified"]:
    print("Proof is valid")
else:
    print("Proof is invalid")
```

### ZK Applications

Zero-knowledge proofs can be used for:

1. **Private Transactions**: Prove a transaction occurred without revealing details
2. **Identity Verification**: Prove you own an address without revealing it
3. **Age Verification**: Prove you're over a certain age without revealing birthdate
4. **Asset Ownership**: Prove you own an asset without revealing your identity
5. **Credential Verification**: Prove you have credentials without revealing them

## Solana Tool Suite

OrganiX registers several Solana-related tools with the MCP system:

| Tool Name | Description |
|-----------|-------------|
| `get_solana_balance` | Get SOL balance for an address |
| `get_solana_token_accounts` | Get token accounts for an address |
| `get_nfts_by_owner` | Get NFTs owned by an address |
| `get_recent_solana_transactions` | Get recent transactions for an address |
| `create_zk_proof` | Create a zero-knowledge proof |
| `verify_zk_proof` | Verify a zero-knowledge proof |

These tools can be accessed via the MultiAgentCoordinator:

```python
# Get blockchain data through the coordinator
result = await coordinator.get_blockchain_data(address)

# Get Phantom connect button
button_html = coordinator.get_phantom_connect_html()

# Create and verify ZK proofs
proof = await coordinator.create_zero_knowledge_proof("knowledge", data)
verification = await coordinator.verify_zero_knowledge_proof(proof)
```

## Usage Examples

### Creating a Wallet Dashboard

```python
async def create_wallet_dashboard(address):
    # Get data in parallel
    balance_task = solana_integration.get_solana_balance(address)
    tokens_task = solana_integration.get_solana_token_accounts(address)
    nfts_task = solana_integration.get_nfts_by_owner(address)
    transactions_task = solana_integration.get_recent_solana_transactions(address, limit=10)
    
    # Wait for all tasks to complete
    balance = await balance_task
    tokens = await tokens_task
    nfts = await nfts_task
    transactions = await transactions_task
    
    # Create dashboard data
    dashboard = {
        "address": address,
        "sol_balance": balance["balance"]["sol"],
        "token_count": len(tokens["token_accounts"]),
        "tokens": tokens["token_accounts"],
        "nft_count": len(nfts["nfts"]),
        "nfts": nfts["nfts"],
        "recent_transactions": transactions["transactions"]
    }
    
    return dashboard
```

### Privacy-Preserving Verification

```python
async def verify_nft_ownership_privately(address, collection_id):
    # Get NFTs owned by the address
    nfts = await solana_integration.get_nfts_by_owner(address)
    
    # Check if any NFT belongs to the collection
    owned_nfts = [
        nft for nft in nfts["nfts"]
        if nft.get("grouping", [{}])[0].get("group_value") == collection_id
    ]
    
    if owned_nfts:
        # Create a zero-knowledge proof of ownership
        proof = await zk_proofs.create_proof_of_ownership(
            address=address,
            asset_id=owned_nfts[0]["id"]
        )
        
        return {
            "owns_nft": True,
            "proof": proof,
            "collection": collection_id
        }
    else:
        return {
            "owns_nft": False
        }
```

## Security Considerations

1. **Private Key Management**: Never expose private keys in code or logs
2. **RPC Endpoint Security**: Use secure, authenticated RPC endpoints
3. **Input Validation**: Validate all blockchain addresses before processing
4. **Rate Limiting**: Implement rate limiting for RPC calls
5. **Error Handling**: Properly handle and log blockchain errors
6. **User Consent**: Always get user consent before accessing wallet data
7. **ZK Security**: Understand the limitations of ZK proofs in your application

Remember that blockchain operations are public and permanent. Always prioritize security and privacy in your implementations.

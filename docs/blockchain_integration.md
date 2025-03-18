# OrganiX Blockchain Integration

## Solana and Zero-Knowledge Technology Integration

This guide provides detailed information about OrganiX's integration with Solana blockchain and zero-knowledge technologies.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Setup and Configuration](#setup-and-configuration)
4. [Phantom Wallet Integration](#phantom-wallet-integration)
5. [Solana Data Access](#solana-data-access)
6. [NFT Integration](#nft-integration)
7. [Zero-Knowledge Proofs](#zero-knowledge-proofs)
8. [Agent Capabilities](#agent-capabilities)
9. [Security Considerations](#security-considerations)
10. [Advanced Usage](#advanced-usage)

## Overview

OrganiX includes comprehensive blockchain integration focused on the Solana ecosystem, providing:

- Real-time Solana blockchain data access
- Phantom wallet integration with secure connection flows
- NFT discovery and analysis
- Zero-knowledge proof creation and verification
- Dedicated blockchain specialist agent

This integration allows developers to build AI-powered applications that can interact with blockchain data while maintaining privacy and security.

## Features

### Solana Integration

- **Account Information**: Access account data, balances, and history
- **Token Discovery**: Identify and analyze SPL tokens
- **NFT Integration**: Discover and analyze NFT collections
- **Transaction Monitoring**: Track and analyze on-chain activity

### Zero-Knowledge Features

- **Proof of Knowledge**: Create ZK proofs to demonstrate knowledge without revealing information
- **Proof of Ownership**: Verify asset ownership without exposing identity
- **Verification**: Secure verification of ZK proofs
- **Privacy-Preserving Operations**: Maintain privacy while confirming information

### Wallet Integration

- **Phantom Connection**: Connect to Phantom wallet with QR codes or deep links
- **Wallet Authentication**: Authenticate via wallet signatures
- **Multi-Wallet Support**: Support multiple wallet connections

## Setup and Configuration

### Environment Variables

Add the following to your `.env` file:

```
# Solana Configuration
SOLANA_NETWORK=mainnet-beta
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_PRIVATE_KEY=optional_private_key_for_signing

# Zero-Knowledge Configuration
ENABLE_ZK_PROOFS=true
```

### RPC Providers

For production use, consider using one of these RPC providers:

- [Helius](https://helius.xyz/) - Recommended for NFT data
- [QuickNode](https://www.quicknode.com/) - Good all-purpose provider
- [Alchemy](https://www.alchemy.com/) - Enterprise-grade provider

### Installation

The blockchain integration requires the following dependencies:

```
# Already included in requirements.txt
aiohttp==3.9.1
nacl==1.4.0
base58==2.1.1
```

## Phantom Wallet Integration

### Connection Button

Use the provided function to generate a Phantom wallet connection button:

```python
from blockchain_integration import solana_integration

# Generate HTML for wallet connection
wallet_html = solana_integration.create_agent_wallet_button_html(
    dapp_name="OrganiX Agent",
    theme="dark"  # or "light"
)

# Use in web app
print(wallet_html)
```

The generated button will look like:

```
[Phantom Logo] Connect to Phantom
```

### Connection Flow

The connection process works as follows:

1. User clicks the connect button
2. Phantom wallet opens (browser extension or mobile app)
3. User approves the connection
4. The application receives the connected wallet address
5. The agent can then access on-chain data for this address

### QR Code Generation

For mobile connections, generate a QR code:

```python
# Get connection details including QR code URL
connection_info = solana_integration.generate_phantom_connection_url(
    dapp_url="https://your-app-url.com",
    redirect_url="https://your-app-url.com/callback"
)

qr_code_url = connection_info["qr_code_url"]
```

## Solana Data Access

### Account Information

```python
from blockchain_integration import solana_integration

# Get account information
async def get_account_data(address):
    account_info = await solana_integration.get_solana_account(address)
    
    if account_info["success"]:
        # Access account data
        program_id = account_info["account"].get("owner")
        data = account_info["account"].get("data")
        
        return {
            "program_id": program_id,
            "data": data
        }
    else:
        print(f"Error: {account_info.get('message')}")
        return None
```

### Balance Checking

```python
# Get SOL balance
async def get_sol_balance(address):
    balance_info = await solana_integration.get_solana_balance(address)
    
    if balance_info["success"]:
        # Access balance in SOL
        sol_balance = balance_info["balance"]["sol"]
        lamports = balance_info["balance"]["lamports"]
        
        return {
            "sol": sol_balance,
            "lamports": lamports
        }
    else:
        print(f"Error: {balance_info.get('message')}")
        return None
```

### Token Accounts

```python
# Get token accounts owned by an address
async def get_tokens(address):
    tokens_info = await solana_integration.get_solana_token_accounts(address)
    
    if tokens_info["success"]:
        token_accounts = tokens_info["token_accounts"]
        
        # Extract token info
        token_details = []
        for account in token_accounts:
            parsed_info = account.get("account", {}).get("data", {}).get("parsed", {}).get("info", {})
            mint = parsed_info.get("mint")
            token_amount = parsed_info.get("tokenAmount", {})
            
            token_details.append({
                "mint": mint,
                "amount": token_amount.get("uiAmount"),
                "decimals": token_amount.get("decimals")
            })
            
        return token_details
    else:
        print(f"Error: {tokens_info.get('message')}")
        return []
```

### Transaction History

```python
# Get recent transactions
async def get_transactions(address, limit=10):
    tx_info = await solana_integration.get_recent_solana_transactions(address, limit)
    
    if tx_info["success"]:
        transactions = tx_info["transactions"]
        
        # Process transactions
        tx_summaries = []
        for tx in transactions:
            tx_summaries.append({
                "signature": tx.get("signature"),
                "slot": tx.get("slot"),
                "timestamp": tx.get("blockTime"),
                "status": "confirmed" if tx.get("confirmationStatus") == "confirmed" else "pending"
            })
            
        return tx_summaries
    else:
        print(f"Error: {tx_info.get('message')}")
        return []
```

## NFT Integration

### NFT Discovery

```python
# Get NFTs owned by an address
async def get_nfts(address):
    nft_info = await solana_integration.get_nfts_by_owner(address)
    
    if nft_info["success"]:
        nfts = nft_info["nfts"]
        
        # Process NFT information
        nft_details = []
        for nft in nfts:
            content = nft.get("content", {})
            
            nft_details.append({
                "name": nft.get("name"),
                "mint": nft.get("id"),
                "collection": nft.get("grouping", [{}])[0].get("group_value"),
                "image": content.get("files", [{}])[0].get("uri") if content.get("files") else None
            })
            
        return nft_details
    else:
        print(f"Error: {nft_info.get('message')}")
        return []
```

### NFT Analysis

The blockchain specialist agent can analyze NFTs for:

- Collection membership
- Rarity scores and traits
- Historical ownership
- Marketplace listings

```python
from advanced_chat import coordinator

# Analyze an NFT
async def analyze_nft(mint_address):
    query = f"Analyze the NFT with mint address {mint_address}. What collection is it from, what are its traits, and is it currently listed on any marketplaces?"
    
    result = await coordinator.process_with_agent("blockchain", query)
    return result["response"]
```

## Zero-Knowledge Proofs

### Creating Proofs

```python
from blockchain_integration import zk_proofs

# Create a proof of knowledge
async def create_knowledge_proof(secret_data):
    """Create a proof that you know some data without revealing it"""
    proof_result = await zk_proofs.create_proof_of_knowledge(secret_data)
    
    if proof_result["success"]:
        proof = proof_result["proof"]
        return proof
    else:
        print(f"Error: {proof_result.get('message')}")
        return None

# Create a proof of asset ownership
async def create_ownership_proof(address, asset_id):
    """Create a proof that you own an asset without revealing your identity"""
    proof_result = await zk_proofs.create_proof_of_ownership(address, asset_id)
    
    if proof_result["success"]:
        proof = proof_result["proof"]
        return proof
    else:
        print(f"Error: {proof_result.get('message')}")
        return None
```

### Verifying Proofs

```python
# Verify a zero-knowledge proof
def verify_proof(proof, public_input=None):
    """Verify a zero-knowledge proof"""
    verification = zk_proofs.verify_proof(proof, public_input)
    
    if verification["success"]:
        if verification["verified"]:
            return True
        else:
            print("Proof verification failed")
            return False
    else:
        print(f"Error: {verification.get('message')}")
        return False
```

## Agent Capabilities

The OrganiX blockchain specialist agent can:

### Information Tasks

- Explain blockchain concepts
- Analyze tokens and NFTs
- Interpret transaction history
- Provide market insights
- Explain technical concepts

### Data Tasks

- Retrieve on-chain data
- Track balances and holdings
- Monitor transaction activity
- Discover and analyze NFTs
- Verify proofs and signatures

Example usage:

```python
from advanced_chat import coordinator

# Use blockchain specialist agent
async def blockchain_query(question):
    result = await coordinator.process_with_agent("blockchain", question)
    return result["response"]
    
# Example questions
questions = [
    "What is the current SOL price?",
    "Explain how Solana achieves high throughput",
    "What are the top NFT collections on Solana?",
    "How do zero-knowledge proofs work?",
    "Explain the Phantom wallet connection process"
]
```

## Security Considerations

### Key Management

- **Never** store private keys in code repositories
- Use environment variables or secure key management services
- Consider using wallet connections rather than private keys

### RPC Security

- Use HTTPS for all RPC connections
- Implement rate limiting to prevent abuse
- Consider using dedicated API keys for production

### Zero-Knowledge Best Practices

- Remember that ZK proofs are simulated in this implementation
- For production use, use established ZK libraries like `libsnark` or `circom`
- Test proof verification thoroughly before relying on it

## Advanced Usage

### Custom RPC Methods

You can extend the Solana integration with custom RPC methods:

```python
async def custom_rpc_call(method, params):
    """Make a custom RPC call to Solana"""
    if not solana_integration.solana_configured:
        return {
            "success": False,
            "message": "Solana RPC URL not configured"
        }
        
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(solana_integration.solana_rpc_url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "result": result.get("result")
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "message": f"RPC request failed with status {response.status}: {error_text}"
                    }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error making RPC call: {str(e)}"
        }
```

### Program Data Parsing

For smart contract (program) data parsing:

```python
import base64
import struct

def parse_program_data(encoded_data, format_str):
    """Parse binary program data"""
    if not encoded_data:
        return None
        
    # Remove metadata indicator if present
    data = encoded_data
    if isinstance(data, list) and len(data) > 0:
        data = data[0]
        
    # Decode base64
    try:
        binary_data = base64.b64decode(data)
        
        # Unpack using struct format string
        unpacked = struct.unpack(format_str, binary_data)
        return unpacked
    except Exception as e:
        print(f"Error parsing program data: {str(e)}")
        return None
```

### Advanced ZK Applications

Ideas for advanced zero-knowledge applications:

1. **Private Voting**: Implement anonymous voting while ensuring only eligible participants vote
2. **Confidential Transactions**: Create transactions that hide sender, receiver, or amount
3. **Identity Verification**: Verify identity attributes without revealing personal information
4. **Anonymous Authentication**: Authenticate users without tracking their identity
5. **Compliance Proof**: Demonstrate regulatory compliance without revealing sensitive data

"""
Blockchain Integration - Handles connections to blockchain networks
Supports Solana and agent capabilities with Phantom wallet integration
"""
import os
import json
import asyncio
import aiohttp
import base64
import time
from datetime import datetime
import nacl.signing
from nacl.encoding import Base64Encoder
from dotenv import load_dotenv
from utils import log

# Load environment variables
load_dotenv()

class SolanaIntegration:
    def __init__(self):
        # Solana configuration
        self.solana_network = os.getenv("SOLANA_NETWORK", "mainnet-beta")
        self.solana_rpc_url = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
        self.solana_private_key = os.getenv("SOLANA_PRIVATE_KEY")
        
        # Phantom wallet integration
        self.phantom_api_url = "https://phantom.app/api"
        
        # Check if configured
        self.solana_configured = bool(self.solana_rpc_url)
        
        # Warn if not configured
        if not self.solana_configured:
            log.warning("Solana RPC URL not configured. Some blockchain features will be disabled.")
            
        # Initialize keypair if available
        self.keypair = None
        if self.solana_private_key:
            try:
                seed = base64.b64decode(self.solana_private_key)
                self.signing_key = nacl.signing.SigningKey(seed)
                self.public_key = self.signing_key.verify_key.encode(encoder=Base64Encoder).decode('utf-8')
                log.info(f"Initialized Solana keypair with public key: {self.public_key}")
            except Exception as e:
                log.error(f"Failed to initialize Solana keypair: {str(e)}")
                self.keypair = None
        
    async def get_solana_account(self, address):
        """Get Solana account information"""
        if not self.solana_configured:
            return {
                "success": False,
                "message": "Solana RPC URL not configured"
            }
            
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [
                address,
                {
                    "encoding": "jsonParsed"
                }
            ]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.solana_rpc_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "account": result.get("result", {}).get("value", {})
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
                "message": f"Error getting Solana account: {str(e)}"
            }
            
    async def get_solana_balance(self, address):
        """Get SOL balance for an address"""
        if not self.solana_configured:
            return {
                "success": False,
                "message": "Solana RPC URL not configured"
            }
            
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [address]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.solana_rpc_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        # Convert lamports to SOL (1 SOL = 10^9 lamports)
                        lamports = result.get("result", {}).get("value", 0)
                        sol = lamports / 1_000_000_000
                        return {
                            "success": True,
                            "balance": {
                                "lamports": lamports,
                                "sol": sol
                            }
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
                "message": f"Error getting Solana balance: {str(e)}"
            }
            
    async def get_solana_token_accounts(self, owner_address):
        """Get token accounts owned by an address"""
        if not self.solana_configured:
            return {
                "success": False,
                "message": "Solana RPC URL not configured"
            }
            
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                owner_address,
                {
                    "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
                },
                {
                    "encoding": "jsonParsed"
                }
            ]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.solana_rpc_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "token_accounts": result.get("result", {}).get("value", [])
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
                "message": f"Error getting token accounts: {str(e)}"
            }
            
    def generate_phantom_connection_url(self, dapp_url, redirect_url):
        """Generate a URL for connecting to Phantom wallet"""
        if not dapp_url:
            return {
                "success": False,
                "message": "dApp URL is required"
            }
            
        connection_url = f"https://phantom.app/ul/v1/connect?app_url={dapp_url}"
        
        if redirect_url:
            connection_url += f"&redirect_url={redirect_url}"
            
        return {
            "success": True,
            "connection_url": connection_url,
            "qr_code_url": f"https://phantom.app/ul/v1/qr?type=connect&app_url={dapp_url}"
        }
        
    async def get_nfts_by_owner(self, owner_address):
        """Get NFTs owned by an address"""
        if not self.solana_configured:
            return {
                "success": False,
                "message": "Solana RPC URL not configured"
            }
            
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAssetsByOwner",
            "params": [
                owner_address,
                {
                    "page": 1,
                    "limit": 10
                }
            ]
        }
        
        try:
            # Use DAS API for NFT metadata
            das_url = "https://mainnet.helius-rpc.com/?api-key=15339bd9-b84a-4bcb-b7c1-aa4e98b427ec"
            async with aiohttp.ClientSession() as session:
                async with session.post(das_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "nfts": result.get("result", {}).get("items", [])
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "message": f"DAS request failed with status {response.status}: {error_text}"
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting NFTs: {str(e)}"
            }
            
    def create_agent_wallet_button_html(self, dapp_name="OrganiX", theme="dark"):
        """Create HTML for a Phantom wallet connect button"""
        html = f"""
        <button 
            class="phantom-button phantom-button-{theme}" 
            onclick="window.open('{self.generate_phantom_connection_url(dapp_name, '')['connection_url']}', '_blank')">
            <img src="https://phantom.app/img/logo.png" alt="Phantom" width="20" height="20">
            Connect to Phantom
        </button>
        <style>
            .phantom-button {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                padding: 10px 16px;
                border-radius: 8px;
                font-family: 'Inter', sans-serif;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                border: none;
            }}
            .phantom-button-dark {{
                background-color: #4e44ce;
                color: white;
            }}
            .phantom-button-dark:hover {{
                background-color: #3c32b5;
            }}
            .phantom-button-light {{
                background-color: #e9e9fb;
                color: #4e44ce;
            }}
            .phantom-button-light:hover {{
                background-color: #d8d8f6;
            }}
        </style>
        """
        return html
        
    async def get_recent_solana_transactions(self, address, limit=10):
        """Get recent transactions for an address"""
        if not self.solana_configured:
            return {
                "success": False,
                "message": "Solana RPC URL not configured"
            }
            
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [
                address,
                {
                    "limit": limit
                }
            ]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.solana_rpc_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "transactions": result.get("result", [])
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
                "message": f"Error getting transactions: {str(e)}"
            }

class ZeroKnowledgeProofs:
    def __init__(self):
        # ZK circuit configuration
        self.zk_enabled = os.getenv("ENABLE_ZK_PROOFS", "false").lower() == "true"
        
        if not self.zk_enabled:
            log.warning("Zero-Knowledge proofs are disabled. Set ENABLE_ZK_PROOFS=true to enable.")
            
    async def create_proof_of_knowledge(self, data, options=None):
        """Create a ZK proof that you know some data without revealing it"""
        if not self.zk_enabled:
            return {
                "success": False,
                "message": "Zero-Knowledge proofs are disabled"
            }
        
        try:
            # Simulate ZK proof generation
            # In a real implementation, this would use a library like circom or snarkjs
            simulated_proof = {
                "proof_type": "knowledge",
                "data_hash": self._hash_data(data),
                "timestamp": time.time(),
                "verified": True
            }
            
            return {
                "success": True,
                "proof": simulated_proof
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating proof: {str(e)}"
            }
    
    async def create_proof_of_ownership(self, address, asset_id):
        """Create a ZK proof that you own an asset without revealing your identity"""
        if not self.zk_enabled:
            return {
                "success": False,
                "message": "Zero-Knowledge proofs are disabled"
            }
            
        try:
            # Simulate ZK proof generation
            simulated_proof = {
                "proof_type": "ownership",
                "asset_hash": self._hash_data(asset_id),
                "timestamp": time.time(),
                "verified": True
            }
            
            return {
                "success": True,
                "proof": simulated_proof
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating proof: {str(e)}"
            }
    
    def _hash_data(self, data):
        """Create a hash of data (simulated for now)"""
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        elif not isinstance(data, str):
            data = str(data)
            
        # In a real implementation, use a cryptographic hash function
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()
        
    def verify_proof(self, proof, public_input=None):
        """Verify a ZK proof"""
        if not self.zk_enabled:
            return {
                "success": False,
                "message": "Zero-Knowledge proofs are disabled"
            }
            
        # Simulated verification
        # In a real implementation, this would use a ZK verification algorithm
        if proof and isinstance(proof, dict) and proof.get("verified", False):
            return {
                "success": True,
                "verified": True
            }
        else:
            return {
                "success": True,
                "verified": False,
                "message": "Invalid proof"
            }

# Initialize global instances
solana_integration = SolanaIntegration()
zk_proofs = ZeroKnowledgeProofs()

async def test_solana():
    """Test Solana integration with a known address"""
    # Test with Phantom's team wallet
    test_address = "FxsqrtTMuAKYgNwiGRD3FwVr1FtsrfUJMPWq49dZVERP"
    
    print("Testing Solana integration...")
    balance = await solana_integration.get_solana_balance(test_address)
    print(f"Balance: {json.dumps(balance, indent=2)}")
    
    token_accounts = await solana_integration.get_solana_token_accounts(test_address)
    token_count = len(token_accounts.get("token_accounts", []))
    print(f"Found {token_count} token accounts")
    
    nfts = await solana_integration.get_nfts_by_owner(test_address)
    nft_count = len(nfts.get("nfts", []))
    print(f"Found {nft_count} NFTs")
    
    return {
        "balance": balance,
        "token_count": token_count,
        "nft_count": nft_count
    }

if __name__ == "__main__":
    # Test Solana integration when run directly
    asyncio.run(test_solana())

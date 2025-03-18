"""
Social Media Integrations - Manages connections to social platforms
"""
import os
import json
import asyncio
import aiohttp
import time
import hashlib
import hmac
import base64
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv
from utils import log

# Load environment variables
load_dotenv()

class TwitterIntegration:
    def __init__(self):
        """Initialize Twitter integration"""
        # Load credentials from environment
        self.twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.twitter_api_key = os.getenv("TWITTER_API_KEY")
        self.twitter_api_secret = os.getenv("TWITTER_API_SECRET")
        self.twitter_access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.twitter_access_secret = os.getenv("TWITTER_ACCESS_SECRET")
        
        # Twitter API v2 base URL
        self.base_url = "https://api.twitter.com/2"
        
        # Check if configured
        self.is_configured = bool(self.twitter_bearer_token or (self.twitter_api_key and self.twitter_api_secret))
        
        # Cache for user information
        self.user_cache = {}
        
        if not self.is_configured:
            log.warning("Twitter API credentials not found in environment variables.")
            log.info("Set TWITTER_BEARER_TOKEN or TWITTER_API_KEY and TWITTER_API_SECRET in .env file to enable Twitter integration.")
    
    async def get_user_by_username(self, username, force_refresh=False):
        """Get Twitter user information by username"""
        # Check cache first
        if not force_refresh and username in self.user_cache:
            return self.user_cache[username]
            
        if not self.is_configured:
            return {
                "success": False,
                "message": "Twitter API credentials not configured"
            }
            
        headers = {"Authorization": f"Bearer {self.twitter_bearer_token}"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/users/by/username/{username}?user.fields=description,profile_image_url,public_metrics,verified",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        # Cache results
                        self.user_cache[username] = {
                            "success": True,
                            "user": result.get("data", {})
                        }
                        return self.user_cache[username]
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "message": f"API request failed with status {response.status}: {error_text}"
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error fetching Twitter user: {str(e)}"
            }
    
    async def get_user_timeline(self, username, max_results=10):
        """Get recent tweets from a user's timeline"""
        if not self.is_configured:
            return {
                "success": False,
                "message": "Twitter API credentials not configured"
            }
            
        # First get the user ID
        user_result = await self.get_user_by_username(username)
        if not user_result["success"]:
            return user_result
            
        user_id = user_result["user"].get("id")
        if not user_id:
            return {
                "success": False,
                "message": "Could not retrieve user ID"
            }
            
        # Get user timeline
        headers = {"Authorization": f"Bearer {self.twitter_bearer_token}"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/users/{user_id}/tweets?max_results={max_results}&tweet.fields=created_at,public_metrics",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "tweets": result.get("data", [])
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "message": f"API request failed with status {response.status}: {error_text}"
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error fetching user timeline: {str(e)}"
            }
    
    async def search_tweets(self, query, max_results=25):
        """Search for tweets matching a query"""
        if not self.is_configured:
            return {
                "success": False,
                "message": "Twitter API credentials not configured"
            }
            
        headers = {"Authorization": f"Bearer {self.twitter_bearer_token}"}
        encoded_query = urllib.parse.quote(query)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/tweets/search/recent?query={encoded_query}&max_results={max_results}&tweet.fields=created_at,public_metrics,author_id",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "tweets": result.get("data", []),
                            "meta": result.get("meta", {})
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "message": f"API request failed with status {response.status}: {error_text}"
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error searching tweets: {str(e)}"
            }
    
    async def post_tweet(self, text):
        """Post a tweet using OAuth 1.0a"""
        if not self.is_configured or not all([
            self.twitter_api_key, 
            self.twitter_api_secret,
            self.twitter_access_token,
            self.twitter_access_secret
        ]):
            return {
                "success": False,
                "message": "Twitter OAuth credentials not fully configured"
            }
            
        # Create OAuth 1.0a signature
        oauth_timestamp = str(int(time.time()))
        oauth_nonce = hashlib.md5(oauth_timestamp.encode()).hexdigest()
        
        # Create parameter string
        params = {
            "oauth_consumer_key": self.twitter_api_key,
            "oauth_nonce": oauth_nonce,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": oauth_timestamp,
            "oauth_token": self.twitter_access_token,
            "oauth_version": "1.0",
            "text": text
        }
        
        # Create signature base string
        param_string = "&".join([f"{k}={urllib.parse.quote(str(v))}" for k, v in sorted(params.items())])
        base_url = f"{self.base_url}/tweets"
        signature_base = f"POST&{urllib.parse.quote(base_url)}&{urllib.parse.quote(param_string)}"
        
        # Create signing key
        signing_key = f"{urllib.parse.quote(self.twitter_api_secret)}&{urllib.parse.quote(self.twitter_access_secret)}"
        
        # Create signature
        hashed = hmac.new(
            signing_key.encode(),
            signature_base.encode(),
            hashlib.sha1
        )
        signature = base64.b64encode(hashed.digest()).decode()
        
        # Create Authorization header
        auth_header = 'OAuth '
        auth_header += f'oauth_consumer_key="{urllib.parse.quote(self.twitter_api_key)}", '
        auth_header += f'oauth_nonce="{oauth_nonce}", '
        auth_header += f'oauth_signature="{urllib.parse.quote(signature)}", '
        auth_header += f'oauth_signature_method="HMAC-SHA1", '
        auth_header += f'oauth_timestamp="{oauth_timestamp}", '
        auth_header += f'oauth_token="{urllib.parse.quote(self.twitter_access_token)}", '
        auth_header += f'oauth_version="1.0"'
        
        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json"
        }
        
        payload = {"text": text}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    base_url,
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status in (200, 201):
                        result = await response.json()
                        return {
                            "success": True,
                            "tweet_id": result.get("data", {}).get("id"),
                            "tweet": result.get("data", {})
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "message": f"API request failed with status {response.status}: {error_text}"
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error posting tweet: {str(e)}"
            }
    
    async def get_organix_profile(self):
        """Get the OrganiX Twitter profile"""
        return await self.get_user_by_username("0xOrganix")

# Initialize global instance
twitter_integration = TwitterIntegration()

async def test_twitter():
    """Test Twitter integration with OrganiX profile"""
    print("Testing Twitter integration...")
    
    organix_profile = await twitter_integration.get_organix_profile()
    if organix_profile["success"]:
        user = organix_profile["user"]
        print(f"Found OrganiX profile: @{user.get('username')}")
        print(f"Bio: {user.get('description')}")
        print(f"Followers: {user.get('public_metrics', {}).get('followers_count', 0)}")
        
        # Get recent tweets
        timeline = await twitter_integration.get_user_timeline("0xOrganix", 5)
        if timeline["success"]:
            print("\nRecent tweets:")
            for tweet in timeline.get("tweets", []):
                created_at = tweet.get("created_at", "").replace("T", " ").split(".")[0]
                print(f"[{created_at}] {tweet.get('text')}")
                
        return {
            "profile": organix_profile,
            "timeline": timeline if timeline["success"] else None
        }
    else:
        print(f"Error: {organix_profile.get('message', 'Unknown error')}")
        return None

if __name__ == "__main__":
    # Test Twitter integration
    asyncio.run(test_twitter())

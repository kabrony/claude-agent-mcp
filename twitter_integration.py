"""
Twitter/X Integration for OrganiX - Direct integration with Twitter/X API
"""
import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TwitterIntegration:
    def __init__(self, 
                 api_key=None, 
                 api_secret=None, 
                 access_token=None, 
                 access_secret=None):
        """
        Initialize Twitter integration with API credentials
        
        This can use either direct Twitter API credentials or leverage Composio
        for authentication and integration.
        """
        # Get credentials from parameters or environment
        self.api_key = api_key or os.getenv("TWITTER_API_KEY")
        self.api_secret = api_secret or os.getenv("TWITTER_API_SECRET")
        self.access_token = access_token or os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_secret = access_secret or os.getenv("TWITTER_ACCESS_SECRET")
        
        self.is_authenticated = False
        self.client = None
        
        # Initialize client if all credentials are available
        if self.api_key and self.api_secret and self.access_token and self.access_secret:
            try:
                # Attempt to create Tweepy client (if installed)
                self._setup_client()
            except Exception as e:
                logging.error(f"Error initializing Twitter client: {str(e)}")
    
    def _setup_client(self):
        """Set up the Twitter client using tweepy"""
        try:
            import tweepy
            
            # Create tweepy client with credentials
            self.client = tweepy.Client(
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_secret
            )
            
            self.is_authenticated = True
            logging.info("Twitter client initialized successfully")
            
        except ImportError:
            logging.warning("Tweepy not installed. Run: pip install tweepy")
        except Exception as e:
            logging.error(f"Error setting up Twitter client: {str(e)}")
            self.is_authenticated = False
    
    async def post_tweet(self, content: str) -> Dict[str, Any]:
        """Post a tweet to the authenticated account"""
        if not self.is_authenticated or not self.client:
            return {"success": False, "error": "Not authenticated with Twitter"}
        
        try:
            # Execute in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.client.create_tweet(text=content)
            )
            
            # Extract the tweet ID from the response
            tweet_id = response.data["id"]
            
            return {
                "success": True, 
                "tweet_id": tweet_id,
                "url": f"https://twitter.com/user/status/{tweet_id}"
            }
            
        except Exception as e:
            logging.error(f"Error posting tweet: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_user_timeline(self, username: str, count: int = 10) -> Dict[str, Any]:
        """Get recent tweets from a user's timeline"""
        if not self.is_authenticated or not self.client:
            return {"success": False, "error": "Not authenticated with Twitter"}
        
        try:
            # Execute in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            
            # First get the user ID
            user_response = await loop.run_in_executor(
                None,
                lambda: self.client.get_user(username=username)
            )
            
            user_id = user_response.data.id
            
            # Then get the user's tweets
            response = await loop.run_in_executor(
                None,
                lambda: self.client.get_users_tweets(
                    id=user_id,
                    max_results=count,
                    tweet_fields=["created_at", "public_metrics"]
                )
            )
            
            # Format the tweets
            tweets = []
            for tweet in response.data:
                tweets.append({
                    "id": tweet.id,
                    "text": tweet.text,
                    "created_at": tweet.created_at.isoformat() if hasattr(tweet, "created_at") else None,
                    "metrics": tweet.public_metrics if hasattr(tweet, "public_metrics") else None,
                    "url": f"https://twitter.com/user/status/{tweet.id}"
                })
            
            return {
                "success": True,
                "username": username,
                "user_id": user_id,
                "tweets": tweets
            }
            
        except Exception as e:
            logging.error(f"Error getting user timeline: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def search_tweets(self, query: str, count: int = 10) -> Dict[str, Any]:
        """Search for tweets matching a query"""
        if not self.is_authenticated or not self.client:
            return {"success": False, "error": "Not authenticated with Twitter"}
        
        try:
            # Execute in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.search_recent_tweets(
                    query=query,
                    max_results=count,
                    tweet_fields=["created_at", "public_metrics", "author_id"]
                )
            )
            
            # Format the tweets
            tweets = []
            for tweet in response.data:
                tweets.append({
                    "id": tweet.id,
                    "text": tweet.text,
                    "author_id": tweet.author_id,
                    "created_at": tweet.created_at.isoformat() if hasattr(tweet, "created_at") else None,
                    "metrics": tweet.public_metrics if hasattr(tweet, "public_metrics") else None,
                    "url": f"https://twitter.com/user/status/{tweet.id}"
                })
            
            return {
                "success": True,
                "query": query,
                "tweets": tweets
            }
            
        except Exception as e:
            logging.error(f"Error searching tweets: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the Twitter integration"""
        status = {
            "authenticated": self.is_authenticated,
            "client_initialized": self.client is not None
        }
        
        if not self.is_authenticated:
            if not self.api_key:
                status["error"] = "Missing API key"
            elif not self.api_secret:
                status["error"] = "Missing API secret"
            elif not self.access_token:
                status["error"] = "Missing access token"
            elif not self.access_secret:
                status["error"] = "Missing access secret"
            else:
                status["error"] = "Authentication failed"
        
        return status

async def test_twitter():
    """Test function for Twitter integration"""
    twitter = TwitterIntegration()
    
    # Check status
    status = twitter.get_status()
    print("Twitter integration status:", status)
    
    if not status["authenticated"]:
        print("Cannot run tests: Not authenticated with Twitter")
        return
    
    # Post a test tweet
    tweet_result = await twitter.post_tweet("Testing OrganiX Twitter integration! #OrganiX #AI")
    print("Tweet result:", tweet_result)
    
    # Get user timeline
    timeline_result = await twitter.get_user_timeline("0xOrganix", count=5)
    print("Timeline result:", timeline_result)
    
    # Search tweets
    search_result = await twitter.search_tweets("OrganiX AI", count=5)
    print("Search result:", search_result)

if __name__ == "__main__":
    # Run test function
    asyncio.run(test_twitter())

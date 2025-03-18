# OrganiX Social Media Integration

## Twitter/X Integration Guide

This document provides instructions for integrating the OrganiX agent with the official [OrganiX Twitter account](https://x.com/0xOrganix).

## Setup Requirements

To integrate OrganiX with Twitter/X, you'll need:

1. Twitter Developer Account with elevated access
2. API Key and Secret
3. Access Token and Secret
4. Bearer Token

## Configuration

### 1. Environment Variables

Add the following to your `.env` file:

```
# Twitter/X API Credentials
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_SECRET=your_access_secret_here
```

### 2. Install Dependencies

The integration requires the following dependencies which are already included in `requirements.txt`:

- `aiohttp` - For API requests
- `dotenv` - For environment variable management

### 3. Verify Setup

Run the following to verify that the Twitter integration is working correctly:

```python
# Test Twitter integration
from social_integrations import SocialMediaManager

async def test_twitter():
    manager = SocialMediaManager()
    profile = await manager.get_twitter_profile("0xOrganix")
    print(f"Profile data: {profile}")
    
    # If profile fetched successfully, try getting timeline
    if profile["success"]:
        timeline = await manager.get_twitter_timeline("0xOrganix", count=5)
        print(f"Timeline data: {timeline}")
        
    return profile["success"]

# Run test
import asyncio
asyncio.run(test_twitter())
```

## Usage Examples

### Fetch Profile Information

```python
from social_integrations import SocialMediaManager

# Initialize manager
manager = SocialMediaManager()

# Get profile information
profile_data = await manager.get_twitter_profile("0xOrganix")

if profile_data["success"]:
    profile = profile_data["profile"]
    print(f"Name: {profile.get('name')}")
    print(f"Description: {profile.get('description')}")
    print(f"Followers: {profile.get('public_metrics', {}).get('followers_count')}")
```

### Fetch Timeline

```python
# Get recent tweets
timeline_data = await manager.get_twitter_timeline("0xOrganix", count=10)

if timeline_data["success"]:
    tweets = timeline_data["tweets"]
    for tweet in tweets:
        print(f"Tweet: {tweet.get('text')}")
        print(f"Posted at: {tweet.get('created_at')}")
        print(f"Likes: {tweet.get('public_metrics', {}).get('like_count')}")
        print("---")
```

## Integration with Agent System

The social media integration can be used within the agent system to provide context and information about OrganiX's social presence.

### Example: Adding Twitter Awareness to Agent

```python
from advanced_chat import coordinator
from social_integrations import SocialMediaManager

# Initialize social media manager
social_manager = SocialMediaManager()

async def process_with_twitter_context(query):
    """Process a query with Twitter context"""
    # Check if query is about Twitter
    if "twitter" in query.lower() or "0xorganix" in query.lower():
        # Fetch latest Twitter data
        profile = await social_manager.get_twitter_profile("0xOrganix")
        timeline = await social_manager.get_twitter_timeline("0xOrganix", count=3)
        
        # Create context string
        context = "Context from OrganiX Twitter:\n"
        
        if profile["success"]:
            context += f"Profile description: {profile['profile'].get('description', 'N/A')}\n"
            
        if timeline["success"] and timeline["tweets"]:
            context += "Recent tweets:\n"
            for tweet in timeline["tweets"]:
                context += f"- {tweet.get('text')}\n"
                
        # Process with the agent using Twitter context
        return await coordinator.process_with_context_awareness(query, context=context)
    else:
        # Process normally
        return await coordinator.process_query(query)
```

## Security Considerations

1. **API Key Protection**: Never expose your Twitter API credentials in client-side code
2. **Rate Limiting**: Be mindful of Twitter API rate limits (especially for free tier)
3. **Content Policy**: Ensure automated interactions comply with Twitter's terms of service
4. **User Privacy**: Don't store or process user data from Twitter without appropriate disclosure

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Check that your API keys and tokens are correctly configured in the `.env` file
2. **Rate Limit Exceeded**: Twitter API has rate limits; implement exponential backoff for retries
3. **API Changes**: Twitter API can change; check for updates if integration suddenly fails

### Error Handling

The social media integration includes built-in error handling:

```python
# Example with error handling
profile_data = await social_manager.get_twitter_profile("non_existent_user")

if not profile_data["success"]:
    error_message = profile_data.get("message", "Unknown error")
    print(f"Error fetching profile: {error_message}")
    
    # Implement fallback behavior
    # ...
```

## Future Enhancements

1. **Tweet Posting**: Add capability to post tweets (requires additional permissions)
2. **Engagement Tracking**: Monitor mentions and engagements with OrganiX tweets
3. **Sentiment Analysis**: Analyze sentiment of tweets mentioning OrganiX
4. **Trending Topics**: Track blockchain and AI-related trending topics

## Official Account Information

Official OrganiX Twitter/X account: [@0xOrganix](https://x.com/0xOrganix)

This account is used for:
- Announcements of new features and updates
- Sharing insights about OrganiX development
- Engaging with the community
- Amplifying relevant blockchain and AI content

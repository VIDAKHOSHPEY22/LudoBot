"""
Telegram Bot Connection Test Module
Tests the connection to Telegram API with the provided bot token.
Verifies token validity and network connectivity.
"""

import requests
import time
import sys
import os
from typing import Tuple, Optional


class TokenTester:
    """
    Tests the bot token and connection to Telegram API.
    Provides detailed feedback about connection status.
    """
    
    def __init__(self, token: str):
        """
        Initialize the token tester.
        
        Args:
            token: Telegram bot token
        """
        self.token = token
        self.api_base = "https://api.telegram.org/bot"
    
    def test_connection(self) -> Tuple[bool, Optional[dict]]:
        """
        Test the connection to Telegram API with the provided token.
        
        Returns:
            Tuple[bool, Optional[dict]]: (success, bot_info)
        """
        print("🔄 Testing Telegram API connection...")
        
        # Check if token is valid format
        if not self._validate_token():
            return False, None
        
        # Test API endpoint
        url = f"{self.api_base}{self.token}/getMe"
        
        try:
            # Make the API request
            response = requests.get(url, timeout=10)
            print(f"✅ Response received! Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data.get('result', {})
                    return True, bot_info
                else:
                    print(f"❌ API Error: {data.get('description', 'Unknown error')}")
                    return False, None
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return False, None
                
        except requests.exceptions.Timeout:
            print("❌ Error: Timeout - Connection to Telegram timed out")
            print("💡 Possible causes:")
            print("   - Slow internet connection")
            print("   - Firewall blocking the connection")
            print("   - Telegram API is temporarily unavailable")
            return False, None
            
        except requests.exceptions.ConnectionError:
            print("❌ Error: Connection Error - Cannot reach Telegram")
            print("💡 Possible causes:")
            print("   - No internet connection")
            print("   - Telegram is blocked in your region")
            print("   - DNS resolution failed")
            return False, None
            
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            return False, None
    
    def _validate_token(self) -> bool:
        """
        Validate the bot token format.
        
        Returns:
            bool: True if token format is valid
        """
        if not self.token or self.token == "[put your token here for test❤️]":
            print("❌ Error: No valid token provided!")
            print("💡 Please set your bot token in the TOKEN variable")
            return False
        
        # Check token format (should be like: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz)
        parts = self.token.split(':')
        if len(parts) != 2 or not parts[0].isdigit() or len(parts[1]) < 10:
            print("⚠️ Warning: Token format looks invalid")
            print("💡 Token should be in format: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
            # Still try the connection
        
        return True
    
    def get_bot_info(self) -> Optional[dict]:
        """
        Get detailed bot information.
        
        Returns:
            Optional[dict]: Bot information or None
        """
        success, bot_info = self.test_connection()
        
        if success and bot_info:
            print("\n✅ Connection successful!")
            print("🤖 Bot Information:")
            print(f"   Name: {bot_info.get('first_name')}")
            print(f"   Username: @{bot_info.get('username')}")
            print(f"   Bot ID: {bot_info.get('id')}")
            print(f"   Can join groups: {bot_info.get('can_join_groups')}")
            print(f"   Supports inline: {bot_info.get('supports_inline_queries')}")
            return bot_info
        else:
            return None
    
    def test_full_connection(self):
        """
        Run a full connection test with detailed output.
        """
        print("=" * 50)
        print("🚀 Telegram Bot Token Test")
        print("=" * 50)
        
        # Test connection
        success, bot_info = self.test_connection()
        
        if success and bot_info:
            print("\n" + "=" * 50)
            print("✅ SUCCESS! Your bot token is valid!")
            print("=" * 50)
            print(f"🤖 Bot: @{bot_info.get('username')}")
            print(f"📋 Name: {bot_info.get('first_name')}")
            print(f"🆔 ID: {bot_info.get('id')}")
            print("=" * 50)
            print("\n🎉 Your bot is ready to use!")
            print("💡 Next steps:")
            print("   1. Run: python run.py")
            print("   2. Start a chat with your bot on Telegram")
            print("   3. Send /start command")
            return True
        else:
            print("\n" + "=" * 50)
            print("❌ FAILED! Connection test failed")
            print("=" * 50)
            print("💡 Troubleshooting tips:")
            print("   1. Check your bot token from @BotFather")
            print("   2. Make sure you have internet access")
            print("   3. Try using a VPN if Telegram is blocked")
            print("   4. Check your firewall settings")
            print("   5. Verify the token format is correct")
            return False


def test_with_retry(token: str, max_retries: int = 3) -> bool:
    """
    Test connection with automatic retries.
    
    Args:
        token: Bot token
        max_retries: Maximum number of retry attempts
        
    Returns:
        bool: True if connection successful
    """
    tester = TokenTester(token)
    
    for attempt in range(max_retries):
        print(f"\n🔄 Attempt {attempt + 1}/{max_retries}")
        
        success, bot_info = tester.test_connection()
        
        if success and bot_info:
            print("\n✅ Connection established!")
            print(f"🤖 Bot: @{bot_info.get('username')}")
            return True
        
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
            print(f"⏳ Waiting {wait_time}s before retry...")
            time.sleep(wait_time)
    
    print("\n❌ All connection attempts failed!")
    return False


def get_token_from_env() -> Optional[str]:
    """
    Get bot token from environment variables.
    
    Returns:
        Optional[str]: Bot token or None
    """
    token = os.getenv("BOT_TOKEN")
    if token:
        return token
    
    # Try to read from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv("BOT_TOKEN")
    except ImportError:
        pass
    
    return None


# Default token for direct testing
TOKEN = "[put your token here for test❤️]"


def main():
    """
    Main function to run the token test.
    """
    # Try to get token from environment first
    token = get_token_from_env()
    
    # If no token in env, use the hardcoded token
    if not token:
        token = TOKEN
    
    # Check if token is still the placeholder
    if token == "[put your token here for test❤️]":
        print("=" * 50)
        print("⚠️ WARNING: No valid token found!")
        print("=" * 50)
        print("\nPlease set your bot token:")
        print("1. Edit this file and set TOKEN = 'your_token'")
        print("2. Or set environment variable: set BOT_TOKEN=your_token")
        print("3. Or create a .env file with BOT_TOKEN=your_token")
        print("\nExample:")
        print("   TOKEN = '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz'")
        return
    
    # Create tester and run
    tester = TokenTester(token)
    success = tester.test_full_connection()
    
    # Also test with retries if first attempt failed
    if not success:
        print("\n" + "=" * 50)
        print("🔄 Trying with retries...")
        print("=" * 50)
        test_with_retry(token, max_retries=3)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
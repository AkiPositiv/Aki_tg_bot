#!/usr/bin/env python3
"""
Telegram RPG Bot - Test Script
"""
import os
import sys
import sqlite3
import requests
import subprocess
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bot_test")

class BotTester:
    def __init__(self):
        self.bot_token = "1730744154:AAGxL3yNgmoN3LOZvOWdNGu6Wgxt81TacXE"
        self.db_path = "/app/backend/rpg_game.db"
        self.log_path = "/app/backend/bot.log"
        self.tests_passed = 0
        self.tests_failed = 0
        self.telegram_api = f"https://api.telegram.org/bot{self.bot_token}"
    
    def run_tests(self):
        """Run all tests"""
        logger.info("Starting Telegram RPG Bot tests")
        
        # Test bot process
        self.test_bot_process()
        
        # Test database
        self.test_database_exists()
        self.test_database_tables()
        
        # Test bot API
        self.test_bot_api()
        
        # Print results
        logger.info(f"Tests completed: {self.tests_passed} passed, {self.tests_failed} failed")
        return self.tests_failed == 0
    
    def test_bot_process(self):
        """Test if bot process is running"""
        logger.info("Testing bot process...")
        try:
            result = subprocess.run(
                ["ps", "aux"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            if "bot_main.py" in result.stdout:
                logger.info("✅ Bot process is running")
                self.tests_passed += 1
            else:
                logger.error("❌ Bot process is not running")
                self.tests_failed += 1
        except Exception as e:
            logger.error(f"❌ Error checking bot process: {e}")
            self.tests_failed += 1
    
    def test_database_exists(self):
        """Test if database file exists"""
        logger.info("Testing database existence...")
        if Path(self.db_path).exists():
            logger.info(f"✅ Database file exists at {self.db_path}")
            self.tests_passed += 1
        else:
            logger.error(f"❌ Database file not found at {self.db_path}")
            self.tests_failed += 1
    
    def test_database_tables(self):
        """Test database tables"""
        logger.info("Testing database tables...")
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check users table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if cursor.fetchone():
                logger.info("✅ Users table exists")
                self.tests_passed += 1
            else:
                logger.error("❌ Users table not found")
                self.tests_failed += 1
            
            # Check battles table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='battles'")
            if cursor.fetchone():
                logger.info("✅ Battles table exists")
                self.tests_passed += 1
            else:
                logger.error("❌ Battles table not found")
                self.tests_failed += 1
            
            # Check table structure
            try:
                cursor.execute("PRAGMA table_info(users)")
                columns = [row[1] for row in cursor.fetchall()]
                required_columns = ['id', 'name', 'gender', 'kingdom', 'level', 'experience', 
                                   'strength', 'armor', 'hp', 'agility', 'mana']
                
                if all(col in columns for col in required_columns):
                    logger.info("✅ Users table has correct structure")
                    self.tests_passed += 1
                else:
                    missing = [col for col in required_columns if col not in columns]
                    logger.error(f"❌ Users table missing columns: {missing}")
                    self.tests_failed += 1
            except Exception as e:
                logger.error(f"❌ Error checking users table structure: {e}")
                self.tests_failed += 1
            
            conn.close()
        except Exception as e:
            logger.error(f"❌ Error connecting to database: {e}")
            self.tests_failed += 1
    
    def test_bot_api(self):
        """Test bot API"""
        logger.info("Testing bot API...")
        try:
            # Get bot info
            response = requests.get(f"{self.telegram_api}/getMe")
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get("ok"):
                    bot_username = bot_info["result"]["username"]
                    logger.info(f"✅ Bot API is working. Bot username: {bot_username}")
                    self.tests_passed += 1
                else:
                    logger.error(f"❌ Bot API error: {bot_info}")
                    self.tests_failed += 1
            else:
                logger.error(f"❌ Bot API request failed with status code {response.status_code}")
                self.tests_failed += 1
                
            # Check webhook status
            webhook_response = requests.get(f"{self.telegram_api}/getWebhookInfo")
            if webhook_response.status_code == 200:
                webhook_info = webhook_response.json()
                if webhook_info.get("ok"):
                    webhook_url = webhook_info["result"].get("url", "Not set")
                    if webhook_url:
                        logger.info(f"ℹ️ Bot is using webhook: {webhook_url}")
                    else:
                        logger.info("ℹ️ Bot is using polling (no webhook set)")
                    self.tests_passed += 1
                else:
                    logger.error(f"❌ Error getting webhook info: {webhook_info}")
                    self.tests_failed += 1
            else:
                logger.error(f"❌ Webhook info request failed with status code {webhook_response.status_code}")
                self.tests_failed += 1
                
        except Exception as e:
            logger.error(f"❌ Error testing bot API: {e}")
            self.tests_failed += 1
    
    def check_log_file(self):
        """Check log file for errors"""
        logger.info("Checking log file...")
        try:
            if not Path(self.log_path).exists():
                logger.error(f"❌ Log file not found at {self.log_path}")
                self.tests_failed += 1
                return
            
            with open(self.log_path, 'r') as f:
                log_content = f.read()
            
            # Check for critical errors
            error_keywords = ["ERROR", "CRITICAL", "Exception", "Error", "Failed"]
            errors_found = False
            
            for line in log_content.splitlines():
                if any(keyword in line for keyword in error_keywords):
                    logger.error(f"❌ Error found in logs: {line}")
                    errors_found = True
            
            if not errors_found:
                logger.info("✅ No critical errors found in logs")
                self.tests_passed += 1
            else:
                self.tests_failed += 1
                
        except Exception as e:
            logger.error(f"❌ Error checking log file: {e}")
            self.tests_failed += 1

def main():
    tester = BotTester()
    success = tester.run_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
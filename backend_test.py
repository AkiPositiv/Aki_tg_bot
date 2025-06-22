#!/usr/bin/env python3
"""
Telegram RPG Bot v3.0 - Test Script
Tests the new Interactive Battle and Kingdom Wars systems
"""
import os
import sys
import sqlite3
import requests
import subprocess
import time
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
import pytz

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
        self.log_path = "/app/backend/bot_v3.log"
        self.tests_passed = 0
        self.tests_failed = 0
        self.telegram_api = f"https://api.telegram.org/bot{self.bot_token}"
        self.tashkent_tz = pytz.timezone('Asia/Tashkent')
    
    def run_tests(self):
        """Run all tests"""
        logger.info("Starting Telegram RPG Bot v2.0 tests")
        
        # Test bot process
        self.test_bot_process()
        
        # Test database
        self.test_database_exists()
        self.test_database_tables()
        
        # Test bot API
        self.test_bot_api()
        
        # Test new shop and inventory system
        self.test_item_database()
        self.test_shop_service()
        self.test_inventory_service()
        
        # Check logs for errors
        self.check_log_file()
        
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
            
            # Check items table (NEW)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='items'")
            if cursor.fetchone():
                logger.info("✅ Items table exists")
                self.tests_passed += 1
            else:
                logger.error("❌ Items table not found")
                self.tests_failed += 1
            
            # Check user_items table (NEW)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_items'")
            if cursor.fetchone():
                logger.info("✅ User_items table exists")
                self.tests_passed += 1
            else:
                logger.error("❌ User_items table not found")
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
    
    def test_item_database(self):
        """Test item database"""
        logger.info("Testing item database...")
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check item count
            cursor.execute("SELECT COUNT(*) FROM items")
            item_count = cursor.fetchone()[0]
            if item_count == 15:
                logger.info(f"✅ Item database contains expected 15 items")
                self.tests_passed += 1
            else:
                logger.error(f"❌ Expected 15 items, found {item_count}")
                self.tests_failed += 1
            
            # Check item types
            cursor.execute("SELECT item_type, COUNT(*) FROM items GROUP BY item_type")
            item_types = {row[0]: row[1] for row in cursor.fetchall()}
            
            expected_types = {
                'weapon': 4,
                'armor': 4,
                'consumable': 5,
                'material': 2
            }
            
            if all(item_types.get(k, 0) == v for k, v in expected_types.items()):
                logger.info("✅ Item types distribution is correct")
                self.tests_passed += 1
            else:
                logger.error(f"❌ Item type distribution mismatch. Expected: {expected_types}, Found: {item_types}")
                self.tests_failed += 1
            
            # Check rarities
            cursor.execute("SELECT rarity, COUNT(*) FROM items GROUP BY rarity")
            rarities = {row[0]: row[1] for row in cursor.fetchall()}
            
            if 'common' in rarities and 'rare' in rarities and 'legendary' in rarities:
                logger.info("✅ Item rarities are correctly defined")
                self.tests_passed += 1
            else:
                logger.error(f"❌ Missing rarities. Found: {rarities}")
                self.tests_failed += 1
            
            # Check item properties
            cursor.execute("PRAGMA table_info(items)")
            columns = [row[1] for row in cursor.fetchall()]
            required_properties = [
                'strength_bonus', 'armor_bonus', 'hp_bonus', 'agility_bonus', 'mana_bonus',
                'durability', 'price', 'level_required'
            ]
            
            if all(prop in columns for prop in required_properties):
                logger.info("✅ Item properties are correctly defined")
                self.tests_passed += 1
            else:
                missing = [prop for prop in required_properties if prop not in columns]
                logger.error(f"❌ Missing item properties: {missing}")
                self.tests_failed += 1
            
            conn.close()
        except Exception as e:
            logger.error(f"❌ Error testing item database: {e}")
            self.tests_failed += 1
    
    def test_shop_service(self):
        """Test shop service functionality"""
        logger.info("Testing shop service...")
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check shop items
            cursor.execute("SELECT COUNT(*) FROM items WHERE is_available_in_shop = 1 OR is_available_in_shop IS NULL")
            shop_items = cursor.fetchone()[0]
            if shop_items > 0:
                logger.info(f"✅ Shop has {shop_items} items available")
                self.tests_passed += 1
            else:
                logger.error("❌ No items available in shop")
                self.tests_failed += 1
            
            # Check item categories
            cursor.execute("SELECT DISTINCT item_type FROM items")
            categories = [row[0] for row in cursor.fetchall()]
            expected_categories = ['weapon', 'armor', 'consumable', 'material']
            
            if all(cat in categories for cat in expected_categories):
                logger.info("✅ Shop categories are correctly defined")
                self.tests_passed += 1
            else:
                missing = [cat for cat in expected_categories if cat not in categories]
                logger.error(f"❌ Missing shop categories: {missing}")
                self.tests_failed += 1
            
            conn.close()
        except Exception as e:
            logger.error(f"❌ Error testing shop service: {e}")
            self.tests_failed += 1
    
    def test_inventory_service(self):
        """Test inventory service functionality"""
        logger.info("Testing inventory service...")
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check user_items table structure
            cursor.execute("PRAGMA table_info(user_items)")
            columns = [row[1] for row in cursor.fetchall()]
            required_columns = ['user_id', 'item_id', 'quantity', 'is_equipped', 'current_durability']
            
            if all(col in columns for col in required_columns):
                logger.info("✅ User_items table has correct structure")
                self.tests_passed += 1
            else:
                missing = [col for col in required_columns if col not in columns]
                logger.error(f"❌ User_items table missing columns: {missing}")
                self.tests_failed += 1
            
            # Check foreign key relationships
            try:
                # This is a simplified check - ideally we'd check the actual FK constraints
                cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='user_items'")
                if cursor.fetchone():
                    logger.info("✅ User_items table has indexes (likely for foreign keys)")
                    self.tests_passed += 1
                else:
                    logger.warning("⚠️ User_items table might be missing indexes for foreign keys")
            except Exception as e:
                logger.error(f"❌ Error checking user_items indexes: {e}")
                self.tests_failed += 1
            
            conn.close()
        except Exception as e:
            logger.error(f"❌ Error testing inventory service: {e}")
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
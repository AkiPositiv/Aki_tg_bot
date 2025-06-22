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
        logger.info("Starting Telegram RPG Bot v3.0 tests")
        
        # Test bot process
        self.test_bot_process()
        
        # Test database
        self.test_database_exists()
        self.test_database_tables()
        
        # Test bot API
        self.test_bot_api()
        
        # Test new v3.0 features
        self.test_monster_system()
        self.test_interactive_battle_system()
        self.test_kingdom_wars_system()
        self.test_war_scheduler()
        
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
            
            # Check all required tables
            required_tables = [
                'users', 'battles', 'items', 'user_items',
                'monsters', 'interactive_battles', 'kingdom_wars', 'war_participations'
            ]
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            for table in required_tables:
                if table in existing_tables:
                    logger.info(f"✅ {table} table exists")
                    self.tests_passed += 1
                else:
                    logger.error(f"❌ {table} table not found")
                    self.tests_failed += 1
            
            # Check v3.0 specific tables structure
            self.check_table_structure(cursor, 'monsters', [
                'id', 'name', 'description', 'monster_type', 'level', 
                'strength', 'armor', 'hp', 'agility', 'exp_reward', 'money_reward'
            ])
            
            self.check_table_structure(cursor, 'interactive_battles', [
                'id', 'mode', 'phase', 'player1_id', 'player2_id', 'monster_data',
                'current_round', 'max_rounds', 'player1_hp', 'player1_mana',
                'player2_hp', 'player2_mana', 'monster_hp', 'player1_attack_choice',
                'player1_dodge_choice', 'player2_attack_choice', 'player2_dodge_choice',
                'round_start_time', 'round_timeout', 'battle_log', 'winner_id',
                'exp_gained', 'money_gained', 'created_at', 'finished_at'
            ])
            
            self.check_table_structure(cursor, 'kingdom_wars', [
                'id', 'war_type', 'status', 'scheduled_time', 'started_at', 'finished_at',
                'attacking_kingdoms', 'defending_kingdom', 'attack_squads', 'defense_squad',
                'total_attack_stats', 'defense_stats', 'defense_buff', 'battle_results',
                'money_transferred', 'exp_distributed', 'created_at'
            ])
            
            self.check_table_structure(cursor, 'war_participations', [
                'id', 'war_id', 'user_id', 'kingdom', 'role', 'player_stats',
                'money_gained', 'money_lost', 'exp_gained', 'joined_at'
            ])
            
            conn.close()
        except Exception as e:
            logger.error(f"❌ Error connecting to database: {e}")
            self.tests_failed += 1
    
    def check_table_structure(self, cursor, table_name, required_columns):
        """Check if table has required columns"""
        try:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            
            if all(col in columns for col in required_columns):
                logger.info(f"✅ {table_name} table has correct structure")
                self.tests_passed += 1
            else:
                missing = [col for col in required_columns if col not in columns]
                logger.error(f"❌ {table_name} table missing columns: {missing}")
                self.tests_failed += 1
        except Exception as e:
            logger.error(f"❌ Error checking {table_name} table structure: {e}")
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
    
    def test_monster_system(self):
        """Test monster system"""
        logger.info("Testing monster system...")
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if monsters exist in database
            cursor.execute("SELECT COUNT(*) FROM monsters")
            monster_count = cursor.fetchone()[0]
            if monster_count > 0:
                logger.info(f"✅ Monster database contains {monster_count} monsters")
                self.tests_passed += 1
            else:
                logger.warning("⚠️ No monsters found in database. This might be normal if they are generated dynamically.")
            
            # Check monster types
            cursor.execute("SELECT DISTINCT monster_type FROM monsters")
            monster_types = [row[0] for row in cursor.fetchall()]
            expected_types = ['weak', 'normal', 'strong', 'boss']
            
            if monster_types:
                for monster_type in monster_types:
                    if monster_type in expected_types:
                        logger.info(f"✅ Monster type '{monster_type}' is valid")
                        self.tests_passed += 1
                    else:
                        logger.error(f"❌ Invalid monster type: {monster_type}")
                        self.tests_failed += 1
            
            # Test monster generation code by checking interactive battles
            cursor.execute("SELECT COUNT(*) FROM interactive_battles WHERE monster_data IS NOT NULL")
            monster_battles = cursor.fetchone()[0]
            if monster_battles > 0:
                logger.info(f"✅ Found {monster_battles} battles with monsters")
                self.tests_passed += 1
                
                # Check monster data structure
                cursor.execute("SELECT monster_data FROM interactive_battles WHERE monster_data IS NOT NULL LIMIT 1")
                monster_data = cursor.fetchone()
                if monster_data:
                    try:
                        monster_json = json.loads(monster_data[0])
                        required_fields = ['name', 'level', 'strength', 'armor', 'hp', 'agility', 
                                          'exp_reward', 'money_reward', 'type_emoji', 'difficulty_color']
                        
                        if all(field in monster_json for field in required_fields):
                            logger.info("✅ Monster data structure is correct")
                            self.tests_passed += 1
                        else:
                            missing = [field for field in required_fields if field not in monster_json]
                            logger.error(f"❌ Monster data missing fields: {missing}")
                            self.tests_failed += 1
                    except json.JSONDecodeError:
                        logger.error("❌ Monster data is not valid JSON")
                        self.tests_failed += 1
            
            conn.close()
        except Exception as e:
            logger.error(f"❌ Error testing monster system: {e}")
            self.tests_failed += 1
    
    def test_interactive_battle_system(self):
        """Test interactive battle system"""
        logger.info("Testing interactive battle system...")
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check battle modes
            cursor.execute("SELECT DISTINCT mode FROM interactive_battles")
            modes = [row[0] for row in cursor.fetchall()]
            expected_modes = ['pve_interactive', 'pvp_interactive', 'auto']
            
            for mode in modes:
                if mode in expected_modes:
                    logger.info(f"✅ Battle mode '{mode}' is valid")
                    self.tests_passed += 1
                else:
                    logger.error(f"❌ Invalid battle mode: {mode}")
                    self.tests_failed += 1
            
            # Check battle phases
            cursor.execute("SELECT DISTINCT phase FROM interactive_battles")
            phases = [row[0] for row in cursor.fetchall()]
            expected_phases = ['monster_encounter', 'attack_selection', 'dodge_selection', 'calculating', 'finished']
            
            for phase in phases:
                if phase in expected_phases:
                    logger.info(f"✅ Battle phase '{phase}' is valid")
                    self.tests_passed += 1
                else:
                    logger.error(f"❌ Invalid battle phase: {phase}")
                    self.tests_failed += 1
            
            # Check battle log structure
            cursor.execute("SELECT battle_log FROM interactive_battles WHERE battle_log != '[]' LIMIT 1")
            battle_log = cursor.fetchone()
            if battle_log:
                try:
                    log_json = json.loads(battle_log[0])
                    if isinstance(log_json, list) and len(log_json) > 0:
                        logger.info("✅ Battle log structure is correct")
                        self.tests_passed += 1
                        
                        # Check log entries
                        if 'round' in log_json[0]:
                            logger.info("✅ Battle log entries contain round information")
                            self.tests_passed += 1
                        else:
                            logger.error("❌ Battle log entries missing round information")
                            self.tests_failed += 1
                    else:
                        logger.warning("⚠️ Battle log is empty or not a list")
                except json.JSONDecodeError:
                    logger.error("❌ Battle log is not valid JSON")
                    self.tests_failed += 1
            
            # Check completed battles
            cursor.execute("SELECT COUNT(*) FROM interactive_battles WHERE phase = 'finished'")
            finished_battles = cursor.fetchone()[0]
            logger.info(f"ℹ️ Found {finished_battles} completed interactive battles")
            
            # Check battle timeout mechanism
            cursor.execute("SELECT round_timeout FROM interactive_battles LIMIT 1")
            timeout = cursor.fetchone()
            if timeout and timeout[0] > 0:
                logger.info(f"✅ Battle timeout is set to {timeout[0]} seconds")
                self.tests_passed += 1
            else:
                logger.warning("⚠️ Battle timeout not set or zero")
            
            conn.close()
        except Exception as e:
            logger.error(f"❌ Error testing interactive battle system: {e}")
            self.tests_failed += 1
    
    def test_kingdom_wars_system(self):
        """Test kingdom wars system"""
        logger.info("Testing kingdom wars system...")
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if wars are scheduled
            cursor.execute("SELECT COUNT(*) FROM kingdom_wars")
            war_count = cursor.fetchone()[0]
            if war_count > 0:
                logger.info(f"✅ Found {war_count} kingdom wars in database")
                self.tests_passed += 1
            else:
                logger.error("❌ No kingdom wars found in database")
                self.tests_failed += 1
            
            # Check war statuses
            cursor.execute("SELECT status, COUNT(*) FROM kingdom_wars GROUP BY status")
            statuses = {row[0]: row[1] for row in cursor.fetchall()}
            expected_statuses = ['scheduled', 'active', 'finished']
            
            for status in expected_statuses:
                if status in statuses:
                    logger.info(f"✅ Found {statuses[status]} wars with status '{status}'")
                    self.tests_passed += 1
                else:
                    logger.warning(f"⚠️ No wars with status '{status}' found")
            
            # Check war types
            cursor.execute("SELECT DISTINCT war_type FROM kingdom_wars")
            war_types = [row[0] for row in cursor.fetchall()]
            expected_types = ['kingdom_attack', 'siege']
            
            for war_type in war_types:
                if war_type in expected_types:
                    logger.info(f"✅ War type '{war_type}' is valid")
                    self.tests_passed += 1
                else:
                    logger.error(f"❌ Invalid war type: {war_type}")
                    self.tests_failed += 1
            
            # Check kingdoms
            cursor.execute("SELECT DISTINCT defending_kingdom FROM kingdom_wars")
            kingdoms = [row[0] for row in cursor.fetchall()]
            expected_kingdoms = ['north', 'south', 'east', 'west']
            
            for kingdom in kingdoms:
                if kingdom in expected_kingdoms:
                    logger.info(f"✅ Kingdom '{kingdom}' is valid")
                    self.tests_passed += 1
                else:
                    logger.error(f"❌ Invalid kingdom: {kingdom}")
                    self.tests_failed += 1
            
            # Check war scheduling
            today = datetime.now().date()
            cursor.execute(
                "SELECT COUNT(*) FROM kingdom_wars WHERE date(scheduled_time) = ?", 
                (today.isoformat(),)
            )
            today_wars = cursor.fetchone()[0]
            if today_wars > 0:
                logger.info(f"✅ Found {today_wars} wars scheduled for today")
                self.tests_passed += 1
            else:
                logger.warning("⚠️ No wars scheduled for today")
            
            # Check war times (should be at 8:00, 13:00, 18:00 Tashkent time)
            cursor.execute("SELECT scheduled_time FROM kingdom_wars LIMIT 20")
            war_times = [row[0] for row in cursor.fetchall()]
            
            tashkent_hours = set()
            for war_time in war_times:
                try:
                    dt = datetime.fromisoformat(war_time.replace('Z', '+00:00'))
                    tashkent_time = dt.astimezone(self.tashkent_tz)
                    tashkent_hours.add(tashkent_time.hour)
                except:
                    # Skip invalid datetime formats
                    pass
            
            expected_hours = {8, 13, 18}
            for hour in expected_hours:
                if hour in tashkent_hours:
                    logger.info(f"✅ Wars are scheduled for {hour}:00 Tashkent time")
                    self.tests_passed += 1
                else:
                    logger.warning(f"⚠️ No wars scheduled for {hour}:00 Tashkent time")
            
            # Check war participation
            cursor.execute("SELECT COUNT(*) FROM war_participations")
            participation_count = cursor.fetchone()[0]
            logger.info(f"ℹ️ Found {participation_count} war participations")
            
            conn.close()
        except Exception as e:
            logger.error(f"❌ Error testing kingdom wars system: {e}")
            self.tests_failed += 1
    
    def test_war_scheduler(self):
        """Test war scheduler"""
        logger.info("Testing war scheduler...")
        try:
            # Check if war_scheduler.py exists
            scheduler_path = Path("/app/backend/war_scheduler.py")
            if scheduler_path.exists():
                logger.info("✅ War scheduler file exists")
                self.tests_passed += 1
            else:
                logger.error("❌ War scheduler file not found")
                self.tests_failed += 1
            
            # Check if scheduler is mentioned in bot_main.py
            bot_main_path = Path("/app/backend/bot_main.py")
            if bot_main_path.exists():
                with open(bot_main_path, 'r') as f:
                    bot_main_content = f.read()
                    if "war_scheduler" in bot_main_content:
                        logger.info("✅ War scheduler is imported in bot_main.py")
                        self.tests_passed += 1
                        
                        if "war_scheduler.start()" in bot_main_content:
                            logger.info("✅ War scheduler is started in bot_main.py")
                            self.tests_passed += 1
                        else:
                            logger.error("❌ War scheduler is not started in bot_main.py")
                            self.tests_failed += 1
                    else:
                        logger.error("❌ War scheduler is not imported in bot_main.py")
                        self.tests_failed += 1
            
            # Check if scheduler is running by looking for scheduled wars
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for tomorrow's wars
            tomorrow = (datetime.now() + timedelta(days=1)).date()
            cursor.execute(
                "SELECT COUNT(*) FROM kingdom_wars WHERE date(scheduled_time) = ?", 
                (tomorrow.isoformat(),)
            )
            tomorrow_wars = cursor.fetchone()[0]
            if tomorrow_wars > 0:
                logger.info(f"✅ Found {tomorrow_wars} wars scheduled for tomorrow")
                self.tests_passed += 1
            else:
                logger.warning("⚠️ No wars scheduled for tomorrow")
            
            conn.close()
            
            # Check for scheduler in process list
            result = subprocess.run(
                ["ps", "aux"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            if "apscheduler" in result.stdout.lower():
                logger.info("✅ APScheduler is running (likely for war scheduling)")
                self.tests_passed += 1
            else:
                logger.warning("⚠️ APScheduler not found in process list")
            
        except Exception as e:
            logger.error(f"❌ Error testing war scheduler: {e}")
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
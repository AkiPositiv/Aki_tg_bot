#!/usr/bin/env python3
"""
Kingdom War Scheduler - запускает войны в указанное время
"""
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from services.kingdom_war_service import KingdomWarService
import logging
import pytz

logger = logging.getLogger(__name__)

class KingdomWarScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.war_service = KingdomWarService()
        self.tashkent_tz = pytz.timezone('Asia/Tashkent')
    
    def start(self):
        """Запуск планировщика войн"""
        # Планировщик войн в 8:00, 13:00, 18:00 по Ташкентскому времени
        for hour in [8, 13, 18]:
            self.scheduler.add_job(
                self.process_scheduled_wars,
                trigger=CronTrigger(hour=hour, minute=0, timezone=self.tashkent_tz),
                id=f'kingdom_war_{hour}',
                args=[hour]
            )
        
        # Планирование войн на завтра каждый день в полночь
        self.scheduler.add_job(
            self.schedule_tomorrow_wars,
            trigger=CronTrigger(hour=0, minute=0, timezone=self.tashkent_tz),
            id='schedule_wars'
        )
        
        # Планирование войн на сегодня при запуске
        self.scheduler.add_job(
            self.schedule_today_wars,
            id='schedule_today_wars'
        )
        
        self.scheduler.start()
        logger.info("Kingdom War Scheduler started")
    
    async def process_scheduled_wars(self, hour: int):
        """Обработка запланированных войн"""
        try:
            # Получить все запланированные войны на этот час
            now = datetime.now(self.tashkent_tz)
            wars = await self.war_service.get_scheduled_wars(now)
            
            wars_started = 0
            for war in wars:
                # Проверить, что время войны соответствует текущему часу
                war_time_tashkent = war.scheduled_time.astimezone(self.tashkent_tz)
                if war_time_tashkent.hour == hour:
                    success = await self.war_service.start_war(war.id)
                    if success:
                        wars_started += 1
                        logger.info(f"Started war {war.id} for kingdom {war.defending_kingdom}")
            
            logger.info(f"Processed {wars_started} wars at {hour}:00 Tashkent time")
            
        except Exception as e:
            logger.error(f"Error processing wars at {hour}:00: {e}")
    
    async def schedule_today_wars(self):
        """Планирование войн на сегодня (при запуске бота)"""
        try:
            today = datetime.now(self.tashkent_tz)
            await self.war_service.schedule_daily_wars(today)
            logger.info("Scheduled wars for today")
        except Exception as e:
            logger.error(f"Error scheduling today's wars: {e}")
    
    async def schedule_tomorrow_wars(self):
        """Планирование войн на завтра"""
        try:
            tomorrow = datetime.now(self.tashkent_tz) + timedelta(days=1)
            await self.war_service.schedule_daily_wars(tomorrow)
            logger.info("Scheduled wars for tomorrow")
        except Exception as e:
            logger.error(f"Error scheduling tomorrow's wars: {e}")
    
    def stop(self):
        """Остановка планировщика"""
        self.scheduler.shutdown()
        logger.info("Kingdom War Scheduler stopped")

# Глобальный экземпляр планировщика
war_scheduler = KingdomWarScheduler()
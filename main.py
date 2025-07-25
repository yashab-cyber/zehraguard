#!/usr/bin/env python3
"""
ZehraGuard InsightX - Main Application Entry Point
"""

import asyncio
import uvicorn
import logging
import signal
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.main import app
from core.config import settings
from core.database import Database
from core.services.ml_service import MLService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/zehraguard.log')
    ]
)

logger = logging.getLogger(__name__)

class ZehraGuardApplication:
    """
    Main application class that manages the lifecycle of ZehraGuard InsightX
    """
    
    def __init__(self):
        self.app = app
        self.database = Database()
        self.ml_service = MLService()
        self.shutdown_event = asyncio.Event()
    
    async def startup(self):
        """
        Application startup tasks
        """
        try:
            logger.info("Starting ZehraGuard InsightX...")
            
            # Initialize database
            logger.info("Initializing database...")
            await self.database.create_tables()
            
            # Initialize ML service
            logger.info("Initializing ML service...")
            await self.ml_service.initialize()
            
            logger.info("ZehraGuard InsightX started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start application: {str(e)}")
            raise
    
    async def shutdown(self):
        """
        Application shutdown tasks
        """
        try:
            logger.info("Shutting down ZehraGuard InsightX...")
            
            # Cleanup tasks would go here
            
            logger.info("ZehraGuard InsightX shut down successfully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
    
    def setup_signal_handlers(self):
        """
        Setup signal handlers for graceful shutdown
        """
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """
    Main application entry point
    """
    zg_app = ZehraGuardApplication()
    zg_app.setup_signal_handlers()
    
    try:
        # Startup
        await zg_app.startup()
        
        # Create server config
        config = uvicorn.Config(
            app=zg_app.app,
            host=settings.api_host,
            port=settings.api_port,
            workers=1,  # Single worker for async app
            log_level=settings.log_level.lower(),
            access_log=True,
            reload=settings.debug
        )
        
        server = uvicorn.Server(config)
        
        # Start server in background
        server_task = asyncio.create_task(server.serve())
        
        # Wait for shutdown signal
        await zg_app.shutdown_event.wait()
        
        # Graceful shutdown
        await zg_app.shutdown()
        server.should_exit = True
        await server_task
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # Run the application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

import os
import mysql.connector
from mysql.connector import pooling
from mysql.connector import Error
from typing import Optional, List, Dict
import logging
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        # Check if running on Railway by looking for a Railway-specific env var
        is_railway = 'RAILWAY_ENVIRONMENT' in os.environ

        if is_railway:
            logger.info("Railway environment detected. Using MYSQL_URL.")
            # Railway provides a single connection string URL which is more reliable
            db_url_str = os.getenv('MYSQL_URL')
            if not db_url_str:
                logger.critical("MYSQL_URL not found in Railway environment! Cannot connect to the database.")
                raise ValueError("MYSQL_URL environment variable not found.")
            
            url = urlparse(db_url_str)
            db_host = url.hostname
            db_user = url.username
            db_password = url.password
            db_name = url.path[1:]  # Remove leading '/'
            db_port = url.port

        else:
            logger.info("Local environment detected. Using .env file variables.")
            db_host = os.getenv('DB_HOST', 'localhost')
            db_user = os.getenv('DB_USER', 'root')
            db_password = os.getenv('DB_PASSWORD', '')
            db_name = os.getenv('DB_NAME', 'vortex_bot')
            db_port = os.getenv('DB_PORT', 3306)

        try:
            # For local development, we ensure the database exists.
            # On Railway, the database is already provisioned and this step is skipped.
            if not is_railway:
                conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, port=int(db_port))
                cursor = conn.cursor()
                logger.info(f"Ensuring local database '{db_name}' exists...")
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                cursor.close()
                conn.close()
                logger.info(f"Local database '{db_name}' is ready.")

            # Create the connection pool
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="bot_pool",
                pool_size=5,
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_password,
                port=int(db_port),
                charset='utf8mb4'
            )
            logger.info("Database connection pool created successfully.")
            
            # Create tables if they don't exist
            self._create_tables()

        except Error as e:
            logger.error(f"Database setup error: {e}")
            raise

    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        conn = self.pool.get_connection()
        cursor = conn.cursor()

        try:
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    first_name VARCHAR(255),
                    username VARCHAR(255),
                    phone_number VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            ''')

            # Statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stats (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT,
                    action_type VARCHAR(50),
                    action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            ''')

            conn.commit()
        except Error as e:
            logger.error(f"Error creating tables: {str(e)}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    async def add_user(self, user_id: int, first_name: str, username: str, phone_number: str) -> bool:
        """Add a new user to the database."""
        conn = self.pool.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT IGNORE INTO users (user_id, first_name, username, phone_number)
                VALUES (%s, %s, %s, %s)
            ''', (user_id, first_name, username, phone_number))
            
            conn.commit()
            return True
        except Error as e:
            logger.error(f"Error adding user: {str(e)}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    async def get_user_stats(self, user_id: int) -> Optional[Dict]:
        """Get user statistics."""
        conn = self.pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_actions,
                    DATE_FORMAT(MAX(action_time), '%Y-%m-%d') as last_action_date
                FROM stats 
                WHERE user_id = %s
            ''', (user_id,))
            
            return cursor.fetchone()
        except Error as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return None
        finally:
            cursor.close()
            conn.close()

    async def log_action(self, user_id: int, action_type: str) -> bool:
        """Log user action."""
        conn = self.pool.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO stats (user_id, action_type)
                VALUES (%s, %s)
            ''', (user_id, action_type))
            
            conn.commit()
            return True
        except Error as e:
            logger.error(f"Error logging action: {str(e)}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    async def get_bot_stats(self) -> Dict:
        """Get overall bot statistics."""
        conn = self.pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT user_id) as total_users,
                    COUNT(*) as total_actions,
                    COUNT(DISTINCT CASE WHEN DATE(action_time) = CURDATE() THEN user_id END) as new_today
                FROM stats
            ''')
            
            return cursor.fetchone()
        except Error as e:
            logger.error(f"Error getting bot stats: {str(e)}")
            return {
                'total_users': 0,
                'total_actions': 0,
                'new_today': 0
            }
        finally:
            cursor.close()
            conn.close()

# Create a singleton instance
db = Database()

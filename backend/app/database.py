"""
Database operations for Clinical Trial Accelerator.

This module handles all SQLite database operations including:
- Database initialization and schema creation
- Protocol CRUD operations
- Connection management
- Error handling and logging
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from .models import ProtocolCreate, ProtocolInDB, ProtocolUpdate

# Configure logging
logger = logging.getLogger(__name__)

# Database configuration
# Use /tmp directory for Vercel serverless functions, fallback to local for development
import os
if os.environ.get('VERCEL'):
    DATABASE_PATH = Path("/tmp/protocols.db")
else:
    DATABASE_PATH = Path("protocols.db")
SCHEMA_VERSION = 1


class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass


class ProtocolNotFoundError(DatabaseError):
    """Exception raised when a protocol is not found."""
    pass


class DuplicateProtocolError(DatabaseError):
    """Exception raised when trying to create a duplicate protocol."""
    pass


def generate_collection_name(study_acronym: str) -> str:
    """
    Generate a unique collection name for Qdrant.
    
    Args:
        study_acronym: The study acronym
        
    Returns:
        Unique collection name in format: study_acronym_timestamp[_microseconds]
    """
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    # Clean study acronym for collection name (alphanumeric + underscore only)
    clean_acronym = ''.join(c for c in study_acronym if c.isalnum() or c == '_').lower()
    
    # Add microseconds for uniqueness when not zero (e.g., in real-time scenarios)
    if now.microsecond > 0:
        microseconds = f"{now.microsecond:06d}"
        return f"{clean_acronym}_{timestamp}_{microseconds}"
    else:
        return f"{clean_acronym}_{timestamp}"


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    
    Yields:
        sqlite3.Connection: Database connection with row factory
        
    Raises:
        DatabaseError: If connection fails
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        yield conn
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise DatabaseError(f"Database operation failed: {e}")
    finally:
        if conn:
            conn.close()


def init_database() -> None:
    """
    Initialize the database and create tables if they don't exist.
    
    Raises:
        DatabaseError: If database initialization fails
    """
    try:
        with get_db_connection() as conn:
            # Create protocols table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS protocols (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    study_acronym TEXT NOT NULL,
                    protocol_title TEXT NOT NULL,
                    collection_name TEXT UNIQUE NOT NULL,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'processing',
                    file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index on collection_name for faster lookups
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_protocols_collection_name 
                ON protocols(collection_name)
            """)
            
            # Create index on status for filtering
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_protocols_status 
                ON protocols(status)
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise DatabaseError(f"Database initialization failed: {e}")


def create_protocol(protocol_data: ProtocolCreate) -> ProtocolInDB:
    """
    Create a new protocol record in the database.
    
    Args:
        protocol_data: Protocol data to create
        
    Returns:
        ProtocolInDB: Created protocol with database fields
        
    Raises:
        DuplicateProtocolError: If collection name already exists
        DatabaseError: If database operation fails
    """
    collection_name = generate_collection_name(protocol_data.study_acronym)
    current_time = datetime.now()
    
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO protocols (
                    study_acronym, protocol_title, collection_name, 
                    upload_date, status, file_path, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                protocol_data.study_acronym,
                protocol_data.protocol_title,
                collection_name,
                current_time,
                "processing",
                protocol_data.file_path,
                current_time
            ))
            
            protocol_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Created protocol with ID {protocol_id}")
            
            # Return the created protocol
            return ProtocolInDB(
                id=protocol_id,
                study_acronym=protocol_data.study_acronym,
                protocol_title=protocol_data.protocol_title,
                collection_name=collection_name,
                upload_date=current_time,
                status="processing",
                file_path=protocol_data.file_path,
                created_at=current_time
            )
            
    except sqlite3.IntegrityError as e:
        if "collection_name" in str(e):
            raise DuplicateProtocolError(f"Collection name already exists: {collection_name}")
        raise DatabaseError(f"Database constraint violation: {e}")
    except Exception as e:
        logger.error(f"Failed to create protocol: {e}")
        raise DatabaseError(f"Failed to create protocol: {e}")


def get_protocol_by_id(protocol_id: int) -> ProtocolInDB:
    """
    Retrieve a protocol by its ID.
    
    Args:
        protocol_id: Protocol ID to retrieve
        
    Returns:
        ProtocolInDB: Protocol data
        
    Raises:
        ProtocolNotFoundError: If protocol doesn't exist
        DatabaseError: If database operation fails
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM protocols WHERE id = ?
            """, (protocol_id,))
            
            row = cursor.fetchone()
            if not row:
                raise ProtocolNotFoundError(f"Protocol with ID {protocol_id} not found")
            
            return _row_to_protocol(row)
            
    except ProtocolNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to get protocol {protocol_id}: {e}")
        raise DatabaseError(f"Failed to retrieve protocol: {e}")


def get_protocol_by_collection_name(collection_name: str) -> ProtocolInDB:
    """
    Retrieve a protocol by its collection name.
    
    Args:
        collection_name: Collection name to search for
        
    Returns:
        ProtocolInDB: Protocol data
        
    Raises:
        ProtocolNotFoundError: If protocol doesn't exist
        DatabaseError: If database operation fails
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM protocols WHERE collection_name = ?
            """, (collection_name,))
            
            row = cursor.fetchone()
            if not row:
                raise ProtocolNotFoundError(f"Protocol with collection name {collection_name} not found")
            
            return _row_to_protocol(row)
            
    except ProtocolNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to get protocol by collection name {collection_name}: {e}")
        raise DatabaseError(f"Failed to retrieve protocol: {e}")


def get_all_protocols(status_filter: Optional[str] = None) -> List[ProtocolInDB]:
    """
    Retrieve all protocols, optionally filtered by status.
    
    Args:
        status_filter: Optional status to filter by
        
    Returns:
        List[ProtocolInDB]: List of protocols
        
    Raises:
        DatabaseError: If database operation fails
    """
    try:
        with get_db_connection() as conn:
            if status_filter:
                cursor = conn.execute("""
                    SELECT * FROM protocols WHERE status = ? 
                    ORDER BY upload_date DESC
                """, (status_filter,))
            else:
                cursor = conn.execute("""
                    SELECT * FROM protocols ORDER BY upload_date DESC
                """)
            
            rows = cursor.fetchall()
            return [_row_to_protocol(row) for row in rows]
            
    except Exception as e:
        logger.error(f"Failed to get protocols: {e}")
        raise DatabaseError(f"Failed to retrieve protocols: {e}")


def update_protocol_status(protocol_id: int, status_update: ProtocolUpdate) -> ProtocolInDB:
    """
    Update a protocol's status.
    
    Args:
        protocol_id: Protocol ID to update
        status_update: New status data
        
    Returns:
        ProtocolInDB: Updated protocol data
        
    Raises:
        ProtocolNotFoundError: If protocol doesn't exist
        DatabaseError: If database operation fails
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("""
                UPDATE protocols SET status = ? WHERE id = ?
            """, (status_update.status, protocol_id))
            
            if cursor.rowcount == 0:
                raise ProtocolNotFoundError(f"Protocol with ID {protocol_id} not found")
            
            conn.commit()
            logger.info(f"Updated protocol {protocol_id} status to {status_update.status}")
            
            # Return updated protocol
            return get_protocol_by_id(protocol_id)
            
    except ProtocolNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to update protocol {protocol_id}: {e}")
        raise DatabaseError(f"Failed to update protocol: {e}")


def delete_protocol(protocol_id: int) -> bool:
    """
    Delete a protocol from the database.
    
    Args:
        protocol_id: Protocol ID to delete
        
    Returns:
        bool: True if protocol was deleted
        
    Raises:
        ProtocolNotFoundError: If protocol doesn't exist
        DatabaseError: If database operation fails
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM protocols WHERE id = ?
            """, (protocol_id,))
            
            if cursor.rowcount == 0:
                raise ProtocolNotFoundError(f"Protocol with ID {protocol_id} not found")
            
            conn.commit()
            logger.info(f"Deleted protocol {protocol_id}")
            return True
            
    except ProtocolNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to delete protocol {protocol_id}: {e}")
        raise DatabaseError(f"Failed to delete protocol: {e}")


def _row_to_protocol(row: sqlite3.Row) -> ProtocolInDB:
    """
    Convert a database row to a ProtocolInDB model.
    
    Args:
        row: SQLite row object
        
    Returns:
        ProtocolInDB: Protocol model instance
    """
    return ProtocolInDB(
        id=row["id"],
        study_acronym=row["study_acronym"],
        protocol_title=row["protocol_title"],
        collection_name=row["collection_name"],
        upload_date=datetime.fromisoformat(row["upload_date"]),
        status=row["status"],
        file_path=row["file_path"],
        created_at=datetime.fromisoformat(row["created_at"])
    ) 
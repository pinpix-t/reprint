"""
File locking utilities for cross-process file access.
Provides a context manager for safe file operations with locking.
"""
import os
import fcntl
import logging
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@contextmanager
def file_lock(file_path: str, mode: str = 'r', blocking: bool = True):
    """
    Context manager for file operations with advisory file locking.
    
    Args:
        file_path: Path to the file
        mode: File open mode ('r', 'w', 'a', etc.)
        blocking: If True, wait for lock; if False, raise BlockingIOError
    
    Yields:
        File object with lock held
        
    Example:
        with file_lock('/path/to/file.csv', 'r') as f:
            data = f.read()
    """
    lock_flags = fcntl.LOCK_EX
    if not blocking:
        lock_flags |= fcntl.LOCK_NB
    
    try:
        with open(file_path, mode, encoding='utf-8') as f:
            try:
                fcntl.flock(f.fileno(), lock_flags)
                logger.debug(f"Acquired file lock for {file_path}")
                yield f
            except BlockingIOError:
                if not blocking:
                    logger.warning(f"File {file_path} is locked by another process")
                    raise
                # Retry with blocking lock
                logger.warning(f"File {file_path} is locked, waiting...")
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                yield f
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                logger.debug(f"Released file lock for {file_path}")
    except (OSError, IOError) as e:
        # Fallback for systems without fcntl (e.g., Windows)
        logger.warning(f"File locking not available on this system: {e}")
        # Just open without locking
        with open(file_path, mode, encoding='utf-8') as f:
            yield f


"""
Job locking utilities to prevent concurrent execution of scheduled jobs.
Uses file-based locking for cross-process coordination.
"""
import os
import fcntl
import time
import logging
from typing import Optional
from contextlib import contextmanager
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

LOCK_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'locks')
LOCK_TIMEOUT_SECONDS = 3600  # 1 hour max lock time

def ensure_lock_dir():
    """Ensure lock directory exists."""
    os.makedirs(LOCK_DIR, exist_ok=True)
    # Set restrictive permissions
    os.chmod(LOCK_DIR, 0o700)

@contextmanager
def job_lock(job_name: str, timeout: int = LOCK_TIMEOUT_SECONDS):
    """
    Context manager for job locking to prevent concurrent execution.
    
    Args:
        job_name: Name of the job (e.g., 'daily_refresh', 'weekly_report')
        timeout: Maximum lock duration in seconds
    
    Yields:
        True if lock acquired, False if already running
        
    Example:
        with job_lock('daily_refresh') as acquired:
            if acquired:
                # Run job
                pass
            else:
                logger.warning("Job already running, skipping")
    """
    ensure_lock_dir()
    lock_file_path = os.path.join(LOCK_DIR, f"{job_name}.lock")
    pid_file_path = os.path.join(LOCK_DIR, f"{job_name}.pid")
    
    lock_acquired = False
    lock_file = None
    
    try:
        # Check if lock file exists and is stale
        if os.path.exists(lock_file_path):
            lock_age = time.time() - os.path.getmtime(lock_file_path)
            if lock_age > timeout:
                logger.warning(f"Stale lock file detected for {job_name} (age: {lock_age}s), removing")
                try:
                    os.remove(lock_file_path)
                    if os.path.exists(pid_file_path):
                        os.remove(pid_file_path)
                except OSError as e:
                    logger.error(f"Error removing stale lock: {e}")
            else:
                # Check if process is still alive
                try:
                    with open(pid_file_path, 'r') as f:
                        pid = int(f.read().strip())
                    # Check if process exists (Unix)
                    try:
                        os.kill(pid, 0)  # Signal 0 doesn't kill, just checks
                        logger.warning(f"Job {job_name} already running (PID: {pid})")
                        yield False
                        return
                    except OSError:
                        # Process doesn't exist, remove stale lock
                        logger.warning(f"Lock file exists but process {pid} is dead, removing stale lock")
                        os.remove(lock_file_path)
                        if os.path.exists(pid_file_path):
                            os.remove(pid_file_path)
                except (ValueError, FileNotFoundError):
                    # Invalid PID file, remove it
                    if os.path.exists(pid_file_path):
                        os.remove(pid_file_path)
        
        # Acquire lock
        lock_file = open(lock_file_path, 'w')
        try:
            # Try non-blocking lock first
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            lock_acquired = True
            
            # Write PID and timestamp
            lock_file.write(f"{os.getpid()}\n{datetime.now().isoformat()}\n")
            lock_file.flush()
            
            # Write PID file
            with open(pid_file_path, 'w') as pid_file:
                pid_file.write(str(os.getpid()))
            
            logger.info(f"Acquired lock for job: {job_name}")
            yield True
            
        except BlockingIOError:
            logger.warning(f"Could not acquire lock for {job_name}, job already running")
            yield False
            return
            
    except (OSError, IOError) as e:
        # Fallback for systems without fcntl (e.g., Windows)
        logger.warning(f"File locking not available: {e}, using file existence check only")
        if os.path.exists(lock_file_path):
            yield False
            return
        
        # Create lock file
        try:
            with open(lock_file_path, 'w') as f:
                f.write(f"{os.getpid()}\n{datetime.now().isoformat()}\n")
            with open(pid_file_path, 'w') as f:
                f.write(str(os.getpid()))
            lock_acquired = True
            yield True
        except Exception as e:
            logger.error(f"Error creating lock file: {e}")
            yield False
            return
            
    finally:
        # Release lock
        if lock_acquired and lock_file:
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            except (OSError, AttributeError):
                pass
            lock_file.close()
            
            # Remove lock files
            try:
                if os.path.exists(lock_file_path):
                    os.remove(lock_file_path)
                if os.path.exists(pid_file_path):
                    os.remove(pid_file_path)
                logger.info(f"Released lock for job: {job_name}")
            except OSError as e:
                logger.error(f"Error removing lock file: {e}")


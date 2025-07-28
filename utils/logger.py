"""
Simple Logger Module for Document Integrity Protection System
Provides structured logging with different levels and file/console output.
"""

import os
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Union
from enum import Enum


class LogLevel(Enum):
    """Log levels for the application."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class SimpleLogger:
    """Simple logger class for the document integrity system."""
    
    def __init__(self, name: str = "DocumentIntegritySystem", 
                 log_dir: Union[str, Path] = "data/logs",
                 log_level: LogLevel = LogLevel.INFO,
                 console_output: bool = True,
                 file_output: bool = True,
                 max_file_size_mb: int = 10,
                 backup_count: int = 5):
        """
        Initialize the logger.
        
        Args:
            name (str): Logger name
            log_dir (Union[str, Path]): Directory for log files
            log_level (LogLevel): Minimum log level to record
            console_output (bool): Whether to output to console
            file_output (bool): Whether to output to file
            max_file_size_mb (int): Maximum log file size in MB
            backup_count (int): Number of backup files to keep
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_level = log_level
        self.console_output = console_output
        self.file_output = file_output
        self.max_file_size_mb = max_file_size_mb
        self.backup_count = backup_count
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize logger
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up the logger with handlers and formatters."""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.log_level.value)
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        if self.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level.value)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # File handler
        if self.file_output:
            log_file = self.log_dir / f"{self.name.lower()}.log"
            
            # Use RotatingFileHandler to manage file size
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=self.max_file_size_mb * 1024 * 1024,
                backupCount=self.backup_count
            )
            file_handler.setLevel(self.log_level.value)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(message, **kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        self.logger.exception(message, **kwargs)
    
    def log_operation(self, operation: str, file_path: Optional[str] = None, 
                     status: str = "SUCCESS", details: Optional[str] = None) -> None:
        """
        Log an operation with structured format.
        
        Args:
            operation (str): Operation name (e.g., "ENCRYPT", "HASH", "VERIFY")
            file_path (Optional[str]): File path involved in operation
            status (str): Operation status ("SUCCESS", "FAILED", "WARNING")
            details (Optional[str]): Additional details
        """
        message_parts = [f"OPERATION: {operation}"]
        
        if file_path:
            message_parts.append(f"FILE: {file_path}")
        
        message_parts.append(f"STATUS: {status}")
        
        if details:
            message_parts.append(f"DETAILS: {details}")
        
        message = " | ".join(message_parts)
        
        if status == "SUCCESS":
            self.info(message)
        elif status == "WARNING":
            self.warning(message)
        else:  # FAILED or ERROR
            self.error(message)
    
    def log_security_event(self, event_type: str, description: str, 
                          severity: str = "INFO", user_data: Optional[dict] = None) -> None:
        """
        Log security-related events.
        
        Args:
            event_type (str): Type of security event
            description (str): Event description
            severity (str): Event severity ("INFO", "WARNING", "ERROR", "CRITICAL")
            user_data (Optional[dict]): Additional user data
        """
        message = f"SECURITY EVENT: {event_type} | {description}"
        
        if user_data:
            user_info = " | ".join([f"{k}: {v}" for k, v in user_data.items()])
            message += f" | {user_info}"
        
        severity_map = {
            "INFO": self.info,
            "WARNING": self.warning,
            "ERROR": self.error,
            "CRITICAL": self.critical
        }
        
        log_func = severity_map.get(severity.upper(), self.info)
        log_func(message)
    
    def log_performance(self, operation: str, duration_ms: float, 
                       file_size_mb: Optional[float] = None) -> None:
        """
        Log performance metrics.
        
        Args:
            operation (str): Operation name
            duration_ms (float): Duration in milliseconds
            file_size_mb (Optional[float]): File size in MB
        """
        message = f"PERFORMANCE: {operation} | Duration: {duration_ms:.2f}ms"
        
        if file_size_mb is not None:
            message += f" | File Size: {file_size_mb:.2f}MB"
            if file_size_mb > 0:
                throughput = file_size_mb / (duration_ms / 1000)  # MB/s
                message += f" | Throughput: {throughput:.2f}MB/s"
        
        self.info(message)
    
    def set_level(self, level: LogLevel) -> None:
        """Change the logging level."""
        self.log_level = level
        self.logger.setLevel(level.value)
        
        for handler in self.logger.handlers:
            handler.setLevel(level.value)
    
    def get_log_file_path(self) -> Optional[Path]:
        """Get the path to the current log file."""
        if self.file_output:
            return self.log_dir / f"{self.name.lower()}.log"
        return None
    
    def clear_logs(self) -> bool:
        """Clear all log files."""
        try:
            if self.file_output:
                log_file = self.get_log_file_path()
                if log_file and log_file.exists():
                    log_file.unlink()
                
                # Clear backup files
                for i in range(1, self.backup_count + 1):
                    backup_file = log_file.with_suffix(f".log.{i}")
                    if backup_file.exists():
                        backup_file.unlink()
                
                self.info("Log files cleared")
                return True
            
            return False
            
        except Exception as e:
            self.error(f"Failed to clear logs: {str(e)}")
            return False
    
    def get_recent_logs(self, lines: int = 100) -> list[str]:
        """
        Get recent log entries.
        
        Args:
            lines (int): Number of recent lines to retrieve
            
        Returns:
            List[str]: Recent log entries
        """
        try:
            log_file = self.get_log_file_path()
            if not log_file or not log_file.exists():
                return []
            
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
                
        except Exception as e:
            self.error(f"Failed to read recent logs: {str(e)}")
            return []


class OperationLogger:
    """Context manager for logging operations with timing."""
    
    def __init__(self, logger: SimpleLogger, operation: str, 
                 file_path: Optional[str] = None):
        """
        Initialize operation logger.
        
        Args:
            logger (SimpleLogger): Logger instance
            operation (str): Operation name
            file_path (Optional[str]): File path for operation
        """
        self.logger = logger
        self.operation = operation
        self.file_path = file_path
        self.start_time = None
        self.success = False
    
    def __enter__(self):
        """Start operation logging."""
        self.start_time = datetime.now()
        self.logger.info(f"Starting operation: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End operation logging."""
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds() * 1000
            
            if exc_type is None:
                self.logger.log_operation(
                    self.operation, 
                    self.file_path, 
                    "SUCCESS",
                    f"Completed in {duration:.2f}ms"
                )
            else:
                self.logger.log_operation(
                    self.operation,
                    self.file_path,
                    "FAILED",
                    f"Failed after {duration:.2f}ms: {str(exc_val)}"
                )
    
    def add_details(self, details: str) -> None:
        """Add details to the operation log."""
        self.logger.debug(f"{self.operation} - {details}")


# Global logger instance
_global_logger: Optional[SimpleLogger] = None


def get_logger(name: str = "DocumentIntegritySystem") -> SimpleLogger:
    """Get or create global logger instance."""
    global _global_logger
    
    if _global_logger is None:
        _global_logger = SimpleLogger(name)
    
    return _global_logger


def setup_logger(log_level: LogLevel = LogLevel.INFO,
                 console_output: bool = True,
                 file_output: bool = True) -> SimpleLogger:
    """
    Setup global logging configuration.
    
    Args:
        log_level (LogLevel): Minimum log level
        console_output (bool): Enable console output
        file_output (bool): Enable file output
        
    Returns:
        SimpleLogger: Configured logger instance
    """
    global _global_logger
    
    _global_logger = SimpleLogger(
        log_level=log_level,
        console_output=console_output,
        file_output=file_output
    )
    
    return _global_logger


# Convenience functions
def log_info(message: str) -> None:
    """Log info message using global logger."""
    get_logger().info(message)


def log_error(message: str) -> None:
    """Log error message using global logger."""
    get_logger().error(message)


def log_warning(message: str) -> None:
    """Log warning message using global logger."""
    get_logger().warning(message)


def log_debug(message: str) -> None:
    """Log debug message using global logger."""
    get_logger().debug(message)


def log_operation(operation: str, file_path: Optional[str] = None, 
                 status: str = "SUCCESS", details: Optional[str] = None) -> None:
    """Log operation using global logger."""
    get_logger().log_operation(operation, file_path, status, details)


if __name__ == "__main__":
    # Example usage
    logger = SimpleLogger("TestLogger", log_level=LogLevel.DEBUG)
    
    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test operation logging
    logger.log_operation("TEST_OPERATION", "test_file.txt", "SUCCESS", "Test completed")
    
    # Test security event logging
    logger.log_security_event("FILE_ACCESS", "File accessed by user", "INFO", 
                            {"user": "admin", "file": "secret.txt"})
    
    # Test performance logging
    logger.log_performance("ENCRYPTION", 1250.5, 5.2)
    
    # Test operation context manager
    with OperationLogger(logger, "CONTEXT_TEST", "test.txt"):
        import time
        time.sleep(0.1)  # Simulate some work
        logger.info("Work completed inside context")
    
    print("✓ Logger testing completed. Check the log file in data/logs/")

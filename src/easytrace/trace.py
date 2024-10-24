import functools
import logging
import inspect
from typing import Callable, Any, Optional, TextIO

LOGGER_NAME = "easytrace"

LOG_LEVEL_MAP = {
    logging.CRITICAL: logging.getLogger(LOGGER_NAME).critical,
    logging.ERROR: logging.getLogger(LOGGER_NAME).error,
    logging.WARNING: logging.getLogger(LOGGER_NAME).warning,
    logging.INFO: logging.getLogger(LOGGER_NAME).info,
    logging.DEBUG: logging.getLogger(LOGGER_NAME).debug
}


class TraceConfig:
    stream : Optional[TextIO] = None
    logging_level : Optional[int] = logging.DEBUG

    def set_stream(stream: TextIO) -> None:
        """Set the global stream to log trace events to
        will be used regardless of stream parameter in @trace(...)

        Args:
            stream (TextIO): Stream to write trace events to
        """        
        TraceConfig.stream = stream

    def set_logging_level(logging_level: int) -> None:
        """Set the global logging level for the default logger used 
        this is overridden by the log_level parameter in @trace(...)

        Args:
            logging_level (int): Enum value for log level to use
        """      
        TraceConfig.logging_level = logging_level


def trace(func: Optional[Callable] = None, *, 
          enter: Optional[str] = None, 
          exit: Optional[str] = None,
          arg_value: bool = True, 
          return_value: bool = True, 
          log_level: Optional[int] = None,
          stream: Optional[TextIO] = None) -> Callable:
    """
    Easy tracing utility that logs the entry, exit, and optionally the arguments and return value of a function.

    Args:
        func (Optional[Callable]): The function to be decorated. If None, the decorator is returned with optional arguments.
        enter (Optional[str]): Custom log message for function entry. If None, a default message is generated.
        exit (Optional[str]): Custom log message for function exit. If None, a default message is generated.
        arg_value (bool): If True, logs the arguments passed to the function. Default is True.
        return_value (bool): If True, logs the return value of the function. Default is True.
        log_level (int): The logging level to use. Default is logging.DEBUG.

    Returns:
        Callable: The decorated function with logging on entry, exit, arguments, and return value.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(LOGGER_NAME)

            # Handle when a file object is passed for the logging
            handler_added = False
            stream_final = stream if stream is not None else TraceConfig.stream
            if stream_final is not None :
                try:
                    handler = logging.StreamHandler(stream_final)
                    logger.addHandler(handler)
                    handler_added = True
                except:
                    pass
            if log_level is not None:
                log = LOG_LEVEL_MAP.get(log_level, TraceConfig.logging_level)
            else:
                log = LOG_LEVEL_MAP.get(TraceConfig.logging_level, logging.DEBUG)

            # Log on function entry
            if enter is None:
                if arg_value:
                    sig = inspect.signature(func)
                    bound_args = sig.bind(*args, **kwargs)
                    bound_args.apply_defaults()

                    # Attempt to print name, value pairs. If we can't just print the parameter names
                    try:
                        str_cast = [(name, str(value)) for name, value in bound_args.arguments.items()]
                        arg_str = '(' + ', '.join([f"{name} : {type(value).__name__} = {str(value)}" for name, value in str_cast if value is not None]) + ')'
                    except:
                        arg_str = '(' + ', '.join([f"{name}" for name, _ in bound_args.arguments.items()]) + ')'
                else:
                    arg_str = ""
                log(f"call\t {func.__name__}{arg_str}")
            else:
                log(enter)

            # Actual function call
            result = func(*args, **kwargs)

            # Log after function has executed
            if exit is None:
                if return_value:
                    try:
                        log(f"return\t {func.__name__} -> {type(result).__name__} = {str(result)}")
                    except:
                        log(f"return\t {func.__name__} -> {type(result).__name__}")
                else:
                    log(f"return\t {func.__name__}")
            else:
                log(exit)

            if handler_added:
                logger.removeHandler(handler)

            return result
        return wrapper

    # If func is None, then no arguments    
    if func is None:
        return decorator
    else:
        return decorator(func)
    
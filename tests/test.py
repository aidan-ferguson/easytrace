from easytrace.trace import trace
from easytrace.trace import TraceConfig
import logging

# Define tracing config
TraceConfig.set_logging_level(logging.INFO)

# Set logging level to DEBUG, so we can see by default
logging.basicConfig(level=logging.DEBUG)
log_file = open("log.log", "w")

# Trace function with default options
@trace
def add_integers(a: int, b: int) -> int:
    return a + b

@trace(log_level=logging.DEBUG, stream=log_file)
def reverse_and_uppercase(s: str) -> str:
    return s[::-1].upper()

if __name__ == "__main__":
    # Should print entering the function with arguments 2, 3 and returning 5
    add_integers(2, 3)

    # This will log, at INFO level to both stdout and file
    reverse_and_uppercase("palindrome")
#!/usr/bin/env python3
"""Sample Python file for v57 testing"""

def hello_world() -> str:
    """Return a greeting"""
    return "Hello from Maximal Oracle v57!"

def fibonacci(n: int) -> int:
    """Calculate Fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

if __name__ == "__main__":
    print(hello_world())
    print(f"Fibonacci(10) = {fibonacci(10)}")

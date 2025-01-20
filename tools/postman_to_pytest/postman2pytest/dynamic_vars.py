"""
Dynamic variable storage for test execution.
"""
import pytest
import threading

class DynamicVars:
    """Thread-safe dynamic variable storage."""
    _instance = None
    _lock = threading.Lock()
    _storage = {}
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __getitem__(self, key):
        with self._lock:
            value = self._storage.get(key)
            print(f"\n=== Getting dynamic var: {key} -> {value} ===")
            print("Current state:", self._storage)
            return value
    
    def __setitem__(self, key, value):
        with self._lock:
            print(f"\n=== Setting dynamic var: {key} = {value} ===")
            self._storage[key] = value
            print("New state:", self._storage)
    
    def get(self, key, default=None):
        with self._lock:
            return self._storage.get(key, default)
    
    def clear(self):
        with self._lock:
            print("\n=== Clearing dynamic vars ===")
            print("Previous state:", self._storage)
            self._storage.clear()
            print("New state:", self._storage)

@pytest.fixture(scope="session")
def dynamic_vars():
    """Store dynamic variables that are set during test execution."""
    print("\n=== Creating dynamic vars fixture ===")
    vars_instance = DynamicVars()
    vars_instance.clear()  # Start fresh
    return vars_instance

def pytest_runtest_call(item):
    """Log test execution and dynamic variable state."""
    print(f"\n=== Running Test: {item.name} ===")
    print("Dynamic vars before test:", DynamicVars()._storage)

def pytest_runtest_makereport(item, call):
    """Log test result and dynamic variable state."""
    if call.when == "call":
        print(f"\n=== Test Complete: {item.name} ===")
        print("Dynamic vars after test:", DynamicVars()._storage)
        print("Test result:", call.excinfo if call.excinfo else "PASSED")

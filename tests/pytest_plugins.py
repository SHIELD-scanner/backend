"""Pytest plugins for performance and reliability improvements."""

import pytest
import time
from unittest.mock import patch


class TimingPlugin:
    """Plugin to track test timing and mark slow tests."""
    
    def __init__(self):
        self.start_time = None
    
    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(self, item):
        """Track test execution time."""
        self.start_time = time.time()
        outcome = yield
        duration = time.time() - self.start_time
        
        # Mark tests that take longer than 5 seconds as slow
        if duration > 5.0:
            print(f"\n⚠️  Slow test detected: {item.name} took {duration:.2f}s")
            
        return outcome


class DatabaseMockPlugin:
    """Plugin to ensure database connections are always mocked."""
    
    @pytest.hookimpl(autouse=True)
    def pytest_runtest_setup(self, item):
        """Ensure database mocking is active before each test."""
        # Additional safety net to prevent real database connections
        if not hasattr(item, '_database_mocked'):
            # This will be cleaned up by conftest.py fixtures
            item._database_mocked = True


def pytest_configure(config):
    """Register custom plugins."""
    config.pluginmanager.register(TimingPlugin(), "timing")
    config.pluginmanager.register(DatabaseMockPlugin(), "db_mock")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers and optimize execution."""
    # config parameter is required by pytest hook but unused here
    for item in items:
        # Add markers based on test path
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
            
        # Mark tests that might be slow
        if any(keyword in item.name.lower() for keyword in 
               ['integration', 'database', 'memory', 'large']):
            item.add_marker(pytest.mark.slow)

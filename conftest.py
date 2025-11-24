import pytest
import os
import django
from django.conf import settings

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DevOpsDemo.settings')


def pytest_configure(config):
    """Configure pytest for Django"""
    if not settings.configured:
        django.setup()


@pytest.fixture(scope='session')
def django_db_setup():
    """Set up test database"""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }

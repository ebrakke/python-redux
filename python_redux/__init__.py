"""
A Redux library for Python
~~~~~~~~~~~~~~~~~~~~~~~~~~

Redux is a library for application state mangement.  It was originally written in Javascript by Dan Abramov

Example Usage:

:license: MIT, see LICENSE for more details
"""

__title__ = 'redux'
__version__ = '1.0'
__author__ = 'Erik Brakke'
__license__ = 'MIT'

from .api import create_store, apply_middleware, bind_action_creators, combine_reducers, compose
from .models import Store

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())


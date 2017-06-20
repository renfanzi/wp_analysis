# -*- coding: utf-8 -*-

import os

def load_config():
#    mode = os.environ.get('MODE')
    mode = 'TESTING'
    try:
        if mode == 'PRODUCTION':
            from production import ProdctionConfig
            return ProductionConfig
        elif mode == 'TESTING':
            from testing import TestingConfig
            return TestingConfig
        else:
            from development import DevelopmentConfig
            return DevelopmentConfig
    except ImportError, e:
        from default import Config
        return Config

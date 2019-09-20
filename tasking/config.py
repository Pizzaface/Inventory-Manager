# config.py (app.tasking.config)

import os
from huey import RedisHuey


settings__development = {
    'host': 'localhost'
}

settings__testing = {
    'host': 'localhost'
}

settings__production = {
    'host': 'production_server'
}

settings = {
    'development': settings__development,
    'testing': settings__testing,
    'production': settings__production,
    'default': settings__development
}

huey = RedisHuey(**settings[os.getenv('FLASK_ENV') or 'default'])
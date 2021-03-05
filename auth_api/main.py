#!/usr/bin/env python3
import argparse
import logging
import os
import toml
from datetime import datetime

from fastapi import FastAPI
import asyncpg
import pytz
import uvicorn
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from .routers import (
    users,
)

from .deps import (
    logger,
)

import auth_api.deps as deps

from .lib_cfg import (config)

import auth_api.lib_misc as lm


# ################################################## SETUP AND ARGUMENT PARSING
# #############################################################################
dir_path = os.path.dirname(os.path.realpath(__file__))


VERSION = 1
START_TIME = datetime.now(pytz.utc)
ACCESS_TOKEN_EXPIRE_MINUTES = 30

tags_metadata = [
    {
        "name": "authentication",
        "description": "Login, logout, etc."
    },
]
# ############################################ SERVER ROUTES
# #############################################################################


app = FastAPI(root_path=config.key('proxy_prefix'), openapi_tags=tags_metadata)

# Include sub routes
app.include_router(users.router)

# Server config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    if os.getenv('NO_ASYNCPG', 'false') == 'false':
        try:
            cfg = config.key('postgresql')
            deps.DB_POOL = await asyncpg.create_pool(**cfg)
        except asyncpg.InvalidPasswordError:
            if config.key('log_level') != 'debug':
                logger.critical("No database found")
                raise
            logger.warning("No Database Found !!!! But we're in debug mode, proceeding anyway")
            deps.DB_POOL = False

# ############################################################### SERVER ROUTES
# #############################################################################


@app.get("/")
def root():
    return lm.status_get(START_TIME, VERSION)


# ##################################################################### STARTUP
# #############################################################################
def main():
    parser = argparse.ArgumentParser(description='Matching server process')
    parser.add_argument('--config', dest='config', help='config file', default=None)
    parser.add_argument('--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    args = parser.parse_args()

    # XXX: Lambda is a hack : toml expects a callable
    if args.config:
        t_config = toml.load(['config_default.toml', args.config])
    else:
        t_config = toml.load('config_default.toml')

    config.merge(t_config)

    if args.debug:
        logger.setLevel(logging.getLevelName('DEBUG'))
        logger.debug('Debug activated')
        config.set('log_level', 'debug')
        config.set(['server', 'log_level'], 'debug')
        logger.debug('Arguments: %s', args)
        config.dump(logger)

        logger.debug('config: %s', toml.dumps(config._config))

        uvicorn.run(
            "auth_api.main:app",
            reload=True,
            **config.key('server')
        )
    uvicorn.run(
        app,
        **config.key('server')
    )


if __name__ == "__main__":
    main()

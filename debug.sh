#!/bin/sh
cd $(dirname $0)
export AIOREDIS_DEBUG=1
export DEBUG=1
exec ./run_game.sh

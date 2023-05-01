#!/bin/sh

set -e

uvicorn app.server:app --host 0.0.0.0 --port 8001 --reload

#!/bin/bash

set -e

LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1 python process.py
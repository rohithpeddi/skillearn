#!/bin/bash
# Kill the running backend if any
ps -ef | grep flaskserver.py | awk '{print $2}' | xargs kill | exit

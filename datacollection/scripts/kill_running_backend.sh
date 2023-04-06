#!/bin/bash
# Kill the running backend if any
ps -ef | grep python | awk '{print $2}' | xargs kill | exit

#!/bin/bash -e

rm -f ecs-event-monitor.zip
rm -rf build
mkdir build
cp -a src/* build
# https://github.com/pypa/pip/issues/3826
# --system is required as otherwise defaults to --user
# which clashes with -t (--target)
pip install --system -r build/requirements.txt -t build
(cd build; zip -r ../ecs-event-monitor.zip *)
ls -l ecs-event-monitor.zip

#!/bin/bash -e

rm -f ecs-event-monitor.zip
rm -rf build
mkdir build
cp -a src/* build
(cd build; zip -r ../ecs-event-monitor.zip *)
ls -l ecs-event-monitor.zip

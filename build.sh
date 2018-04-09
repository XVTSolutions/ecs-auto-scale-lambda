#!/bin/bash -e

rm -f ecs_auto_scale.zip
rm -rf build
mkdir build
cp -a src/* build
(cd build; zip -r ../ecs_auto_scale.zip *)
ls -l ecs_auto_scale.zip

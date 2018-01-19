#!/bin/bash -e

rm -f ecs-auto-scale.zip
rm -rf build
mkdir build
cp -a src/* build
(cd build; zip -r ../ecs-auto-scale.zip *)
ls -l ecs-auto-scale.zip

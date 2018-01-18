#!/bin/bash

read AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN < <(python ~/assumerole.py arn:aws:iam::${bamboo_build_account_id}:role/bamboo_s3_push "${bamboo.buildResultKey}")
export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN

aws s3 cp ecs-event-monitor.zip s3://xvt-infra-build/
aws lambda update-function-code --function-name ${bamboo_cluster_name}-ecs-event-monitor --s3-bucket xvt-infra-build --s3-key ecs-event-monitor.zip

#!/bin/bash

read AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN < <(python ~/assumerole.py arn:aws:iam::${bamboo_build_account_id}:role/bamboo_s3_push "${bamboo.buildResultKey}")
export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN

aws s3 cp ecs_auto_scale.zip s3://${bamboo_build_account_name}-infra-build/
aws lambda update-function-code --function-name ${bamboo_cluster_name}-ecs_auto_scale --s3-bucket ${bamboo_build_account_name}-infra-build --s3-key ecs_auto_scale.zip

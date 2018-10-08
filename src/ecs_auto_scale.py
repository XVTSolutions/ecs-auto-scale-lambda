#!/usr/bin/env python3

import boto3
import datetime
import os
import sys


# https://stackoverflow.com/a/434328/3538079
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def lambda_handler(event, context):
    autoscaling = boto3.session.Session().client('autoscaling', region_name='ap-southeast-2')
    asg_name = os.environ.get('AUTO_SCALING_GROUP')
    asg = autoscaling.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])['AutoScalingGroups'][0]

    # Are we already at capacity?
    if asg['MaxSize'] == 0 or asg['DesiredCapacity'] == asg['MaxSize']:
        message = "Already at capacity"
        print(message)
        return dict(message=message)

    # Are we already scaling the ASG?
    if [instance for instance in asg['Instances']
            if instance["LifecycleState"] == "Pending:Wait"]:
        message = "ASG auto scaling in progress"
        print(message)
        return dict(message=message)

    ecs = boto3.session.Session().client('ecs', region_name='ap-southeast-2')
    cluster = os.environ.get('ECS_CLUSTER')

    container_instance_arns = ecs.list_container_instances(cluster=cluster)['containerInstanceArns']
    container_instances = ecs.describe_container_instances(cluster=cluster, containerInstances=container_instance_arns)['containerInstances']

    # Are any existing ECS instances doing nothing?
    for instance in container_instances:
        if not instance['runningTasksCount']:
            uptime = (datetime.datetime.now(datetime.timezone.utc) - instance['registeredAt']).seconds
            message = "ECS container instance %s not running any tasks: uptime %d seconds" % (instance['ec2InstanceId'], uptime)
            print(message)
            return dict(message=message)

    service_arns = ecs.list_services(cluster=cluster)['serviceArns']
    services = []
    # describe_services has a max length of 10 services
    for chunk in chunker(service_arns, 10):
        services.extend(ecs.describe_services(cluster=cluster, services=chunk)['services'])

    for service in services:
        if datetime.datetime.now(datetime.timezone.utc) - service['createdAt'] > datetime.timedelta(minutes=1):
            if service['runningCount'] >= 1 and service['pendingCount'] >= 1:
                transient_state_desired_count = service['runningCount'] + service['pendingCount'] + service['desiredCount']
            else:
                transient_state_desired_count = service['desiredCount']
            if service['runningCount'] + service['pendingCount'] < transient_state_desired_count:
                autoscaling.set_desired_capacity(AutoScalingGroupName=asg_name, DesiredCapacity=asg['DesiredCapacity'] + 1)
                message = "Updating asg %s desired capacity to %d" % (asg_name, asg['DesiredCapacity'] + 1)
                print(message)
                return dict(message=message)
    message = "Everything is awesome, nothing to do"
    print(message)
    return dict(message=message)


if __name__ == '__main__':
    message = lambda_handler(None, None)
    print(message)

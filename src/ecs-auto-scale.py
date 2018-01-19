#!/usr/bin/env python3

import boto3
import datetime
import os


# https://stackoverflow.com/a/434328/3538079
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def lambda_handler(event, context):
    autoscaling = boto3.session.Session().client('autoscaling', region_name='ap-southeast-2')
    asg_name = os.environ.get('AUTO_SCALING_GROUP')
    asg = autoscaling.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])['AutoScalingGroups'][0]

    # Are we already at capacity?
    if asg['MaxSize'] == 0 or asg['DesiredCapacity'] == asg['MaxSize']:
        raise SystemExit()

    ecs = boto3.session.Session().client('ecs', region_name='ap-southeast-2')
    service_arns = ecs.list_services(cluster=os.environ.get('CLUSTER'))['serviceArns']

    services = []

    # describe_services has a max length of 10 services
    for chunk in chunker(service_arns, 10):
        services.extend(ecs.describe_services(cluster=os.environ.get('CLUSTER'), services=chunk)['services'])

    for service in services:
        if datetime.datetime.now(datetime.timezone.utc) - service['createdAt'] > datetime.timedelta(minutes=1):
            if service['runningCount'] + service['pendingCount'] < service['desiredCount']:
                print("Updating asg %s desired capacity to %d" % (asg_name, asg['DesiredCapacity'] + 1))
                autoscaling.set_desired_capacity(AutoScalingGroupName=asg_name, DesiredCapacity=asg['DesiredCapacity'] + 1)


if __name__ == '__main__':
    lambda_handler(None, None)

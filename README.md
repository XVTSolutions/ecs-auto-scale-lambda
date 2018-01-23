# ecs-auto-scale-lambda

## Motivation

ecs-auto-scale-lambda runs on AWS Lambda looking for ECS clusters
that need scaling out.

Although standard EC2 auto scaling will work fine in certain conditions,
there can be a gap where the auto scaling alarm does not breach but there
is no capacity to run a particular task.

Consider the following conditions:
* ECS agents auto scale out when memory breaches 75% of capacity
* There is one 4GB ECS agent currently, running one 2GB container
* A new task is scheduled to run one 3GB container

The 3GB container will never be scheduled through standard auto scaling.
As far as I'm aware, there are no events fired when this scenario occurs
and there are no metrics that can be measured to create an alarm on this
scenario.

## Algorithm

The lambda can run on a schedule (e.g. every 5 minutes) and performs
the following algorithm:

* If the ASG is already at max capacity, do nothing
* If the ASG is currently scaling out, do nothing
* If there is a container instance starting up, do nothing
* If for any service, the desired count is greater than the
  sum of running count and pending count, increase ASG
  desired capacity by 1.

This assumes that the only reason that desired count is not
in progress of being achieved is due to lack of capacity on
the existing container instances. That assumption may not
be valid.

import json

def lambda_handler(event, context):
    if event["source"] != "aws.ecs":
       raise SystemExit()

    print(json.dumps(event))

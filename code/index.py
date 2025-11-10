import boto3
import datetime
import os

# Available methods: stop or terminate, anything else means only notification
method = os.getenv("METHOD", "log")
max_age = int(os.getenv("MAX_AGE", 24))

client = boto3.client("ec2")


def lambda_handler(event, context):
    try:
        response = client.describe_instances(
            Filters=[
                {"Name": "key-name", "Values": ["packer_*"]},
                {"Name": "tag:Name", "Values": ["Packer Builder"]},
                {
                    "Name": "instance-state-name",
                    "Values": ["stopped", "running"],
                },
            ]
        )
        instances_to_terminate = []
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                launchTime = instance["LaunchTime"]
                tz_info = launchTime.tzinfo
                now = datetime.datetime.now(tz_info)
                delta = datetime.timedelta(hours=max_age)
                the_past = now - delta
                # If the instance was launched more than the max_age ago,
                # get rid of it
                if the_past > instance["LaunchTime"]:
                    instances_to_terminate.append(instance["InstanceId"])

        if len(instances_to_terminate) > 0:
            print("These instances have existed too long: ")
            print(instances_to_terminate)
            # Decide how to handle the instances
            if method == "stop":
                client.stop_instances(InstanceIds=instances_to_terminate)
            elif method == "terminate":
                client.terminate_instances(InstanceIds=instances_to_terminate)

    except Exception as e:
        print(e)
        raise e


if __name__ == "__main__":
    event = []
    context = []
    lambda_handler(event, context)

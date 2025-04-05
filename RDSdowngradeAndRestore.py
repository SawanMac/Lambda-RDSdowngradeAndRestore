import boto3
import os
from datetime import datetime, timedelta

# Initialize AWS clients
rds_client = boto3.client('rds')
cloudwatch_client = boto3.client('cloudwatch')

# Environment variables
MAINTENANCE_WINDOW = os.environ.get('MAINTENANCE_WINDOW', 'Mon:00:00-Mon:03:00')
TARGET_INSTANCE_CLASS = os.environ.get('TARGET_INSTANCE_CLASS', 'db.t3.small')
CPU_THRESHOLD = float(os.environ.get('CPU_THRESHOLD', 20.0))  # Default: 20%

# Dictionary to store original instance classes
original_instance_classes = {}

def lambda_handler(event, context):
    """
    Lambda function to downgrade RDS instances when CPU utilization is low
    and the current time is within the maintenance window. Restores the
    instance to its original class before the end of the maintenance window.
    """
    # Get the list of RDS instances
    instances = rds_client.describe_db_instances()['DBInstances']

    for instance in instances:
        instance_id = instance['DBInstanceIdentifier']
        current_instance_class = instance['DBInstanceClass']

        # Skip if the instance is already at the target class
        if current_instance_class == TARGET_INSTANCE_CLASS:
            print(f"Instance {instance_id} is already at the target class ({TARGET_INSTANCE_CLASS}). Skipping.")
            continue

        # Check CPU utilization
        if is_cpu_utilization_low(instance_id):
            # Check if the current time is within the maintenance window
            if is_within_maintenance_window():
                # Store the original instance class
                original_instance_classes[instance_id] = current_instance_class

                # Downgrade the instance
                downgrade_instance(instance_id)
            else:
                print(f"Current time is outside the maintenance window. Skipping downgrade for {instance_id}.")
        else:
            print(f"CPU utilization is above the threshold for {instance_id}. Skipping downgrade.")

    # Restore instances to their original class before the end of the maintenance window
    restore_instances_to_original_class()

def is_cpu_utilization_low(instance_id):
    """
    Check if the CPU utilization of the instance is below the threshold.
    """
    # Get CPU utilization metrics from CloudWatch
    response = cloudwatch_client.get_metric_statistics(
        Namespace='AWS/RDS',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': instance_id}],
        StartTime=datetime.utcnow() - timedelta(minutes=10),
        EndTime=datetime.utcnow(),
        Period=300,
        Statistics=['Average']
    )
    datapoints = response.get('Datapoints', [])
    if not datapoints:
        print(f"No CPU utilization data available for {instance_id}.")
        return False

    # Check if the average CPU utilization is below the threshold
    avg_cpu_utilization = datapoints[0]['Average']
    print(f"CPU utilization for {instance_id}: {avg_cpu_utilization}%")
    return avg_cpu_utilization < CPU_THRESHOLD

def is_within_maintenance_window():
    """
    Check if the current time is within the maintenance window.
    """
    # Parse the maintenance window
    day_start, time_start, day_end, time_end = MAINTENANCE_WINDOW.split('-')
    now = datetime.utcnow()
    start_time = datetime.strptime(f"{day_start}:{time_start}", "%a:%H:%M")
    end_time = datetime.strptime(f"{day_end}:{time_end}", "%a:%H:%M")

    # Adjust the start and end times to the current week
    start_time = start_time.replace(year=now.year, month=now.month, day=now.day)
    end_time = end_time.replace(year=now.year, month=now.month, day=now.day)

    # Handle cases where the maintenance window spans midnight
    if end_time < start_time:
        end_time += timedelta(days=1)

    return start_time <= now <= end_time

def downgrade_instance(instance_id):
    """
    Downgrade the RDS instance to the target instance class.
    """
    print(f"Downgrading instance {instance_id} to {TARGET_INSTANCE_CLASS}.")
    rds_client.modify_db_instance(
        DBInstanceIdentifier=instance_id,
        DBInstanceClass=TARGET_INSTANCE_CLASS,
        ApplyImmediately=True
    )

def restore_instances_to_original_class():
    """
    Restore RDS instances to their original instance class before the end of the maintenance window.
    """
    for instance_id, original_class in original_instance_classes.items():
        print(f"Restoring instance {instance_id} to its original class ({original_class}).")
        rds_client.modify_db_instance(
            DBInstanceIdentifier=instance_id,
            DBInstanceClass=original_class,
            ApplyImmediately=True
        )
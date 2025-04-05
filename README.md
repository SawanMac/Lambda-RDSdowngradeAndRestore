# Lambda-RDSdowngradeAndRestore
# RDS Downgrade Lambda Function

This project contains an AWS Lambda function that automatically downgrades RDS instances when their CPU utilization is below a specified threshold and the current time is within a defined maintenance window. It also includes unit tests for the Lambda function.

## Files

- **`Lambda-RDSdowngrade.py`**: The main Lambda function that performs the RDS instance downgrade.
- **`test_Lambda-RDSdowngrade.py`**: Unit tests for the Lambda function using the `unittest` framework.

## Features

- Automatically downgrades RDS instances to a target instance class.
- Checks CPU utilization using CloudWatch metrics.
- Ensures downgrades occur only within a specified maintenance window.

## Environment Variables

The Lambda function uses the following environment variables:

- **`MAINTENANCE_WINDOW`**: The maintenance window during which downgrades are allowed (e.g., `Mon:00:00-Mon:03:00`).
- **`TARGET_INSTANCE_CLASS`**: The target RDS instance class for downgrades (e.g., `db.t3.small`).
- **`CPU_THRESHOLD`**: The CPU utilization threshold below which downgrades are triggered (default: `20.0`).

## How It Works

1. The Lambda function retrieves a list of RDS instances using the AWS SDK.
2. For each instance:
   - Skips if the instance is already at the target class.
   - Checks if the CPU utilization is below the threshold.
   - Verifies if the current time is within the maintenance window.
   - Downgrades the instance if all conditions are met.

## Unit Tests

The unit tests mock AWS SDK calls and helper functions to test the Lambda function's behavior under various scenarios.

### Running Tests

1. Install the required dependencies:
   ```bash
   pip install boto3
2. Run the tests:
   python -m unittest test_Lambda-RDSdowngrade.py

**Deployment**
Package the Lambda function and its dependencies.
Deploy the function to AWS Lambda.
Set the required environment variables

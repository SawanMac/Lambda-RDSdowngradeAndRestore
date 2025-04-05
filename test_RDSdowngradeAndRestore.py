import unittest
from unittest.mock import patch, MagicMock
from RDSdowngradeAndRestore import (
    lambda_handler,
    downgrade_instance,
    restore_instances_to_original_class,
    original_instance_classes
)

class TestRDSDowngradeAndRestore(unittest.TestCase):
    @patch('RDSdowngradeAndRestore.boto3.client')
    @patch.dict('os.environ', {
        'AWS_ACCESS_KEY_ID': 'mock_access_key',
        'AWS_SECRET_ACCESS_KEY': 'mock_secret_key',
        'AWS_REGION': 'us-east-1'
    })
    def test_downgrade_instance(self, mock_boto_client):
        # Mock RDS client
        mock_rds_client = MagicMock()
        mock_boto_client.return_value = mock_rds_client

        # Test the downgrade_instance function
        downgrade_instance('test-instance')
        mock_rds_client.modify_db_instance.assert_called_once_with(
            DBInstanceIdentifier='test-instance',
            DBInstanceClass='db.t3.small',
            ApplyImmediately=True
        )

    @patch('RDSdowngradeAndRestore.boto3.client')
    @patch.dict('os.environ', {
        'AWS_ACCESS_KEY_ID': 'mock_access_key',
        'AWS_SECRET_ACCESS_KEY': 'mock_secret_key',
        'AWS_REGION': 'us-east-1'
    })
    def test_restore_instances_to_original_class(self, mock_boto_client):
        # Mock RDS client
        mock_rds_client = MagicMock()
        mock_boto_client.return_value = mock_rds_client

        # Mock original_instance_classes
        original_instance_classes['test-instance'] = 'db.t3.medium'

        # Test the restore_instances_to_original_class function
        restore_instances_to_original_class()
        mock_rds_client.modify_db_instance.assert_called_once_with(
            DBInstanceIdentifier='test-instance',
            DBInstanceClass='db.t3.medium',
            ApplyImmediately=True
        )

    @patch('RDSdowngradeAndRestore.boto3.client')
    @patch.dict('os.environ', {
        'AWS_ACCESS_KEY_ID': 'mock_access_key',
        'AWS_SECRET_ACCESS_KEY': 'mock_secret_key',
        'AWS_REGION': 'us-east-1'
    })
    @patch('RDSdowngradeAndRestore.is_cpu_utilization_low', return_value=True)
    @patch('RDSdowngradeAndRestore.is_within_maintenance_window', return_value=True)
    @patch('RDSdowngradeAndRestore.downgrade_instance')
    @patch('RDSdowngradeAndRestore.restore_instances_to_original_class')
    def test_lambda_handler(self, mock_restore, mock_downgrade, mock_maintenance, mock_cpu, mock_boto_client):
        # Mock RDS client
        mock_rds_client = MagicMock()
        mock_boto_client.return_value = mock_rds_client

        # Mock describe_db_instances response
        mock_rds_client.describe_db_instances.return_value = {
            'DBInstances': [{'DBInstanceIdentifier': 'test-instance', 'DBInstanceClass': 'db.t3.large'}]
        }

        # Mock original_instance_classes to simulate a previous downgrade
        original_instance_classes['test-instance'] = 'db.t3.medium'

        # Test the lambda_handler function
        lambda_handler({}, {})

        # Ensure downgrade_instance is called
        mock_downgrade.assert_called_once_with('test-instance')

        # Ensure restore_instances_to_original_class is called
        mock_restore.assert_called_once()
import unittest
from unittest.mock import patch, MagicMock
from RDSdowngradeAndRestore import (
    lambda_handler,
    is_cpu_utilization_low,
    is_within_maintenance_window,
    downgrade_instance,
    restore_instances_to_original_class,
    original_instance_classes
)

class TestRDSDowngradeAndRestore(unittest.TestCase):
    @patch('RDSdowngradeAndRestore.rds_client')
    @patch('RDSdowngradeAndRestore.cloudwatch_client')
    def test_lambda_handler(self, mock_cloudwatch, mock_rds):
        # Mock RDS describe_db_instances response
        mock_rds.describe_db_instances.return_value = {
            'DBInstances': [
                {'DBInstanceIdentifier': 'test-instance', 'DBInstanceClass': 'db.t3.medium'}
            ]
        }

        # Mock CPU utilization check
        with patch('RDSdowngradeAndRestore.is_cpu_utilization_low', return_value=True):
            # Mock maintenance window check
            with patch('RDSdowngradeAndRestore.is_within_maintenance_window', return_value=True):
                # Mock downgrade instance
                with patch('RDSdowngradeAndRestore.downgrade_instance') as mock_downgrade:
                    # Mock restore instances
                    with patch('RDSdowngradeAndRestore.restore_instances_to_original_class') as mock_restore:
                        lambda_handler({}, {})
                        mock_downgrade.assert_called_once_with('test-instance')
                        mock_restore.assert_called_once()

    @patch('RDSdowngradeAndRestore.rds_client')
    def test_downgrade_instance(self, mock_rds):
        # Test the downgrade_instance function
        downgrade_instance('test-instance')
        mock_rds.modify_db_instance.assert_called_once_with(
            DBInstanceIdentifier='test-instance',
            DBInstanceClass='db.t3.small',
            ApplyImmediately=True
        )

    @patch('RDSdowngradeAndRestore.rds_client')
    def test_restore_instances_to_original_class(self, mock_rds):
        # Mock original_instance_classes
        original_instance_classes['test-instance'] = 'db.t3.medium'

        # Test the restore_instances_to_original_class function
        restore_instances_to_original_class()
        mock_rds.modify_db_instance.assert_called_once_with(
            DBInstanceIdentifier='test-instance',
            DBInstanceClass='db.t3.medium',
            ApplyImmediately=True
        )

if __name__ == '__main__':
    unittest.main()
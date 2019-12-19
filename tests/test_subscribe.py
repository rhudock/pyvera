import json
import logging

import unittest.mock as mock
import pyvera

logging.basicConfig(level=logging.DEBUG)
pyvera.logger = logging.getLogger(__name__)


class TestSubscriptionRegistry:
    def test__event_device_for_vera_lock_status(self):

        sr = pyvera.SubscriptionRegistry()
        mock_lock = mock.create_autospec(pyvera.VeraLock)
        mock_lock.name = mock.MagicMock(return_value="MyTestDeadbolt")

        # Deadbolt changing but not done
        device_json = json.loads(
            "{"
            # subscribe.STATE_JOB_IN_PROGRESS
            '  "state": "1"'
            "}"
        )
        sr._event_device(mock_lock, device_json, [])
        mock_lock.update.assert_not_called()

        # Deadbolt progress with reset state but not done
        device_json = json.loads(
            "{"
            # subscribe.STATE_NO_JOB
            '  "state": "-1",'
            '  "comment": "MyTestDeadbolt: Sending the Z-Wave command after 0 retries"'
            "}"
        )
        sr._event_device(mock_lock, device_json, [])
        mock_lock.update.assert_not_called()

        # Deadbolt progress locked but not done
        device_json = json.loads(
            "{"
            # subscribe.STATE_JOB_IN_PROGRESS
            '  "state": "1",'
            '  "locked": "1",'
            '  "comment": "MyTestDeadbolt"'
            "}"
        )
        sr._event_device(mock_lock, device_json, [])
        mock_lock.update.assert_not_called()

        # Deadbolt progress with status but not done
        device_json = json.loads(
            "{"
            # subscribe.STATE_JOB_IN_PROGRESS
            '  "state": "1",'
            '  "comment": "MyTestDeadbolt: Please wait! Polling node"'
            "}"
        )
        sr._event_device(mock_lock, device_json, [])
        mock_lock.update.assert_not_called()

        # Deadbolt progress complete
        device_json = json.loads(
            "{"
            # subscribe.STATE_JOB_IN_PROGRESS
            '  "state": "1",'
            '  "locked": "1",'
            '  "comment": "MyTestDeadbolt: SUCCESS! Successfully polled node",'
            '  "deviceInfo": {'
            # pyvera.CATEGORY_LOCK
            '    "category": 7'
            "  }"
            "}"
        )
        sr._event_device(mock_lock, device_json, [])
        mock_lock.update.assert_called_once_with(device_json)
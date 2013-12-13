# -*- coding: utf-8 -*-

import unittest
from unittest import TestCase
import json

from mock import patch

from geotrigger import GeotriggerClient, GeotriggerDevice, \
    GeotriggerApplication, __version__
from geotrigger.session import GeotriggerSession, GEOTRIGGER_BASE_URL, \
    AGO_TOKEN_ROUTE


class GeotriggerClientTestCase(TestCase):
    """
    Tests for the `GeotriggerClient` class.
    """

    def setUp(self):
        self.client_id = 'test_client_id'
        self.client_secret = 'test_client_secret'
        self.device_id = 'test_device_id'
        self.access_token = 'test_access_token'
        self.refresh_token = 'test_refresh_token'
        self.expires_in = 'test_expires_in'

    @patch.object(GeotriggerDevice, 'register')
    def test_device_init(self, mock_register):
        """
        Test initialization of the `GeotriggerClient` as a device.
        """
        mock_register.return_value = {
            'device_id': self.device_id,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_in': self.expires_in
        }
        gt = GeotriggerClient(client_id=self.client_id)

        self.assertIsNotNone(gt.session)
        self.assertTrue(gt.session.is_device())
        self.assertEqual(gt.session.client_id, self.client_id)
        gt.session.register.assert_called_once()


    @patch.object(GeotriggerDevice, 'register')
    def test_device_init_manual(self, mock_register):
        gt = GeotriggerClient(session=GeotriggerDevice(self.client_id,
                                                       self.device_id,
                                                       self.access_token,
                                                       self.refresh_token,
                                                       self.expires_in))
        self.assertIsNotNone(gt.session)
        self.assertTrue(gt.session.is_device())
        self.assertEqual(gt.session.client_id, self.client_id)
        self.assertEqual(gt.session.register.call_count, 0)

    @patch.object(GeotriggerApplication, 'request_token')
    def test_application_init(self, mock_request_token):
        """
        Test initialization of the 'GeotriggerClient` as an application.
        """
        mock_request_token.return_value = {
            'access_token': self.access_token,
            'expires_in': self.expires_in
        }
        gt = GeotriggerClient(client_id=self.client_id,
                              client_secret=self.client_secret)

        self.assertIsNotNone(gt.session)
        self.assertTrue(gt.session.is_application())
        self.assertEqual(gt.session.client_id, self.client_id)
        gt.session.request_token.assert_called_once()

    @patch.object(GeotriggerApplication, 'request_token')
    def test_application_init_manual(self, mock_request_token):
        gt = GeotriggerClient(session=GeotriggerApplication(self.client_id,
                                                            self.client_secret,
                                                            self.access_token,
                                                            self.expires_in))
        self.assertIsNotNone(gt.session)
        self.assertTrue(gt.session.is_application())
        self.assertEqual(gt.session.client_id, self.client_id)
        self.assertEqual(gt.session.request_token.call_count, 0)


class GeotriggerDeviceTestCase(TestCase):
    """
    Tests for the `GeotriggerDevice` class.
    """

    def setUp(self):
        self.client_id = 'device_client_id'
        self.device_id = 'device_device_id'
        self.access_token = 'device_access_token'
        self.refresh_token = 'device_refresh_token'
        self.expires_in = 'device_expires_in'
        self.tag = 'device_tag'

        self.geotrigger_headers = {
            'X-GT-Client-Name': 'geotrigger-python',
            'X-GT-Client-Version': __version__,
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }

        with patch.object(GeotriggerDevice, 'register') as mock_register:
            mock_register.return_value = {
                'device_id': self.device_id,
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'expires_in': self.expires_in
            }

            with patch.object(GeotriggerSession, 'post') as mock_post:
                self.client = GeotriggerDevice(self.client_id)

    @patch.object(GeotriggerDevice, 'register')
    @patch.object(GeotriggerSession, 'post')
    def test_register(self, mock_request, mock_register):
        """
        Test device registration with ArcGIS Online.
        """
        # Device should be registered from setUp
        device = self.client

        # Sanity
        self.assertTrue(device.is_device())
        self.assertFalse(device.is_application())

        # Make sure we set all properties from registration response
        self.assertEqual(device.device_id, self.device_id)
        self.assertEqual(device.access_token, self.access_token)
        self.assertEqual(device.refresh_token, self.refresh_token)
        self.assertEqual(device.expires_in, self.expires_in)

        # Ensure `register` is only called once
        device.register.assert_called_once()

        # Device credentials given, registration should not occur
        device2 = GeotriggerDevice(self.client_id, 'device_id',
                                   'access_token', 'refresh_token',
                                   'expires_in')

        # `register` should not have been called
        self.assertEqual(device2.register.call_count, 0)

    @patch.object(GeotriggerSession, 'post')
    def test_geotrigger_request(self, mock_request):
        """
        Test creation of Geotrigger API requests.
        """
        # make a call via the `geotrigger_post` method
        data = {'tags': self.tag}
        url = 'trigger/list'
        self.client.geotrigger_request(url, data=data)

        # ensure that the `request` method is called with the correct parameters
        self.client.post.assert_called_once_with(
            GEOTRIGGER_BASE_URL + url,
            data=json.dumps(data),
            headers=self.geotrigger_headers
        )

    @patch.object(GeotriggerSession, 'ago_request')
    def test_refresh(self, mock_ago_request):
        """
        Test refresh of expired access tokens.
        """
        new_token = 'new_token'
        new_expires = 'new_expires_in'
        mock_ago_request.return_value = {
            'access_token': new_token,
            'expires_in': new_expires
        }

        old_token = self.client.access_token
        old_expires = self.client.expires_in

        # sanity
        self.assertEqual(self.access_token, old_token)
        self.assertEqual(self.expires_in, old_expires)

        # call refresh
        self.client.refresh()

        # check refresh request
        self.client.ago_request.assert_called_once_with(
            AGO_TOKEN_ROUTE,
            {
                'client_id': self.client_id,
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token',
                'f': 'json'
            }
        )

        # check token
        self.assertEqual(self.client.access_token, new_token)
        self.assertEqual(self.client.expires_in, new_expires)


class GeotriggerApplicationTestCase(TestCase):
    """
    Tests for the GeotriggerApplication class.
    """

    def setUp(self):
        self.client_id = 'app_client_id'
        self.access_token = 'app_access_token'
        self.client_secret = 'app_client_secret'
        self.expires_in = 'app_expires_in'
        self.geotrigger_headers = {
            'X-GT-Client-Name': 'geotrigger-python',
            'X-GT-Client-Version': __version__,
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }

        with patch.object(GeotriggerApplication,
                          'request_token') as mock_request_token:
            mock_request_token.return_value = {
                'access_token': self.access_token,
                'expires_in': self.expires_in
            }

            with patch.object(GeotriggerSession, 'post') as mock_request:
                self.client = GeotriggerApplication(self.client_id,
                                                    self.client_secret)

    @patch.object(GeotriggerApplication, 'request_token')
    @patch.object(GeotriggerSession, 'post')
    def test_request_token(self, mock_post, mock_request_token):
        """
        Test application token requests to ArcGIS Online.
        """
        # App should be registered from setUp
        app = self.client

        # Sanity
        self.assertTrue(app.is_application())
        self.assertFalse(app.is_device())
        self.assertIsNone(app.device_id)
        self.assertIsNone(app.refresh_token)

        # Make sure we set all properties from token response
        self.assertEqual(app.client_id, self.client_id)
        self.assertEqual(app.access_token, self.access_token)
        self.assertEqual(app.client_secret, self.client_secret)
        self.assertEqual(app.expires_in, self.expires_in)

        # Ensure `request_token` only called once
        app.request_token.assert_called_once()

        # App credentials given, token request should not occur
        app2 = GeotriggerApplication(self.client_id, self.client_secret,
                                     'access_token', 'expires_in')

        # `request_token` should not have been called
        self.assertEqual(app2.request_token.call_count, 0)

    @patch.object(GeotriggerSession, 'post')
    def test_geotrigger_request(self, mock_request):
        """
        Test creation of Geotrigger API requests.
        """
        # make a call via the `geotrigger_post` method
        data = {'triggerIds': 'trigger_id'}
        url = 'trigger/run'
        self.client.geotrigger_request(url, data=data)

        # ensure that the `post` method is called with the correct parameters
        self.client.post.assert_called_once_with(
            GEOTRIGGER_BASE_URL + url,
            headers=self.geotrigger_headers,
            data=json.dumps(data)
        )

    @patch.object(GeotriggerSession, 'ago_request')
    def test_refresh(self, mock_ago_request):
        """
        Test refresh of expired access tokens.
        """
        new_token = 'new_token'
        new_expires = 'new_expires_in'
        mock_ago_request.return_value = {
            'access_token': new_token,
            'expires_in': new_expires
        }

        old_token = self.client.access_token
        old_expires = self.client.expires_in

        # sanity
        self.assertEqual(self.access_token, old_token)
        self.assertEqual(self.expires_in, old_expires)

        # call refresh
        self.client.refresh()

        # check refresh request
        self.client.ago_request.assert_called_once_with(
            AGO_TOKEN_ROUTE,
            {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials',
                'f': 'json'
            }
        )

        # check refreshed token
        self.assertEqual(self.client.access_token, new_token)
        self.assertEqual(self.client.expires_in, new_expires)


if __name__ == '__main__':
    unittest.main()
# Copyright 2017 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import httplib
import socket
import unittest

import mock

from google.appengine.ext import testbed

from dashboard.services import request


class _RequestTest(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_memcache_stub()

    http = mock.MagicMock()
    self._request = http.request

    patcher = mock.patch('dashboard.common.utils.ServiceAccountHttp')
    service_account_http = patcher.start()
    service_account_http.return_value = http
    self.addCleanup(patcher.stop)


class SuccessTest(_RequestTest):

  def testRequest(self):
    self._request.return_value = ({'status': '200'}, 'response')
    response = request.Request('https://example.com')
    self._request.assert_called_once_with('https://example.com', method='GET')
    self.assertEqual(response, 'response')

  def testRequestJson(self):
    self._request.return_value = ({'status': '200'}, '"response"')
    response = request.RequestJson('https://example.com')
    self._request.assert_called_once_with('https://example.com', method='GET')
    self.assertEqual(response, 'response')

  def testRequestJsonWithPrefix(self):
    self._request.return_value = ({'status': '200'}, ')]}\'\n"response"')
    response = request.RequestJson('https://example.com')
    self._request.assert_called_once_with('https://example.com', method='GET')
    self.assertEqual(response, 'response')

  def testRequestWithBodyAndParameters(self):
    self._request.return_value = ({'status': '200'}, 'response')
    response = request.Request('https://example.com', 'POST', body='a string',
                               url_param_1='value_1', url_param_2='value_2')
    self._request.assert_called_once_with(
        'https://example.com?url_param_1=value_1&url_param_2=value_2',
        method='POST', body='"a string"',
        headers={'Content-Type': 'application/json'})
    self.assertEqual(response, 'response')


class FailureAndRetryTest(_RequestTest):

  def _TestRetry(self):
    response = request.Request('https://example.com')

    self._request.assert_called_with('https://example.com', method='GET')
    self.assertEqual(self._request.call_count, 2)
    self.assertEqual(response, 'response')

  def testHttpErrorCode(self):
    self._request.return_value = ({'status': '500'}, '')
    with self.assertRaises(httplib.HTTPException):
      request.Request('https://example.com')
    self._request.assert_called_with('https://example.com', method='GET')
    self.assertEqual(self._request.call_count, 2)

  def testHttpException(self):
    self._request.side_effect = httplib.HTTPException
    with self.assertRaises(httplib.HTTPException):
      request.Request('https://example.com')
    self._request.assert_called_with('https://example.com', method='GET')
    self.assertEqual(self._request.call_count, 2)

  def testSocketError(self):
    self._request.side_effect = socket.error
    with self.assertRaises(socket.error):
      request.Request('https://example.com')
    self._request.assert_called_with('https://example.com', method='GET')
    self.assertEqual(self._request.call_count, 2)

  def testNotFound(self):
    self._request.return_value = ({'status': '404'}, '')
    with self.assertRaises(request.NotFoundError):
      request.Request('https://example.com')
    self._request.assert_called_with('https://example.com', method='GET')
    self.assertEqual(self._request.call_count, 1)

  def testHttpErrorCodeSuccessOnRetry(self):
    failure_return_value = ({'status': '500'}, '')
    success_return_value = ({'status': '200'}, 'response')
    self._request.side_effect = failure_return_value, success_return_value
    self._TestRetry()

  def testHttpExceptionSuccessOnRetry(self):
    return_value = ({'status': '200'}, 'response')
    self._request.side_effect = httplib.HTTPException, return_value
    self._TestRetry()

  def testSocketErrorSuccessOnRetry(self):
    return_value = ({'status': '200'}, 'response')
    self._request.side_effect = socket.error, return_value
    self._TestRetry()


class CacheTest(_RequestTest):

  def testSetAndGet(self):
    self._request.return_value = ({'status': '200'}, 'response')

    response = request.Request('https://example.com', use_cache=True)
    self.assertEqual(response, 'response')
    self.assertEqual(self._request.call_count, 1)

    response = request.Request('https://example.com', use_cache=True)
    self.assertEqual(response, 'response')
    self.assertEqual(self._request.call_count, 1)

  def testRequestBody(self):
    self._request.return_value = ({'status': '200'}, 'response')
    with self.assertRaises(NotImplementedError):
      request.Request('https://example.com', body='body', use_cache=True)


class AuthTest(_RequestTest):

  def testNoAuth(self):
    http = mock.MagicMock()

    patcher = mock.patch('httplib2.Http')
    httplib2_http = patcher.start()
    httplib2_http.return_value = http
    self.addCleanup(patcher.stop)

    http.request.return_value = ({'status': '200'}, 'response')
    response = request.Request('https://example.com', use_auth=False)
    http.request.assert_called_once_with('https://example.com', method='GET')
    self.assertEqual(self._request.call_count, 0)
    self.assertEqual(response, 'response')

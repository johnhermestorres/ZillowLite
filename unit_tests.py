import os
import application
import unittest
import tempfile
import json

class ZillowLiteTestCase(unittest.TestCase):

    def setUp(self):
        application.application.testing = True
        self.app = application.application.test_client()

    def tearDown(self):
        return

    def test_search_page_loads(self):
        page = self.app.get('/')
        self.assertNotEqual("", page.data, msg="Testing page did not load content")

    def test_search_page_status_code(self):
        response = self.app.get('/')
        status_code = response.status_code
        self.assertEqual(200, status_code, msg="Status code not 200")

    def test_post_with_no_data(self):
        testData = {}
        response = self.app.post('/', data = testData)
        self.assertIn("400 Bad Request", response.data)

    def test_post_invalid_data(self):
        testData = {'foobar': 'barfoo'}
        response = self.app.post('/', data=testData)
        self.assertIn("400 Bad Request", response.data)

    def test_post_valid_data(self):
        testData = {'inputAddress': '2114 Bigelow Ave', 'inputCityState': 'Seattle, WA', 'inputZip': ''}
        response = self.app.post('/', data=testData)
        jsonData = json.loads(response.data)
        self.assertNotIn("400 Bad Request", response.data)
        self.assertIn('links', jsonData.keys())
        self.assertIn('address', jsonData.keys())
        self.assertIn('zestimate', jsonData.keys())
        self.assertIn('localRealEstate', jsonData.keys())

    def test_post_valid_addrres_invalid_citystate(self):
        testData = {'inputAddress': '2114 Bigelow Ave', 'inputCityState': 'fooBar, FB', 'inputZip': ''}
        response = self.app.post('/', data=testData)
        self.assertIn("Error code: 508", response.data)

    def test_post_valid_address_invalid_zip(self):
        testData = {'inputAddress': '2114 Bigelow Ave', 'inputCityState': '', 'inputZip': 'foobar'}
        response = self.app.post('/', data=testData)
        self.assertIn("Error code: 508", response.data)

    def test_post_valid_address_no_citystate_and_zip(self):
        testData = {'inputAddress': '2114 Bigelow Ave', 'inputCityState': '', 'inputZip': ''}
        response = self.app.post('/', data=testData)
        self.assertIn("Error code: 501", response.data)

    def test_post_valid_citystate_no_address_no_zip(self):
        testData = {'inputAddress': '', 'inputCityState': 'Seattle, WA', 'inputZip': ''}
        response = self.app.post('/', data=testData)
        self.assertIn("Error code: 500", response.data)

    def test_invalid_zillow_api_key(self):
        valid_zillow_key = application.ZILLOW_API_KEY
        application.ZILLOW_API_KEY = "INVALID_ZILLOW_KEY"
        testData = {'inputAddress': '2114 Bigelow Ave', 'inputCityState': 'Seattle, WA', 'inputZip': ''}
        response = self.app.post('/', data=testData)
        self.assertIn("Error code: 2", response.data)
        application.ZILLOW_API_KEY = valid_zillow_key

    def test_invalid_zillow_url(self):
        valid_zillow_url = application.ZILLOW_URL
        application.ZILLOW_URL = "http://www.zillow.com/webservice/GetSearchResultsFOOBAR.htm"
        testData = {'inputAddress': '2114 Bigelow Ave', 'inputCityState': 'Seattle, WA', 'inputZip': ''}
        response = self.app.post('/', data=testData)
        self.assertIn("Error code: 4", response.data) 
        application.ZILLOW_URL = valid_zillow_url



if __name__ == '__main__':
    unittest.main()

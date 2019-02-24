from main import Application
from tornado.testing import AsyncHTTPTestCase
import unittest



class BlogTest(AsyncHTTPTestCase):

    def get_app(self):
        return Application

    def setUp(self):
        super(BlogTest, self).setUp()
        self.http_server.start()

    def get_url(self, path):
        return 'http://192.168.22.100:8000%s' % path

    def test_get_blog_list(self):
        headers = {
            'Cookie': 'OUTFOX_SEARCH_USER_ID_NCOO=1549765371.768925; BLOG="2|1:0|10:1550904490|4:BLOG|24:S2c1Q3p1V2s4aXg3cjIzZA==|8e72b5e8a688f8c449bbf41d411d3157f6b5c0b86265ed7ea3e1bb58b0a1ca01"; ___rl__test__cookies=1550904516525'
        }
        response = self.fetch('/', headers=headers)
        self.assertEqual(response.code, 200)

    def test_get_blog_detail(self):
        headers = {
            'Cookie': 'OUTFOX_SEARCH_USER_ID_NCOO=1549765371.768925; BLOG="2|1:0|10:1550904490|4:BLOG|24:S2c1Q3p1V2s4aXg3cjIzZA==|8e72b5e8a688f8c449bbf41d411d3157f6b5c0b86265ed7ea3e1bb58b0a1ca01"; ___rl__test__cookies=1550904516525'
        }
        response = self.fetch('/detail/qg0KIJuETX8Ur9sG', headers=headers)
        self.assertEqual(response.code, 200)

if __name__ == "__main__":
    unittest.main()
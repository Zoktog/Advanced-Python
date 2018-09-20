import log_analyzer
import unittest


class TestBuildReport(unittest.TestCase):

    def parse_url(self):
        res = log_analyzer.parse_line('1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] '
                                      '"GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" '
                                      '"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" '
                                      '"-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390')

        self.assertEqual(res.group('request_url'), '/api/v2/banner/25019354')

        res = log_analyzer.parse_line('1.195.208.16 -  - [29/Jun/2017:03:50:23 +0300] '
                                      '"POST /api/v2/target/12988/list?status=1 HTTP/1.0" 200 2 '
                                      '"https://rb.mail.ru/api/v2/target/12988/list?status=1" '
                                      '"MR HTTP Monitor" "-" "1498697423-1957913694-4708-9752787" "-" 0.003')

        self.assertEqual(res.group('request_url'), '/api/v2/target/12988/list?status=1')

        res = log_analyzer.parse_line('')
        self.assertEqual(res.group('request_url'), None)

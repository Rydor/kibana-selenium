import config
import logging
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

log_format = "%(asctime)s %(name)s [%(levelname)s] %(message)s"
logging.basicConfig(format=log_format, filename='kibana.log',
                    level=logging.ERROR)


class KibanaOne(unittest.TestCase):

    def setUp(self):
        try:
            """
            This is used to test remotely and through Jenkins.
            Ensure when committing code that this value is not commented out.
            """
            self.driver = webdriver.PhantomJS()

            """
            :service_args: configuration management for phantomjs
             This is used for testing headless and locally.
            """
            # service_args = ['--proxy=localhost:9999', '--proxy-type=socks5']
            # self.driver = webdriver.PhantomJS(service_args=service_args)

            """
            The next few lines are needed if you want to execute
            tests in firefox for the visual display of the tests.
            """
            myProxy = "localhost:9999"
            proxy = Proxy({
                'proxyType': ProxyType.MANUAL,
                'socksProxy': myProxy
            })
            # self.driver = webdriver.Firefox(proxy=proxy)

            """
            This will create the session within which all actions take place
            """
            self.driver.set_window_size(1920, 1080)
            conf = config.app['kibana']
            user = conf['username']
            passwd = conf['kibana_password']
            ext_vip = conf['external_lb_vip_address']
            url = "http://{0}:{1}@{2}:8443/".format(user, passwd, ext_vip)
            self.driver.get(url)
            time.sleep(2)
            """
            element is used to ensure the page has fully
            loaded before we start accessing the page elements
            """
            element = WebDriverWait(self.driver, 10).until(
                ec.text_to_be_present_in_element((By.CSS_SELECTOR, ".brand"),
                                                 "Event Dashboard")
                )
            time.sleep(1)
        except Exception, e:
            self.driver.save_screenshot('setup.png')
            logging.error(
                "Setup failed... {}".format(e), exc_info=True)
            raise

    def test_login(self):
        try:
            header = self.driver.find_element_by_css_selector('.brand').text
            self.assertIn("Event Dashboard", header)
        except Exception, e:
            self.driver.save_screenshot('login_ss.png')
            logging.error(
                "Login test failed with... {}".format(e), exc_info=True)
            raise

    def test_graph_exists(self):
        try:
            k_con = self.driver.find_element_by_class_name('kibana-container')
            kib_row = k_con.find_element_by_class_name('kibana-row')
            row = kib_row.find_element_by_class_name('row-control')
            panel = row.find_element_by_class_name('panel-container')
            self.assertIn("OPENSTACK EVENTS", panel.text)
        except Exception, e:
            self.driver.save_screenshot('graph_exists_ss.png')
            logging.error(
                "Graph test failed with... {}".format(e), exc_info=True)
            raise

    def test_log_section_exists(self):
        try:
            logs = self.driver.find_element_by_class_name("table-hover")
            self.assertIn("@timestamp host module logmessage", logs.text)
        except Exception, e:
            self.driver.save_screenshot('log_section_ss.png')
            logging.error(
                "Log Section test failed with... {}".format(e), exc_info=True)
            raise

    def test_log_content_exists(self):
        try:
            self.driver.implicitly_wait(1)
            pointer = self.driver.find_element_by_css_selector('tr.pointer')
            pointer.click()
            self.driver.implicitly_wait(1)
            table = self.driver.find_element_by_css_selector(
                'table.table-details')
            tbody = table.find_element_by_css_selector('tbody')
            log = tbody.find_elements_by_tag_name('tr')
            for i, v in enumerate(log, start=1):
                if "message" in v.text:
                    if "logmessage" in v.text:
                        pass
                    else:
                        child = i
            css = "tr.ng-scope:nth-child({0}) > td:nth-child(3)".format(child)
            mess_content = tbody.find_element_by_css_selector(css).text
            self.assertIsNotNone(mess_content)
        except Exception, e:
            self.driver.save_screenshot('log_content_ss.png')
            logging.error(
                "Log Content test failed with... {}".format(e), exc_info=True)
            raise

    def tearDown(self):
        self.driver.quit()

if __name__ == '__main__':
    unittest.main()

"""
@Project ：12306craweler 
@File    ：CrawlerSpiderV1.py
@IDE     ：PyCharm 
@Author  ：Atomyzd
@Useage    ：12306爬虫
"""
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()

class TrainSpider(object):
    login_url = "https://kyfw.12306.cn/otn/resources/login.html"
    personal_url = "https://kyfw.12306.cn/otn/view/index.html"

    def __init__(self, from_station, to_station, train_date):
        self.from_station = from_station
        self.to_station = to_station
        self.train_date = train_date

    def login(self):
        driver.get(self.login_url)
        scan_btn = driver.find_element_by_xpath("//li[@class='login-hd-account']/a")
        scan_btn.click()
        # 需要判断是否登录成功，此时需要使用显式等待
        WebDriverWait(driver, 1000).until(
            # EC.url_to_be(self.personal_url)
            EC.url_contains(self.personal_url)
        )
        print("登录成功!")

    def run(self):
        # 1. 登录
        self.login()


def main():
    spider  = TrainSpider("北京", "上海", "2022-9-22")
    spider.run()


if __name__ == '__main__':
    main()


"""
@Project ：12306craweler 
@File    ：CrawlerSpiderV1.py
@IDE     ：PyCharm 
@Author  ：Atomyzd
@Useage    ：12306爬虫
"""
import csv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()

class TrainSpider(object):
    login_url = "https://kyfw.12306.cn/otn/resources/login.html"
    personal_url = "https://kyfw.12306.cn/otn/view/index.html"
    left_ticket_url = "https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc"

    def __init__(self, from_station, to_station, train_date):
        self.from_station = from_station
        self.to_station = to_station
        self.train_date = train_date
        self.station_codes = dict()
        # 初始化站点所对应的代号
        self.init_station_code()

    def init_station_code(self):
        with open("stations.csv", "r", encoding='utf-8') as fp:
            reader = csv.DictReader(fp)
            for line in reader:
                name = line['name']
                code = line['code']
                self.station_codes[name] = code
                # print("name:%s, code:%s" % (name, code))

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


    def search_left_ticket(self):
        driver.get(self.left_ticket_url)
        tip_btn = driver.find_element_by_id("qd_closeDefaultWarningWindowDialog_id")
        tip_btn.click()
        # 找到输入框元素,出发站的代号设置
        from_station_input = driver.find_element_by_id("fromStation")
        from_station_code = self.station_codes[self.from_station]
        driver.execute_script("arguments[0].value='%s'" % from_station_code, from_station_input)
        # 终点站的代号设置
        to_station_input = driver.find_element_by_id("toStation")
        to_station_code = self.station_codes[self.to_station]
        driver.execute_script("arguments[0].value='%s'" % to_station_code, to_station_input)
        # 日期设置
        train_date_input = driver.find_element_by_id("train_date")
        # train_date_input.clear()
        # train_date_input.send_keys(self.train_date)
        driver.execute_script("arguments[0].value='%s'" % self.train_date, train_date_input)

        # 执行查询操作
        search_btn = driver.find_element_by_id("query_ticket")
        search_btn.click()

    def run(self):
        # 1. 登录
        self.login()
        # 2. 车次余票查询
        self.search_left_ticket()


def main():
    spider = TrainSpider("淮安", "南京", "2022-09-23")
    spider.run()


if __name__ == '__main__':
    main()


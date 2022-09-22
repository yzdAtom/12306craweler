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
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

driver = webdriver.Chrome()
# 9：商务座，M：一等座，O：二等座，3：硬卧，4：软卧，1：硬座

class TrainSpider(object):
    login_url = "https://kyfw.12306.cn/otn/resources/login.html"
    personal_url = "https://kyfw.12306.cn/otn/view/index.html"
    left_ticket_url = "https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc"
    confirm_passenger_url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"

    def __init__(self, from_station, to_station, train_date, trains, passengers):
        """
        :param from_station: 出发站
        :param to_station: 到达站
        :param train_date: 日期
        :param trains: 车次
        :param passengers: 购票人
        """
        self.from_station = from_station
        self.to_station = to_station
        self.train_date = train_date
        self.trains = trains
        self.passengers = passengers
        self.station_codes = dict()
        self.selected_number = None
        self.selected_seat = None
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

        # 解析车次信息
        # 等待列车信息被加载
        WebDriverWait(driver, 1000).until(
            EC.presence_of_element_located((By.XPATH, "//tbody[@id='queryLeftTable']/tr"))
        )
        train_trs = driver.find_elements_by_xpath("//tbody[@id='queryLeftTable']/tr[not(@datatran)]")
        is_searched = False
        for train_tr in train_trs:
            # print(train_tr.text)
            infos = train_tr.text.replace("\n", " ").split(" ")
            number = infos[0]
            if number in self.trains:
                seat_types = self.trains[number]
                for seat_type in seat_types:
                    if seat_type == "O":
                        # 二等座
                        count = infos[9]
                        if count.isdigit() or count == "有":
                            is_searched = True
                            break
                    elif seat_type == "M":
                        # 一等座
                        count = infos[8]
                        if count.isdigit() or count == "有":
                            is_searched = True
                            break
                if is_searched is True:
                    self.selected_number = number
                    order_btn = train_tr.find_element_by_xpath("//a[@class='btn72']")
                    order_btn.click()
                    break

    def confirm_passengers(self):
        WebDriverWait(driver, 1000).until(
            EC.url_contains(self.confirm_passenger_url)
        )

        WebDriverWait(driver, 1000).until(
            EC.presence_of_element_located((By.XPATH, "//ul[@id='normal_passenger_id']/li/label"))
        )

        # 确认需要购买车票的乘客
        passenger_labels = driver.find_elements_by_xpath("//ul[@id='normal_passenger_id']/li/label")
        for passenger_label in passenger_labels:
            name = passenger_label.text
            if name in self.passengers:
                passenger_label.click()
        # 确认需要购买的席位信息
        seat_select = Select(driver.find_element_by_id("seatType_1"))
        seat_types = self.trains[self.selected_number]
        for seat_type in seat_types:
            try:
                self.selected_seat = seat_type
                seat_select.select_by_value(seat_type)
            except NoSuchElementException:
                continue
            else:
                break
        # 等待提交订单按钮可以被点击
        WebDriverWait(driver, 1000).until(
            EC.element_to_be_clickable((By.ID, "submitOrder_id"))
        )
        submit_btn = driver.find_element_by_id("submitOrder_id")
        submit_btn.click()

        WebDriverWait(driver, 1000).until(
            EC.presence_of_element_located((By.CLASS_NAME,"dhtmlx_wins_body_inner"))
        )

        WebDriverWait(driver, 1000).until(
            EC.element_to_be_clickable((By.ID, "qr_submit_id"))
        )

        order_btn = driver.find_element_by_id("qr_submit_id")
        while order_btn:
            try:
                order_btn.click()
                order_btn = driver.find_element_by_id("qr_submit_id")
            except:
                break
        print("恭喜！%s车次%s抢票成功" % (self.selected_number, self.selected_seat))



    def run(self):
        # 1. 登录
        self.login()
        # 2. 车次余票查询
        self.search_left_ticket()
        # 3. 确认乘客和车次信息
        self.confirm_passengers()



def main():
    spider = TrainSpider("淮安", "南京", "2022-09-23", {"D5515":["O", "M"]}, ["XXXXX"])
    spider.run()


if __name__ == '__main__':
    main()


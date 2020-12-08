# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 00:17:04 2020

@author: Wong Wei Jie 
"""

from selenium import webdriver
from datetime import timedelta, date, datetime
from selenium.webdriver.chrome.options import Options
import time 

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)+1):
        yield end_date - timedelta(n)

chrome_options = Options()
prefs = {'profile.default_content_setting_values.automatic_downloads': 1}
chrome_options.add_experimental_option("prefs", prefs)
browser = webdriver.Chrome('C:/Users/User/Documents/QAM/Sunmer_Project/chromedriver_win32/chromedriver', 
                           chrome_options=chrome_options)
browser.get("https://www.dukascopy.com/swiss/english/marketwatch/historical/")
browser.maximize_window()
loginState = False

frame = browser.find_element_by_xpath('/html/body/div/main/div[2]/div/div/div/p[3]/iframe')
browser.switch_to.frame(frame)
time.sleep(2)


#pair - 'EUR/USD'
#start_date - datetime format year, month and day only. Start date of the historical continuous tick data extraction.
#end_date - End date of the historical continuous tick data extraction in datetime format.
def downloadDailyTickDataForexPair(pair, start_date, end_date):
    global loginState
    
    pair_instrument = browser.find_element_by_xpath(
            "//li[@class='d-qh-eh-Ag'][@data-instrument='"+pair+"']")
    print(pair_instrument.get_attribute('innerHTML'))
    
    datepicker = browser.find_element_by_css_selector("div.a-popupdatepicker")
    
    previous_year = datepicker.find_element_by_xpath(
            ".//button[@class='d-Ch-fi-btn d-Ch-fi-previousYear']")
    
    pair_instrument.find_element_by_css_selector('span').click()
    
    for single_date in daterange(start_date, end_date):
        print(single_date.strftime("%Y-%m-%d"))
        datepickerButton = browser.find_element_by_xpath(
                "//div[@class='a-b-c a-ab-v d-wh-vg-Ch-Dh']")
        datepickerButton.click()
        
        currDateText = datepickerButton.find_element_by_xpath('div/div/span').text
        print("currDateText", currDateText)
        
        month_list = ['January', 'February', 'March',
                      'April', 'May', 'June',
                      'July', 'August', 'September',
                      'October', 'November', 'December']
        
        iterstateYear, iterstateMonth, iterstateDay = list(map(lambda string : int(string), currDateText.split("-")))
        
        while (single_date.year < iterstateYear):
                print("single_date", single_date)
                print("iterstateYear", iterstateYear)
                previous_year.click()
                iterstateYear = int(datepicker.find_element_by_xpath(".//button[@class='d-Ch-fi-btn d-Ch-fi-ni']").text)
        
        
        while single_date.month != iterstateMonth:
                print("month", single_date.month)
                print("iterstateMonth", iterstateMonth)
                currentMonth = datepicker.find_element_by_xpath(".//button[@class='d-Ch-fi-btn d-Ch-fi-mi']")
                currentMonth.click()
                monthDropDown =  datepicker.find_elements_by_xpath(".//table/thead/tr/td/div[@class='d-Ch-fi-u']/ul/li")
                browser.execute_script("arguments[0].click();", monthDropDown[single_date.month-1])
                stringMth = datepicker.find_element_by_xpath(".//button[@class='d-Ch-fi-btn d-Ch-fi-mi']").text
                iterstateMonth = month_list.index(stringMth)+1
    
        
        print("currmtnh", datepicker.find_element_by_xpath(".//button[@class='d-Ch-fi-btn d-Ch-fi-mi']").text)
        rows = datepicker.find_elements_by_xpath(".//th[@class='d-Ch-fi-gi'][@role='rowheader']")
        
        for row in rows: 
            if int(row.text) == single_date.isocalendar()[1]:
                print("row ", row.text)
                for dayGrid in row.find_elements_by_xpath("..//td[@role='gridcell']"):
                    if int(dayGrid.text)==single_date.day: 
                        print("selected day ", dayGrid.text)
                        dayGrid.click()
                        break
                break
            
        #change to UTC
        dayStartTime = browser.find_element_by_xpath("//div[@class='d-wh-vg-xh d-wh-vg-Fh-Gh-Hh-p']")
        
        # if time is not in UTC
        if dayStartTime.text != 'Day start time:\nUTC ':
            
            dayStartTime.click()
            UTC = browser.find_element_by_xpath("//div[@class='a-u a-u-eb'][@role='listbox']")\
                    .find_element_by_xpath(".//div[@class='a-L a-T'][@id=':d']")          
            UTC.click()
        
        #change to GMT
        GMT = browser.find_element_by_xpath("""//div[contains(@class, 'a-b-c a-ab-v') 
                                                and contains(@class, 'a-ab-v-H-J') and 
                                                .//text()='GMT']""")
        GMT.click()
        
        #change volume to Units
        volume = browser.find_element_by_xpath("//div[@class='d-wh-vg-xh d-wh-vg-Ih-Jh-p']")
        
        # if volume not in Units
        if volume.text != 'Units ':
            
            volume.click()
            volumeDropDown = browser.find_element_by_xpath("//div[@class='a-u a-u-eb'][@role='listbox']")
            selectUnits = volumeDropDown.find_element_by_xpath("//div[@id=':e']")
            selectUnits.click()
        
        #Download
        download = browser.find_element_by_xpath("//div[@class='a-b-c d-oh-i-ph-v d-wh-vg-Tg'][@role='button']")
        download.click()
        
        if not loginState:
            currtime = datetime.now()
            stoptime = currtime + timedelta(seconds = 2)
            while(datetime.now() < stoptime):
                try:
                    loginPage = browser.find_element_by_xpath("//div[@class='d-oh-i-ph-Rh d-oh-i-ph-Rh-Uh d-oh-i-ph-Rh-Sh d-oh-i-ph-Rh-Uh-Vh']")
                    username = loginPage.find_element_by_xpath(".//input[@class='d-e-Xg'][@type='text']")
                    pwd = loginPage.find_element_by_xpath(".//input[@class='d-e-Xg'][@type='password']")
                    username.send_keys('wowchickawowow@gmail.com')
                    pwd.send_keys('S1728788e')
                    submitLogin = loginPage.find_element_by_xpath(".//div[@class='a-b-c d-e-v'][@role='button']")
                    submitLogin.click()
                    loginState = True
                    break
                except:
                    continue
        
        currtime = datetime.now()
        stoptime = currtime + timedelta(seconds = 30)
        while(datetime.now() < stoptime):
            try:
                save = browser.find_element_by_xpath("//div[@class='a-b-c a-ab-v d-Wh-Xh-Zh'][@role='button']")
                reset = browser.find_element_by_xpath("//div[@class='a-b-c a-ab-v d-Wh-Xh-Ug'][@role='button']")
                save.click()
                reset.click()
                break
            except:
                continue

        

pair = 'EUR/USD'
start_date = datetime(year=2017, month=1, day=1)
end_date = datetime(year=2017, month=1, day=6)
downloadDailyTickDataForexPair(pair, start_date, end_date)


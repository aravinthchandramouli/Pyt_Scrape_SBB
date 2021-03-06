from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
import json
import pandas as pd
SBB_URL = 'https://www.sbb.ch/en/buying/pages/fahrplan/fahrplan.xhtml'

class SBB():
    def __init__(self):
        opts = Options()
        # opts.set_headless() # comment this if you want to see the browser.
        self.browser = Firefox(options = opts)
        self.browser.fullscreen_window()
        self.browser.get(SBB_URL)
        self.searchResults = []

    def search(self, fromCity, toCity):
        from_station = self.browser.find_element_by_id('shopForm_von_valueComp')
        from_station.send_keys(fromCity)
        to_station = self.browser.find_element_by_id('shopForm_nach_valueComp')
        to_station.send_keys(toCity)
        self.browser.find_element_by_class_name('verbindungSuchen').click()
    
    def goToSearchPage(self):
        self.browser.get(SBB_URL)

    def parseResults(self):
        results = self.browser.find_element_by_class_name('mod_accordion_set')
        allRoutes = results.find_elements_by_class_name('sbb_mod_ext')
        for route in allRoutes:
            try:
                connectionDetails = route.find_element_by_class_name('mod_timetable_connection_details')
                route.click()
                routemode = connectionDetails.find_element_by_xpath('./div/div/span[2]').text
                expanded_element = route.find_element_by_class_name('mod_accordion_item_content')
                directionName = connectionDetails.find_element_by_class_name('mod_timetable_direction').text
                startTime = connectionDetails.find_element_by_class_name('mod_timetable_starttime').find_element_by_xpath('.//span[@data-timetable= "parse-time"]').text
                endTime = connectionDetails.find_element_by_class_name('mod_timetable_endtime').find_element_by_xpath('.//span[@data-timetable= "parse-time"]').text
                trainName = expanded_element.find_element_by_xpath('//*[@id="stage_0_0"]/div[1]/div[1]/span[4]').get_attribute('innerHTML')
                info = {
                    "mode": routemode,
                    "directionName":directionName,
                    "startTime":startTime,
                    "endTime":endTime,
                    "duration":route.find_element_by_class_name('mod_timetable_duration').find_element_by_xpath('.//span[@data-timetable="parse-duration"]').text,
                    "noOfChanges":route.find_element_by_class_name('mod_timetable_change').find_element_by_xpath('./p[1]').text,
                    "occupancyListText":route.find_element_by_class_name('mod_timetable_occupancy').text,
                    "platform":route.find_element_by_class_name('mod_timetable_platform').text,
                    "timetableMessage":route.find_element_by_class_name('mod_timetable_message').text,
                    "price": route.find_element_by_class_name('timetableBuyButtonLabel').text.replace("from",""),
                    "trainName":trainName
                }
                self.searchResults.append(info)
            except Exception as error:
                print(error)
                continue


if __name__ == '__main__':
    print("starting scraping")
    #You can do multiple searches with this framework. Hopefully, you know the list of the cities you want to search for .
    sbb = SBB()
    fromCity = 'Lucerne'
    toCity = 'Interlaken'
    sbb.search(fromCity, toCity)
    time.sleep(10) # Need to find an alternative solution to sleep. First thing that came to mind, to make sure that the following code runs after the page is loaded with the results.
    sbb.parseResults()
    print(sbb.searchResults)
    sbb.goToSearchPage()
    df = pd.read_json(json.dumps(sbb.searchResults))
    df.to_csv('searchResults'+fromCity+'-'+toCity+'.csv')
    #time.sleep(5)
    sbb.browser.close() # Do this once you're done.
    
    # If you're multithreading , create a function of whatever written in the main. write a method for persisting the scraped results in a DB.
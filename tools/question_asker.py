from selenium import webdriver
from config import URL_ASK, GOOGLE_CHROME_PATH, CHROMEDRIVER_PATH


def ask(question):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.binary_location = GOOGLE_CHROME_PATH

    browser = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
    browser.get(URL_ASK)

    text = browser.find_element_by_id('question_question_text')
    text.send_keys(question)

    for element in browser.find_elements_by_xpath("//*[contains(text(), 'I agree')]"):
        browser.execute_script('arguments[0].click();', element)

    browser.find_element_by_id('questionsNewForm').submit()
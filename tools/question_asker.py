from selenium import webdriver
from config import URL_ASK, GOOGLE_CHROME_PATH, CHROMEDRIVER_PATH

class QuestionAsker:
    @staticmethod
    def ask(question):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.binary_location = GOOGLE_CHROME_PATH

        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
        driver.get(URL_ASK)

        JS_ADD_TEXT_TO_INPUT = """
            var elm = arguments[0], txt = arguments[1];
            elm.value += txt;
            elm.dispatchEvent(new Event('change'));
            """

        text_input = driver.find_element_by_id('question_question_text')
        driver.execute_script(JS_ADD_TEXT_TO_INPUT, text_input, question)

        for element in driver.find_elements_by_xpath("//*[contains(text(), 'I agree')]"):
            driver.execute_script('arguments[0].click();', element)

        driver.find_element_by_id('questionsNewForm').submit()
        driver.close()
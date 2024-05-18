from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Initialize the WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless') # 몇몇 동적요소때문에 headless모드는 사용하지 않음
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open the target webpage
url = "https://docs.minaprotocol.com/about-mina"
driver.get(url)

html_source = driver.page_source
print(html_source)

# Close the WebDriver
driver.quit()

print("Data has been saved successfully!")

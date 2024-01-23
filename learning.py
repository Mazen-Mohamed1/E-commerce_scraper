from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
import time
import re
import csv

user_input = input('Enter the product: ').replace(' ', '+')
Noon_limit = 0

# websites url
sites = ['Noon',
         'Jumia',
         'https://www.amazon.eg/?&tag=egtxabkgode-21&ref=pd_sl_7p2aq4fe2v_e&adgrpid=152488092398&hvpone=&hvptwo=&hvadid=666798652278&hvpos=&hvnetw=g&hvrand=13189778680749034432&hvqmt=e&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=1005390&hvtargid=kwd-10573980&hydadcr=334_2589534&language=en_AE'
         ]

# websites Data
products_details = []


def noon(link):
    try:
        service = Service(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service)

        global Noon_limit

        # getting the main divs
        browser.get(link)
        time.sleep(5)
        products_list = browser.find_elements('class name', 'sc-5c17cc27-0')

        # getting the pages limit
        results = browser.find_element('class name', 'sc-3729600-4')
        Noon_limit = int(results.text[:-12]) / 50

        # getting the html code and the text
        for i in range(3, len(products_list)):
            html_code = products_list[i].get_attribute('outerHTML')
            soup = BeautifulSoup(html_code, 'html.parser')
            try:
                products_name = soup.find('div', {'data-qa': 'product-name'}).text
            except:
                products_name = "No Name found"
            try:
                products_price = soup.find('strong', {'class': 'amount'}).text
            except:
                products_price = 'No price found'
            try:
                products_discount = soup.find('span', {'class': 'discount'}).text
            except:
                products_discount = 'No Discount found'
            try:
                products_rate = soup.find('div', {'class': 'sc-363ddf4f-2'}).text
            except:
                products_rate = 'No Rate found'
            try:
                products_link = f"https://www.noon.com{soup.find('a').get('href')}"
            except:
                products_link = 'No Link found'

            # # adding the data
            products_details.append({
                'Website': 'NOON',
                'PRODUCT PRICE': f'EGP {products_price}',
                'DISCOUNT': products_discount,
                'PRODUCT RATE': products_rate,
                'BRAND NAME': products_name,
                'PRODUCT LINK': products_link
            })

    except Exception as e:
        print(f'Oops, something went wrong with Noon ==> {e}')

def jumia(link):
    try:
        global jumia_limit

        # getting the elements from the page
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')
        products_list = soup.find_all('article', {'class': 'prd'})
        limit = soup.find('p', {'class': '-gy5'}).text
        jumia_limit = int(limit[:-15]) / 40

        # scraping the data
        for i in range(len(products_list)):
            try:
                products_name = products_list[i].find('h3', {'class': 'name'}).text
            except:
                products_name = 'No Name found'
            try:
                products_price = products_list[i].find('div', {'class': 'prc'}).text
            except:
                products_price = 'No Price found'
            try:
                products_rate = products_list[i].find('div', {'class': 'stars'}).text
            except:
                products_rate = 'No Rate found'
            try:
                products_discount = products_list[i].find('div', {'class': 'bdg'}).text
            except:
                products_discount = 'No Discount found'

            product_link = f"https://www.jumia.com.eg{products_list[i].find('a', {'class': 'core'}).get('href')}"

            products_details.append({
                'Website': 'JUMIA',
                'PRODUCT PRICE': products_price,
                'DISCOUNT': products_discount,
                'PRODUCT RATE': products_rate,
                'BRAND NAME': products_name,
                'PRODUCT LINK': product_link
            })
    except Exception as e:
        print(f'Oops, something went wrong with Noon ==> {e}')


def amazon(link):
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1920,1080')

        # Initialize the Chrome driver with options
        service = Service(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service, options=chrome_options)

        products = []
        # scraping teh data
        browser.get(link)
        time.sleep(5)
        search_bar = browser.find_element('name', 'field-keywords')
        search_btn = browser.find_element('id', 'nav-search-submit-button')
        search_bar.send_keys(user_input)
        time.sleep(5)
        search_btn.click()
        time.sleep(5)
        products_list = browser.find_elements('class name', 'sg-col-4-of-24')

        # getting the text
        for i in range(len(products_list) - 1):
            list_html = products_list[i].get_attribute('outerHTML')
            soup = BeautifulSoup(list_html, 'html.parser')
            try:
                products_names = soup.find('span', {'class': 'a-size-base-plus'}).text
            except:
                products_names = 'No Name found'
            try:
                products_rates = soup.find('span', {'class': 'a-icon-alt'}).text
            except:
                products_rates = 'No Rate found'
            try:
                products_prices = soup.find('span', {'class': 'a-price-whole'}).text
            except:
                products_prices = 'No price found'
            try:
                discount_price = soup.find('span', {'class': 'a-text-price'}).text
            except:
                discount_price = 'No Discount found'
            try:
                products_links = f"https://www.amazon.eg{soup.find('a', {'class': 'a-text-normal'}).get('href')}"
            except:
                products_links = 'No Link found'

            # calculating the off percentage
            if products_prices != 'No price found' and products_prices != 'No Discount found':
                pattern = r'EGP[^\d]*([\d,]+)'

                match = re.search(pattern, discount_price)

                if match:
                    extracted_number = match.group(1)
                    original_price = float(extracted_number.replace(',', ''))
                    price = float(products_prices.replace(',', ''))

                    discount_price = f'{int(((original_price - price) / original_price) * 100)}% Off'

            # adding the data
            products_details.append({
                'Website': 'AMAZON',
                'PRODUCT PRICE': f'EGP {products_prices}',
                'DISCOUNT': discount_price,
                'PRODUCT RATE': products_rates,
                'BRAND NAME': products_names,
                'PRODUCT LINK': products_links
            })
        else:
            print('Amazon Done')
    except Exception as e:
        print(f'Oops, something went wrong with Noon ==> {e}')

def file_printing():
    # creating the csv file
    path = 'D:/projects/products_details.csv'
    keys = products_details[0].keys()
    with open(path, 'w', newline='', encoding='UTF-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(products_details)

# handling the websites
def websites(link):
    for num, link in enumerate(link, 1):
        if num == 3:
            amazon(link)
        elif num == 2:
            for i in range(1, 3):
                url = f'https://www.noon.com/egypt-en/search/?limit=50&originalQuery=%D8%B3%D8%A7%D8%B9%D8%A9&page={i}&q={user_input}&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc&gclid=Cj0KCQiAhomtBhDgARIsABcaYylLRnSwoSrKZbbdAAkG5BRn1KaidgQ2f6hww7II-QZy8OIkzKj5l4AaAnbbEALw_wcB&utm_campaign=C1000151355N_eg_en_web_searchxxexactandphrasexxbrandpurexx08082022_noon_web_c1000088l_acquisition_sembranded_&utm_medium=cpc&utm_source=C1000088L'
                noon(url)
                if i >= int(Noon_limit):
                    break
            else:
                print('Noon Done')
        else:
            for i in range(1, 2):
                url = f'https://www.jumia.com.eg/catalog/?q{user_input}&page={i}#catalog-listing'
                jumia(url)
                if i >= int(jumia_limit):
                    break
            else:
                print('Jumia Done')
    else:
        file_printing()
        print('file printed successfully')


websites(sites)

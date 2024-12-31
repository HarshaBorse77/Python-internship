from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import csv
import json

# Setup the Selenium WebDriver
service = Service(r'C:\Users\mohit\Downloads\hii\chromedriver-win64\chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=service, options=options)

# Function to authenticate to Amazon
def authenticate_amazon(email, password):
    driver.get("https://www.amazon.in")
    
    try:
        sign_in_btn = driver.find_element(By.ID, 'nav-link-accountList')
        sign_in_btn.click()

        email_field = driver.find_element(By.ID, 'ap_email')
        email_field.send_keys(email)
        driver.find_element(By.ID, 'continue').click()

        password_field = driver.find_element(By.ID, 'ap_password')
        password_field.send_keys(password)
        driver.find_element(By.ID, 'signInSubmit').click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'nav-link-accountList')))
        print("Logged in successfully!")
    except Exception as e:
        print(f"Error during authentication: {e}")

# Function to scrape product details
def scrape_category(category_url, category_name, max_products=1500):
    driver.get(category_url)
    time.sleep(3)

    products = []
    product_count = 0
    
    while product_count < max_products:
        try:
            # Wait for the product elements to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'zg-item-immersion'))
            )

            product_elements = driver.find_elements(By.CLASS_NAME, 'zg-item-immersion')

            for product in product_elements:
                if product_count >= max_products:
                    break

                try:
                    name = product.find_element(By.CLASS_NAME, 'p13n-sc-truncate').text
                    price = product.find_element(By.CLASS_NAME, 'p13n-sc-price').text
                    discount = "50% or above"  # Placeholder since discount info is often missing
                    rating = product.find_element(By.CLASS_NAME, 'a-icon-alt').text
                    description = product.find_element(By.CLASS_NAME, 'p13n-product-description').text
                    ship_from = "Amazon or other seller"  # Placeholder for Ship From
                    sold_by = "Amazon or partner"  # Placeholder for Sold By
                    num_bought = "N/A"  # Often missing; placeholder

                    # Add extracted product details to the list
                    products.append({
                        'Product Name': name,
                        'Price': price,
                        'Discount': discount,
                        'Rating': rating,
                        'Product Description': description,
                        'Ship From': ship_from,
                        'Sold By': sold_by,
                        'Number Bought': num_bought,
                        'Category Name': category_name,
                        'Images': "Image URLs Placeholder"  # Replace with actual image scraping logic
                    })

                    product_count += 1
                except NoSuchElementException:
                    continue

            # Navigate to the next page if exists
            try:
                next_page = driver.find_element(By.XPATH, '//li[@class="a-last"]/a')
                next_page.click()
                time.sleep(3)
            except NoSuchElementException:
                print("No next page available.")
                break

        except TimeoutException:
            print("Page loading timeout.")
            break

    return products

# Export data to CSV
def export_to_csv(products, filename='amazon_products.csv'):
    if products:
        keys = products[0].keys()
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(products)

# Export data to JSON
def export_to_json(products, filename='amazon_products.json'):
    if products:
        with open(filename, mode='w', encoding='utf-8') as file:
            json.dump(products, file, indent=4, ensure_ascii=False)

# Main script
if _name_ == "_main_":
    try:
        # Authenticate to Amazon
        email = "borseh31@gmail.com"  # Replace with your email
        password = "N3nv1Y-$6M9n0um"  # Replace with your password
        authenticate_amazon(email, password)

        # List of categories to scrape (replace with actual URLs)
        categories = [
            {"url": "https://www.amazon.in/gp/bestsellers/electronics", "name": "Electronics"},
            # Add 9 more category URLs and names
        ]

        all_products = []

        # Scrape each category
        for category in categories:
            category_products = scrape_category(category["url"], category["name"])
            all_products.extend(category_products)

        # Export data
        export_to_csv(all_products, filename='amazon_best_sellers.csv')
        

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
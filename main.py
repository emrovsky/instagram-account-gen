import logging
import random
import sys
import threading
import time
from datetime import datetime

import loguru
import tls_client
import faker

from modules import mailtm

logging.disable(sys.maxsize)
class InstaGen:
    def __init__(self):
        self.session = tls_client.Session(client_identifier="chrome_120")
        self.session.headers = {
            'authority': 'www.instagram.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://www.instagram.com/accounts/emailsignup/',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Brave";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"10.0.0"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        self.name_surname = faker.Faker().name()
        self.nickname = self.name_surname.replace(" ","").lower() + str(random.randint(100000,999999))[:30]

        self.mailtmapi = mailtm.MailTmApi()
        mail_details = self.mailtmapi.get_random_mail(self.mailtmapi.get_random_avaible_domain())
        self.email = mail_details["email"]
        self.email_password = mail_details["password"]
        self.mail_token = mail_details["token"]


        self.bday =  str(random.randint(1, 25))
        self.bmonth =  str(random.randint(1, 12)),
        self.byear =  str(random.randint(1980, 2000))

        self.proxy = random.choice(open("proxy.txt","r").readlines()).strip()
        self.session.proxies = {'http': 'http://' + self.proxy.strip(), 'https': 'http://' + self.proxy.strip()}


    def get_signup_page(self):
        response = self.session.get('https://www.instagram.com/accounts/emailsignup/')
        try:
            self.machine_id = response.text.split('"machine_id":"')[1].split('"')[0]
            self.session.headers['x-asbd-id'] = '129477'
            self.session.headers['x-csrftoken'] = response.cookies["csrftoken"]
            self.session.headers['x-ig-app-id'] = '936619743392459'
            self.session.headers['x-ig-www-claim'] = '0'
        except:
            loguru.logger.error(f"error occured while getting a key from page")
            return False

        response = self.session.get('https://www.instagram.com/api/v1/web/login_page/')
    def send_email_code(self):
        data = {
            'enc_password':  f'#PWD_INSTAGRAM_BROWSER:0:{int(datetime.now().timestamp())}:{self.email_password}',
            'email': self.email,
            'first_name': self.name_surname,
            'username': self.nickname,
            'opt_into_one_tap': 'false',
        }

        response = self.session.post(
            'https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/',
            data=data,
        )
        data = {
            'day': self.bday,
            'month': self.bmonth,
            'year': self.byear,
        }

        response = self.session.post(
            'https://www.instagram.com/api/v1/web/consent/check_age_eligibility/',
            data=data,
        )

        data = {
            'device_id': self.machine_id,
            'email': self.email,
        }

        response = self.session.post(
            'https://www.instagram.com/api/v1/accounts/send_verify_email/',
            data=data,
        )
        loguru.logger.info(f"[{self.email}] mail code sent")
    def finish_register(self):
        while True:
            time.sleep(1)
            mails = self.mailtmapi.get_emails(self.mail_token)
            if mails != []:
                mail_code = mails[0]['subject'].split(" ")[0]
                break



        loguru.logger.info(f"[{self.email}] - {mail_code}")

        data = {
            'code': mail_code,
            'device_id': self.machine_id,
            'email': self.email,
        }

        response = self.session.post(
            'https://www.instagram.com/api/v1/accounts/check_confirmation_code/',
            data=data,
        )
        signup_code = response.json()["signup_code"]

        data = {
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int(datetime.now().timestamp())}:{self.email_password}',
            'day': self.bday,
            'email': self.email,
            'first_name': self.name_surname,
            'month': self.bmonth,
            'username': self.nickname,
            'year': self.byear,
            'client_id': self.machine_id,
            'seamless_login_enabled': '1',
            'tos_version': 'row',
            'force_sign_up_code': signup_code,
        }

        response = self.session.post(
            'https://www.instagram.com/api/v1/web/accounts/web_create_ajax/',
            data=data,
        )

        if response.json().get("account_created"):
            loguru.logger.success(f"[{self.nickname}] account created")

            open("created.txt","a").write(f"{self.nickname}:{self.email}:{self.email_password}\n")

        else:
            loguru.logger.error(f"error occurred while account creation : {response.text}")
def start():
    while True:
        try:
            gen = InstaGen()
            x = gen.get_signup_page()
            if x != False:
                gen.send_email_code()
                gen.finish_register()
        except Exception as e:
            loguru.logger.error(e)


thread_count = input("thread count > ")
for a in range(int(thread_count)):
    t = threading.Thread(target=start).start()
    time.sleep(0.1)
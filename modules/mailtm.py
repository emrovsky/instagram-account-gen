import json
import random

import random_strings
import requests

class MailTmApi:
    def __init__(self):
        self.session = requests.session()
        self.session.headers = {
            'authority': 'api.mail.gw',
            'accept': '*/*',
            'accept-language': 'tr-TR,tr;q=0.9',
            'cache-control': 'no-cache',
            'origin': 'https://mail.tm',
            'pragma': 'no-cache',
            'referer': 'https://mail.tm/',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Brave";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }
        self.proxy = random.choice(open("proxy.txt", "r").readlines()).strip()
        self.session.proxies = {'http': 'http://' + self.proxy.strip(), 'https': 'http://' + self.proxy.strip()}
    def get_random_avaible_domain(self):
        response = self.session.get('https://api.mail.gw/domains')
        random_mail_domain = random.choice(response.json()["hydra:member"])["domain"]
        return random_mail_domain

    def get_random_mail(self,domain):
        nickname = random_strings.random_hex(10)
        password = random_strings.random_hex(8)

        json_data = {
            'address': f'{nickname}@{domain}',
            'password': password,
        }

        response = self.session.post('https://api.mail.gw/accounts', json=json_data)

        dondurulen_json = response.json()
        dondurulen_json.update({'password': password})

        response = self.session.post('https://api.mail.gw/token', json=json_data)
        return {"email": f'{nickname}@{domain}', "password": password, "token": response.json()["token"]}
    def get_emails(self,mail_token):
        self.session.headers['authorization'] = f'Bearer {mail_token}'
        response = self.session.get('https://api.mail.gw/messages')
        return response.json()["hydra:member"]

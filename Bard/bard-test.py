# Working basic code where you can hard code a question and you get an answer

from bardapi import Bard
import os
import requests

token = os.environ.get("BARD_TOKEN")
bard = Bard(token=token)
res = bard.get_answer("What's the best mayo brand?")['content']
print(res)


# from bardapi import Bard
# import os
# import requests
# os.environ['_BARD_API_KEY'] = ''
# token=''

# session = requests.Session()
# session.headers = {
#             "Host": "bard.google.com",
#             "X-Same-Domain": "1",
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
#             "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
#             "Origin": "https://bard.google.com",
#             "Referer": "https://bard.google.com/",
#         }
# session.cookies.set("__Secure-1PSID", os.getenv("_BARD_API_KEY")) 
# # session.cookies.set("__Secure-1PSID", token) 

# bard = Bard(token=token, session=session, timeout=30)
# bard.get_answer("나와 내 동년배들이 좋아하는 뉴진스에 대해서 알려줘")['content']

# # Continued conversation without set new session
# bard.get_answer("What is my last prompt??")['content']
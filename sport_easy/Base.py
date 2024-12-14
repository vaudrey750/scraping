import json
import pathlib
import requests
from typing import Dict
from datetime import datetime, date
from os import path
import uuid


APP_PATH = pathlib.Path(__file__).parent
COOKIES_FILE_PATH = f"{APP_PATH}/cookies.json"


class SportEasy:
    def __is_cookie_is_validate() -> Dict[str, str]:
        """
            Check if cookie in file is availble
            return cookie when it's available
        """
        cookies = {}
        today = date.today()
        
        with open(COOKIES_FILE_PATH, "r") as json_file:
            cookies = json.load(json_file)
        
        if today < datetime.strptime(cookies.get("expire_date"), "%Y-%m-%d").date():
            return cookies
        return {}
        

    @classmethod    
    def api_login(cls, user_name, password) -> Dict[str, str]:
        """
            login too api and get cookie
            when cookie is not availble create and save new one
        """
        
        available_cookie = cls.__is_cookie_is_validate()
        if available_cookie:
            return available_cookie
        
        result = requests.post(
            "https://api.sporteasy.net/v2.1/account/authenticate/",
            headers={
                "Referer": "https://app.sporteasy.net/",
                "Origin": "https://app.sporteasy.net",
                "Content-Type": "application/json"
            },
            data=json.dumps({
               "username": user_name,
               "password": password
            })
        )
        
        if result and result.json().get("success") == True:
            with open(COOKIES_FILE_PATH, "w") as fp:
                for cookie in result.cookies:
                    available_cookie.update({cookie.name: cookie.value})
                    if cookie.name == "sporteasy":
                        available_cookie.update({"expire_date": datetime.utcfromtimestamp(int(cookie.expires)).strftime("%Y-%m-%d")})
                json.dump(available_cookie, fp)
        return available_cookie
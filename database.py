
import redis
import os
import json
from model import Contact
from dotenv import load_dotenv

# Load the confg files
load_dotenv()

class RedisDictionary:
    def __init__(self):
        self.client = redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
            decode_responses=True,
            username=os.getenv("REDIS_USERNAME"),
            password=os.getenv("REDIS_PASSWORD"),
        )
        self.client.flushall()
        print("Redis Data Structure Ready")
        self.noneChar = "N/A"
    
    def __getitem__(self, key):
        response = self.client.hgetall(name=key)
        if response:
            for key, value in response.items():
                if value == self.noneChar:
                    response[key] = None

            contact = Contact(**response)
            return contact
        
        return {}
    
    def __setitem__(self, name, value: dict | Contact):
        """ Here name-> int & value -> dictionary (Contact)"""
        if isinstance(value, Contact):
            value = value.dict()
        for key, _value in value.items():
            if _value is None:
                value[key] = "N/A"
            
        response = self.client.hset(name=name, mapping=value)
        
    def get(self, key):
        return self.__getitem__(key)

    def __repr__(self):
        ans = {}
        keys = self.client.keys("*")
        for key in keys:
            value = self.client.hgetall(key)
            ans[key] = value
        # print(ans)
        return json.dumps(ans, indent=4)
    

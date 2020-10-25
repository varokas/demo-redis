import time
from locust import HttpUser, task, between

class Locust(HttpUser):
    wait_time = between(1, 2)
    
    @task
    def index_page(self):
        self.client.get("/")
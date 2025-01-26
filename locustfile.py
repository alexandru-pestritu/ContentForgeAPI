from locust import HttpUser, TaskSet, task, between
import random

class AuthenticatedBlogTasks(TaskSet):
    def on_start(self):
        """
        Called once when a Locust "user" is spawned.
        We log in by sending form data to /api/v1/login.
        """
        login_payload = {
            "username": "admin@example.com",
            "password": "admin" 
        }

        with self.client.post("/api/v1/login", data=login_payload, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
            else:
                response.failure(f"Login failed: {response.status_code} {response.text}")
                self.token = None

        self.created_blog_id = None

    @task
    def create_blog(self):
        """
        Create a new blog with an authenticated request.
        We'll store the blog ID for future update/delete tasks.
        """
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {
            "name": f"Perf Test Blog {random.randint(1000,9999)}",
            "base_url": "https://test.example.com",
            "username": "locustuser",
            "api_key": "someapikey"
        }

        with self.client.post("/api/v1/blogs/", json=payload, headers=headers, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Create blog failed: {response.status_code} {response.text}")
            else:
                data = response.json()
                self.created_blog_id = data["id"]

    @task
    def list_blogs(self):
        """
        List blogs with an authenticated GET request.
        """
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        with self.client.get("/api/v1/blogs/?skip=0&limit=10", headers=headers, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"List blogs failed: {response.status_code} {response.text}")

    @task
    def update_blog(self):
        """
        Update the blog we created, if any.
        """
        if not self.token or not self.created_blog_id:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {
            "name": f"Updated Perf Blog {random.randint(10000, 20000)}",
            "base_url": "https://updated-example.com"
        }

        with self.client.put(f"/api/v1/blogs/{self.created_blog_id}", json=payload, headers=headers, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Update blog failed: {response.status_code} {response.text}")

    @task
    def delete_blog(self):
        """
        Delete the blog we created, if any.
        """
        if not self.token or not self.created_blog_id:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        with self.client.delete(f"/api/v1/blogs/{self.created_blog_id}", headers=headers, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Delete blog failed: {response.status_code} {response.text}")
            else:
                self.created_blog_id = None

class AuthenticatedBlogUser(HttpUser):
    """
    Each "user" instance will:
      1) on_start() -> login to get a token
      2) run the tasks (create, list, update, delete)
    """
    tasks = [AuthenticatedBlogTasks]
    wait_time = between(1, 3)

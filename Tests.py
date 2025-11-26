import unittest
import requests
import uuid
import time

#Configuration
GATEWAY_URL = "http://127.0.0.1:8000/api/v1"
FRONTEND_URL = "http://127.0.0.1:5500"
USER_SERVICE_DIRECT = "http://127.0.0.1:8001"

#Random user generation
RANDOM_ID = str(uuid.uuid4())[:8]
TEST_EMAIL = f"Test_{RANDOM_ID}@cybertribe.com"
TEST_PASSWORD = "ThisIsTest1234!"

class SystemTests(unittest.TestCase):
    #Class variables for data sharing
    token = None
    user_id = None

    print(f"Starting Automated System Tests: {TEST_EMAIL}")
    print("-" * 60)

    #1. User Management Service (3 Unit Tests)

    def test_01_register_user(self):
        payload = {"email": TEST_EMAIL, "password": TEST_PASSWORD, "secret_key": "SecureTribe2025!"}
        response = requests.post(f"{GATEWAY_URL}/users/register", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.json())
        print(f"User Registration Test Passed: {TEST_EMAIL}")

    def test_02_login_user(self):
        payload = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
        response = requests.post(f"{GATEWAY_URL}/users/login", json=payload)
        self.assertEqual(response.status_code, 200)
        SystemTests.token = response.json()["token"]
        self.assertTrue (len(SystemTests.token) > 10) 
        print(f"User Login Test Passed: {TEST_EMAIL}")
    
    #Security test (Authentication defense)
    def test_03_wrong_password_login(self):
        payload = {"email": TEST_EMAIL, "password": "Gibberish!"}
        response = requests.post(f"{GATEWAY_URL}/users/login", json=payload)
        self.assertEqual(response.status_code, 401)
        print(f"Wrong Password Login Test Passed: {TEST_EMAIL}")

    #2. MT and Caching (3 Unit Tests)

    def test_04_translation_model(self):
        if not SystemTests.token: self.fail("No token available")
        headers = {"Authorization": f"Bearer {SystemTests.token}"}
        payload = {"text": f"Hello World {RANDOM_ID}", "target_lang": "nl"}
        response = requests.post(f"{GATEWAY_URL}/translate", json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["source"], "model")
        print(f"Translation Model Test Passed")

    def test_05_translation_cache(self):
        if not SystemTests.token: self.fail("No token available")
        headers = {"Authorization": f"Bearer {SystemTests.token}"}
        payload = {"text": f"Hello World {RANDOM_ID}", "target_lang": "nl"}
        response = requests.post(f"{GATEWAY_URL}/translate", json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["source"], "cache")
        print(f"Translation Cache Test Passed")
    
    def test_06_translation_different_language(self):
        if not SystemTests.token: self.fail("No token available")
        headers = {"Authorization": f"Bearer {SystemTests.token}"}
        payload = {"text": "Hello", "target_lang": "bg"}
        response = requests.post(f"{GATEWAY_URL}/translate", json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.json()["translation"], "Hallo")
        print(f"Different Language Translation Test Passed")
    
    #3. User Database (1 Unit Test)

    def test_07_database_persistence(self):
        if not SystemTests.token: self.fail("No token available")
        headers = {"Authorization": f"Bearer {SystemTests.token}"}
        response = requests.get(f"{GATEWAY_URL}/users/list", headers=headers)
        self.assertEqual(response.status_code, 200)
        users = response.json()["registered_users"]
        self.assertIn(TEST_EMAIL, users)
        print(f"User Database Persistence Test Passed: {TEST_EMAIL}")

    #4. API Gateway (3 Unit Test)

    #Security Test (Email validation)
    def test_08_email_validation(self):
        payload = {"email": "Hacker", "password": "ILOVEHACKING", "secret_key": "SecureTribe2025!"}
        response = requests.post(f"{GATEWAY_URL}/users/register", json=payload)
        self.assertEqual(response.status_code, 422)
        self.assertIn("detail", response.json())
        print(f"API Gateway Email Validation Test Passed")

    #Security Test (Access control)
    def test_09_gateway_security(self):
        response = requests.get(f"{GATEWAY_URL}/users/list")
        self.assertEqual(response.status_code, 401)
        print(f"API Gateway Security Test Passed")

    #Security Test (Secure Configuration)
    def test_10_method_tampering(self):
        payload = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
        response = requests.get(f"{GATEWAY_URL}/users/login", json=payload)
        self.assertEqual(response.status_code, 405)
        print(f"API Gateway Method Tampering Test Passed")

    #5. Frontend (1 Unit Test)

    def test_11_frontend_online(self):
        try:
            response = requests.get(f"{FRONTEND_URL}/Frontend/login.html")
            if response.status_code == 404:
                response = requests.get(f"{FRONTEND_URL}/login.html")
            self.assertEqual(response.status_code, 200)
            print(f"Frontend Online Test Passed")
        except requests.exceptions.ConnectionError:
            print(f"Frontend Online Test Failed: Unable to connect to {FRONTEND_URL}")

    #6. Integration Tests (5 Tests)

    def test_12_integration_register_flow(self):
        new_email = f"int_{RANDOM_ID}@cybertribe.com"
        payload = {"email": new_email, "password": "Test1234", "secret_key": "SecureTribe2025!"}
        response = requests.post(f"{GATEWAY_URL}/users/register", json=payload)
        self.assertIn("token", response.json())
        print(f"Integration Register Flow Test Passed")

    def test_13_integration_upload_text(self):
        headers = {"Authorization": f"Bearer {SystemTests.token}"}
        payload = {"text": "Integration Test", "target_lang": "nl"}
        response = requests.post(f"{GATEWAY_URL}/translate", json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        print(f"Integration Upload Text Test Passed")

    def test_14_integration_login_flow(self):
        payload = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
        login_response = requests.post(f"{GATEWAY_URL}/users/login", json=payload)
        temp_token = login_response.json()["token"]

        headers = {"Authorization": f"Bearer {temp_token}"}
        user_response = requests.get(f"{GATEWAY_URL}/users/list", headers=headers)
        self.assertEqual(user_response.status_code, 200)
        print(f"Integration Login Flow Test Passed")

    def test_15_integration_MT_Latency(self):
        start = time.time()
        headers = {"Authorization": f"Bearer {SystemTests.token}"}
        payload = {"text": "Latency Test", "target_lang": "nl"}
        response = requests.post(f"{GATEWAY_URL}/translate", json=payload, headers=headers)
        duration = time.time() - start
        self.assertTrue(duration < 5)
        print(f"Integration MT Latency Test Passed: {duration:.2f} seconds")
        
    #Security test (Session management)
    def test_16_integration_logout_flow(self):
        headers = {"Authorization": "Bearer "}
        response = requests.get(f"{GATEWAY_URL}/users/list", headers=headers)
        self.assertTrue(response.status_code in [401, 422, 500])
        print(f"Integration Logout Flow Test Passed")

    #7. Security Integration Tests (4 Tests)

    #Security test (SQL Injection defense)
    def test_17_sql_injection_attempt(self):
        payload = {"email": f"Test_{RANDOM_ID}@gmail.com", "password": "' OR '1'='1"}
        response = requests.post(f"{GATEWAY_URL}/users/login", json=payload)
        self.assertTrue(response.status_code in [401, 422])
        print(f"SQL Injection Attempt Test Passed")

    #Security test (XSS defense)
    def test_18_xss_payload_handling_MT(self):
        if not SystemTests.token: self.fail("No token available")
        headers = {"Authorization": f"Bearer {SystemTests.token}"}
        malicious_script = "<script>alert('XSS')</script>"
        payload = {"text": malicious_script, "target_lang": "nl"}
        response = requests.post(f"{GATEWAY_URL}/translate", json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        result = response.json().get("translation", "")
        self.assertTrue(len(result) > 0, "Translation result is empty")
        self.assertNotIn("<script>", result, "Malicious script found in translation result")
        print(f"XSS Payload Handling in MT Test Passed")

    #Security test (Cryptohraphy defense)
    def test_19_token_tampering(self):
        if not SystemTests.token: self.fail("No token available")
        original_last_char = SystemTests.token[-1]
        replacement_char = 'A' if original_last_char != 'A' else 'B'
        fake_token = SystemTests.token[:-1] + replacement_char
        headers = {"Authorization": f"Bearer {fake_token}"}
        response = requests.get(f"{GATEWAY_URL}/users/list", headers=headers)
        self.assertEqual(response.status_code, 401)
        print(f"Token Tampering (JWT Forgery) Test Passed")

    #Security test (DoS with large payload)
    def test_20_large_payload_dos(self):
        if not SystemTests.token: self.fail("No token available")
        headers = {"Authorization": f"Bearer {SystemTests.token}"}
        large_text = "A" * 1_000_000
        payload = {"text": large_text, "target_lang": "nl"}

        try:
            response = requests.post(f"{GATEWAY_URL}/translate", json=payload, headers=headers, timeout=10)
            self.assertNotEqual(response.status_code, 500)
            print(f"Large Payload DoS Test Passed")
        
        except requests.exceptions.Timeout:
            self.fail("Large Payload DoS Test Failed: Request timed out")

if __name__ == "__main__":
    unittest.main(verbosity=0)
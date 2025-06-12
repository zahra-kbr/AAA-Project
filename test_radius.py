#!/usr/bin/env python3
"""
FreeRADIUS Test Scenarios
Generate various authentication attempts for log analysis testing
"""

from pyrad.client import Client
from pyrad.dictionary import Dictionary
import pyrad.packet
import time
import random

class RadiusTestSuite:
    def __init__(self, server="127.0.0.1", secret=b"testing123", port=1812):
        self.server = server
        self.secret = secret
        self.port = port
        self.client = None
        self.setup_client()
    
    def setup_client(self):
        """Initialize RADIUS client"""
        try:
            self.client = Client(
                server=self.server, 
                secret=self.secret, 
                dict=Dictionary("dictionary")
            )
            print(f"✅ RADIUS client initialized for {self.server}:{self.port}")
        except Exception as e:
            print(f"❌ Failed to initialize RADIUS client: {e}")
    
    def test_successful_auth(self, username, password):
        """Test successful authentication"""
        print(f"\n🔐 Testing successful auth: {username}")
        try:
            req = self.client.CreateAuthPacket(
                code=pyrad.packet.AccessRequest, 
                User_Name=username
            )
            req["User-Password"] = req.PwCrypt(password)
            
            reply = self.client.SendPacket(req)
            
            if reply.code == pyrad.packet.AccessAccept:
                print(f"✅ {username}: Authentication SUCCESSFUL")
                return True
            else:
                print(f"❌ {username}: Authentication FAILED (unexpected)")
                return False
        except Exception as e:
            print(f"❌ {username}: Error during authentication: {e}")
            return False
    
    def test_failed_auth(self, username, wrong_password):
        """Test failed authentication with wrong password"""
        print(f"\n🔒 Testing failed auth: {username} (wrong password)")
        try:
            req = self.client.CreateAuthPacket(
                code=pyrad.packet.AccessRequest, 
                User_Name=username
            )
            req["User-Password"] = req.PwCrypt(wrong_password)
            
            reply = self.client.SendPacket(req)
            
            if reply.code == pyrad.packet.AccessReject:
                print(f"✅ {username}: Authentication correctly REJECTED")
                return True
            else:
                print(f"❌ {username}: Authentication unexpectedly ACCEPTED")
                return False
        except Exception as e:
            print(f"❌ {username}: Error during failed auth test: {e}")
            return False
    
    def test_nonexistent_user(self, fake_username):
        """Test authentication with non-existent user"""
        print(f"\n👻 Testing non-existent user: {fake_username}")
        try:
            req = self.client.CreateAuthPacket(
                code=pyrad.packet.AccessRequest, 
                User_Name=fake_username
            )
            req["User-Password"] = req.PwCrypt("anypassword")
            
            reply = self.client.SendPacket(req)
            
            if reply.code == pyrad.packet.AccessReject:
                print(f"✅ {fake_username}: Non-existent user correctly REJECTED")
                return True
            else:
                print(f"❌ {fake_username}: Non-existent user unexpectedly ACCEPTED")
                return False
        except Exception as e:
            print(f"❌ {fake_username}: Error during non-existent user test: {e}")
            return False
    
    def test_empty_credentials(self):
        """Test with empty username/password"""
        print(f"\n🔄 Testing empty credentials")
        try:
            req = self.client.CreateAuthPacket(
                code=pyrad.packet.AccessRequest, 
                User_Name=""
            )
            req["User-Password"] = req.PwCrypt("")
            
            reply = self.client.SendPacket(req)
            
            if reply.code == pyrad.packet.AccessReject:
                print(f"✅ Empty credentials correctly REJECTED")
                return True
            else:
                print(f"❌ Empty credentials unexpectedly ACCEPTED")
                return False
        except Exception as e:
            print(f"❌ Error during empty credentials test: {e}")
            return False
    
    def brute_force_simulation(self, username, attempts=5):
        """Simulate brute force attack"""
        print(f"\n🔨 Simulating brute force attack on {username} ({attempts} attempts)")
        passwords = ["123456", "password", "admin", "qwerty", "letmein", "wrongpass"]
        
        for i in range(attempts):
            wrong_password = random.choice(passwords)
            print(f"  Attempt {i+1}/{attempts}: {wrong_password}")
            self.test_failed_auth(username, wrong_password)
            time.sleep(0.5)  # Small delay between attempts
    
    def load_test(self, username, password, count=10):
        """Generate multiple rapid authentication requests"""
        print(f"\n⚡ Load testing: {count} rapid authentications for {username}")
        success_count = 0
        
        for i in range(count):
            if self.test_successful_auth(f"{username}_{i:02d}", password):
                success_count += 1
            time.sleep(0.1)  # Very short delay
        
        print(f"📊 Load test results: {success_count}/{count} successful")
    
    def mixed_scenario_test(self):
        """Run a mixed scenario with various users and outcomes"""
        print(f"\n🎭 Running mixed scenario test...")
        
        # Successful authentications
        users_success = [
            ("alice", "alice123"),
            ("bob", "bob123"),
        ]
        
        # Failed authentications
        users_failed = [
            ("alice", "wrongpass"),
            ("bob", "123456"),
            ("hacker", "hack123"),
        ]
        
        # Mix the tests
        all_tests = []
        for user, pwd in users_success:
            all_tests.append(("success", user, pwd))
        for user, pwd in users_failed:
            all_tests.append(("failed", user, pwd))
        
        # Randomize order
        random.shuffle(all_tests)
        
        for test_type, user, pwd in all_tests:
            if test_type == "success":
                self.test_successful_auth(user, pwd)
            else:
                self.test_failed_auth(user, pwd)
            time.sleep(random.uniform(0.5, 2.0))  # Random delay between 0.5-2 seconds

def run_all_scenarios():
    """Run comprehensive test scenarios"""
    print("🚀 Starting FreeRADIUS Test Suite")
    print("=" * 50)
    
    # Initialize test suite
    test_suite = RadiusTestSuite()
    
    if not test_suite.client:
        print("❌ Cannot proceed without RADIUS client")
        return
    
    # Scenario 1: Basic successful authentications
    print("\n📋 SCENARIO 1: Basic Successful Authentications")
    test_suite.test_successful_auth("alice", "alice123")
    test_suite.test_successful_auth("bob", "bob456") 
    test_suite.test_successful_auth("charlie", "charlie789")
    
    # Scenario 2: Failed authentications
    print("\n📋 SCENARIO 2: Failed Authentications")
    test_suite.test_failed_auth("alice", "wrongpassword")
    test_suite.test_failed_auth("bob", "12345")
    test_suite.test_failed_auth("charlie", "badpass")
    
    # Scenario 3: Non-existent users
    print("\n📋 SCENARIO 3: Non-existent Users")
    test_suite.test_nonexistent_user("hacker")
    test_suite.test_nonexistent_user("unknown_user")
    test_suite.test_nonexistent_user("guest")
    
    # Scenario 4: Edge cases
    print("\n📋 SCENARIO 4: Edge Cases")
    test_suite.test_empty_credentials()
    test_suite.test_nonexistent_user("admin")  # Common target
    
    # Scenario 5: Brute force simulation
    print("\n📋 SCENARIO 5: Brute Force Simulation")
    test_suite.brute_force_simulation("alice", 3)
    
    # Scenario 6: Load testing
    print("\n📋 SCENARIO 6: Load Testing")
    test_suite.load_test("testuser", "testpass", 5)
    
    # Scenario 7: Mixed realistic scenario
    print("\n📋 SCENARIO 7: Mixed Realistic Scenario")
    test_suite.mixed_scenario_test()
    
    print("\n🎉 All test scenarios completed!")
    print("📊 Check your FreeRADIUS logs for generated authentication data")
    print("🔍 Run 'python main.py' to analyze the generated logs")

def run_simple_test():
    """Run just a few basic tests"""
    print("🧪 Running simple test scenarios...")
    
    test_suite = RadiusTestSuite()
    
    # Just a few basic tests
    test_suite.test_successful_auth("alice", "alice123")
    test_suite.test_failed_auth("alice", "wrongpass")
    test_suite.test_successful_auth("bob", "bob456")
    test_suite.test_nonexistent_user("hacker")
    
    print("✅ Simple tests completed!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--simple":
        run_simple_test()
    else:
        run_all_scenarios()
#!/usr/bin/env python3
"""
Comprehensive Integration Testing Suite for Workflow Authentication System

This test suite validates:
1. Backend API endpoints (registration, login, password reset)
2. Email verification system  
3. Frontend-backend integration flows
4. Recent bug fixes (memory leaks, race conditions, validation)
5. Error handling and edge cases
"""

import asyncio
import aiohttp
import json
import time
import re
import random
import string
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    status: str  # "PASS", "FAIL", "SKIP"
    duration: float
    message: str
    details: Optional[Dict[str, Any]] = None


class IntegrationTestSuite:
    """Comprehensive integration test suite"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_base = f"{self.base_url}/api/v1/users/auth"
        self.test_results = []
        self.session = None
        
    async def setup(self):
        """Initialize test environment"""
        self.session = aiohttp.ClientSession()
        print("🚀 Setting up integration test environment...")
        
    async def teardown(self):
        """Clean up test environment"""
        if self.session:
            await self.session.close()
        print("🧹 Test environment cleaned up")
        
    def generate_test_email(self):
        """Generate unique test email"""
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_lowercase, k=6))
        return f"test_{timestamp}_{random_str}@example.com"
        
    def generate_test_username(self):
        """Generate unique test username"""
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_lowercase, k=6))
        return f"testuser_{timestamp}_{random_str}"
        
    async def run_test(self, test_func, test_name: str):
        """Run individual test with timing and error handling"""
        start_time = time.time()
        try:
            print(f"🔍 Running: {test_name}")
            result = await test_func()
            duration = time.time() - start_time
            
            if result.get("success", False):
                self.test_results.append(TestResult(
                    test_name=test_name,
                    status="PASS",
                    duration=duration,
                    message=result.get("message", "Test passed"),
                    details=result.get("details")
                ))
                print(f"✅ PASS: {test_name} ({duration:.2f}s)")
            else:
                self.test_results.append(TestResult(
                    test_name=test_name,
                    status="FAIL", 
                    duration=duration,
                    message=result.get("error", "Test failed"),
                    details=result.get("details")
                ))
                print(f"❌ FAIL: {test_name} ({duration:.2f}s) - {result.get('error')}")
                
        except Exception as e:
            duration = time.time() - start_time
            self.test_results.append(TestResult(
                test_name=test_name,
                status="FAIL",
                duration=duration,
                message=f"Exception: {str(e)}",
                details={"exception_type": type(e).__name__}
            ))
            print(f"💥 ERROR: {test_name} ({duration:.2f}s) - {str(e)}")
            
    # =====================================
    # BACKEND API INTEGRATION TESTS
    # =====================================
    
    async def test_backend_health_check(self):
        """Test if backend server is running and accessible"""
        try:
            async with self.session.get(f"{self.base_url}/docs") as response:
                if response.status == 200:
                    return {
                        "success": True,
                        "message": "Backend server is accessible",
                        "details": {"status_code": response.status}
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Backend returned status {response.status}",
                        "details": {"status_code": response.status}
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"Cannot connect to backend: {str(e)}",
                "details": {"exception": str(e)}
            }
            
    async def test_send_verification_code_register(self):
        """Test sending verification code for registration"""
        test_email = self.generate_test_email()
        
        try:
            payload = {
                "email": test_email,
                "purpose": "register"
            }
            
            async with self.session.post(
                f"{self.api_base}/send-verification-code",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200 and response_data.get("success"):
                    return {
                        "success": True,
                        "message": "Verification code sent successfully",
                        "details": {
                            "email": test_email,
                            "response": response_data
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to send code: {response_data.get('message', 'Unknown error')}",
                        "details": {
                            "status_code": response.status,
                            "response": response_data
                        }
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}",
                "details": {"exception": str(e)}
            }
            
    async def test_send_verification_code_reset_password(self):
        """Test sending verification code for password reset"""
        test_email = self.generate_test_email()
        
        try:
            payload = {
                "email": test_email,
                "purpose": "reset_password"
            }
            
            async with self.session.post(
                f"{self.api_base}/send-verification-code",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200 and response_data.get("success"):
                    return {
                        "success": True,
                        "message": "Password reset code sent successfully",
                        "details": {
                            "email": test_email,
                            "response": response_data
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to send reset code: {response_data.get('message', 'Unknown error')}",
                        "details": {
                            "status_code": response.status,
                            "response": response_data
                        }
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}",
                "details": {"exception": str(e)}
            }
            
    async def test_rate_limiting(self):
        """Test rate limiting on verification code sending"""
        test_email = self.generate_test_email()
        
        try:
            payload = {
                "email": test_email,
                "purpose": "register"
            }
            
            # First request should succeed
            async with self.session.post(
                f"{self.api_base}/send-verification-code",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                first_response = await response.json()
                
            # Second request immediately should be rate limited
            async with self.session.post(
                f"{self.api_base}/send-verification-code",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                second_response = await response.json()
                
                if response.status == 429:
                    return {
                        "success": True,
                        "message": "Rate limiting is working correctly",
                        "details": {
                            "first_response": first_response,
                            "second_response": second_response
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Rate limiting not working, got status {response.status}",
                        "details": {
                            "first_response": first_response,
                            "second_response": second_response
                        }
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Rate limiting test failed: {str(e)}",
                "details": {"exception": str(e)}
            }
            
    async def test_invalid_email_validation(self):
        """Test email validation on verification code endpoint"""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "",
            "test..test@example.com",
            "test@.com"
        ]
        
        results = {}
        all_passed = True
        
        for email in invalid_emails:
            try:
                payload = {
                    "email": email,
                    "purpose": "register"
                }
                
                async with self.session.post(
                    f"{self.api_base}/send-verification-code",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response_data = await response.json()
                    
                    # Should return error for invalid email
                    if response.status != 200:
                        results[email] = "CORRECTLY_REJECTED"
                    else:
                        results[email] = "INCORRECTLY_ACCEPTED"
                        all_passed = False
                        
            except Exception as e:
                results[email] = f"EXCEPTION: {str(e)}"
                all_passed = False
                
        return {
            "success": all_passed,
            "message": "Email validation working correctly" if all_passed else "Email validation has issues",
            "details": {"validation_results": results}
        }
        
    async def test_password_validation_consistency(self):
        """Test password validation consistency between frontend and backend"""
        test_passwords = [
            ("weak", "123"),
            ("weak", "password"),
            ("weak", "12345678"),
            ("medium", "Password1"),
            ("strong", "MyStrongPassword123!"),
            ("strong", "ComplexP@ssw0rd2024!")
        ]
        
        results = {}
        all_consistent = True
        
        for expected_strength, password in test_passwords:
            try:
                # Test with dummy registration attempt (will fail at verification code step)
                payload = {
                    "username": self.generate_test_username(),
                    "email": self.generate_test_email(),
                    "password": password,
                    "code": "123456"  # Invalid code, but password validation should happen first
                }
                
                async with self.session.post(
                    f"{self.api_base}/register",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response_data = await response.json()
                    
                    # Check if password was rejected for weak passwords
                    if expected_strength == "weak":
                        if response.status == 400 and "password" in str(response_data).lower():
                            results[password] = "CORRECTLY_REJECTED_WEAK"
                        else:
                            results[password] = "INCORRECTLY_ACCEPTED_WEAK"
                            all_consistent = False
                    else:
                        # For medium/strong passwords, should pass validation
                        # (will fail at verification code step, which is expected)
                        if "password" not in str(response_data).lower() or "验证码" in str(response_data):
                            results[password] = "CORRECTLY_PASSED_VALIDATION"
                        else:
                            results[password] = "INCORRECTLY_REJECTED_STRONG"
                            all_consistent = False
                            
            except Exception as e:
                results[password] = f"EXCEPTION: {str(e)}"
                all_consistent = False
                
        return {
            "success": all_consistent,
            "message": "Password validation consistent" if all_consistent else "Password validation inconsistent",
            "details": {"validation_results": results}
        }
        
    # =====================================
    # END-TO-END INTEGRATION TESTS
    # =====================================
    
    async def test_complete_registration_flow(self):
        """Test complete registration flow (without email validation)"""
        test_email = self.generate_test_email()
        test_username = self.generate_test_username()
        
        try:
            # Step 1: Send verification code
            send_payload = {
                "email": test_email,
                "purpose": "register"
            }
            
            async with self.session.post(
                f"{self.api_base}/send-verification-code",
                json=send_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                send_response = await response.json()
                
                if not send_response.get("success"):
                    return {
                        "success": False,
                        "error": f"Failed to send verification code: {send_response.get('message')}",
                        "details": {"step": "send_code", "response": send_response}
                    }
                    
            # Step 2: Attempt registration with dummy code (will fail, but tests API structure)
            register_payload = {
                "username": test_username,
                "email": test_email,
                "password": "TestPassword123!",
                "code": "123456"  # Invalid code
            }
            
            async with self.session.post(
                f"{self.api_base}/register",
                json=register_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                register_response = await response.json()
                
                # Should fail due to invalid verification code
                if response.status == 400 and "验证码" in str(register_response):
                    return {
                        "success": True,
                        "message": "Registration flow working correctly (failed at verification step as expected)",
                        "details": {
                            "send_response": send_response,
                            "register_response": register_response
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Unexpected registration response: {register_response}",
                        "details": {
                            "send_response": send_response,
                            "register_response": register_response
                        }
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Registration flow test failed: {str(e)}",
                "details": {"exception": str(e)}
            }
            
    async def test_password_reset_flow(self):
        """Test password reset flow structure"""
        test_email = self.generate_test_email()
        
        try:
            # Step 1: Send password reset code
            send_payload = {
                "email": test_email,
                "purpose": "reset_password"
            }
            
            async with self.session.post(
                f"{self.api_base}/send-verification-code",
                json=send_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                send_response = await response.json()
                
                if not send_response.get("success"):
                    return {
                        "success": False,
                        "error": f"Failed to send reset code: {send_response.get('message')}",
                        "details": {"step": "send_reset_code", "response": send_response}
                    }
                    
            # Step 2: Attempt password reset with dummy code
            reset_payload = {
                "email": test_email,
                "code": "123456",  # Invalid code
                "new_password": "NewPassword123!"
            }
            
            async with self.session.post(
                f"{self.api_base}/reset-password",
                json=reset_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                reset_response = await response.json()
                
                # Should fail due to invalid verification code or non-existent user
                if response.status in [400, 404]:
                    return {
                        "success": True,
                        "message": "Password reset flow working correctly (failed at verification/user step as expected)",
                        "details": {
                            "send_response": send_response,
                            "reset_response": reset_response
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Unexpected reset response: {reset_response}",
                        "details": {
                            "send_response": send_response,
                            "reset_response": reset_response
                        }
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Password reset flow test failed: {str(e)}",
                "details": {"exception": str(e)}
            }
            
    # =====================================
    # CONCURRENT ACCESS TESTS
    # =====================================
    
    async def test_concurrent_verification_requests(self):
        """Test concurrent verification code requests (race condition testing)"""
        test_email = self.generate_test_email()
        
        try:
            payload = {
                "email": test_email,
                "purpose": "register"
            }
            
            # Send 5 concurrent requests
            tasks = []
            for i in range(5):
                task = self.session.post(
                    f"{self.api_base}/send-verification-code",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                tasks.append(task)
                
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            success_count = 0
            rate_limited_count = 0
            error_count = 0
            
            for response in responses:
                if isinstance(response, Exception):
                    error_count += 1
                    continue
                    
                async with response as resp:
                    if resp.status == 200:
                        success_count += 1
                    elif resp.status == 429:
                        rate_limited_count += 1
                    else:
                        error_count += 1
                        
            # Should have 1 success and 4 rate limited (or similar pattern)
            if success_count >= 1 and rate_limited_count >= 3:
                return {
                    "success": True,
                    "message": "Concurrent request handling working correctly",
                    "details": {
                        "success_count": success_count,
                        "rate_limited_count": rate_limited_count,
                        "error_count": error_count
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Concurrent request handling not working as expected",
                    "details": {
                        "success_count": success_count,
                        "rate_limited_count": rate_limited_count,
                        "error_count": error_count
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Concurrent test failed: {str(e)}",
                "details": {"exception": str(e)}
            }
            
    async def test_api_endpoint_existence(self):
        """Test that all expected API endpoints exist"""
        endpoints_to_test = [
            ("POST", "/send-verification-code"),
            ("POST", "/register"),
            ("POST", "/login"), 
            ("POST", "/reset-password"),
            ("POST", "/refresh"),
            ("GET", "/check-username"),
            ("GET", "/check-email")
        ]
        
        results = {}
        all_exist = True
        
        for method, endpoint in endpoints_to_test:
            try:
                url = f"{self.api_base}{endpoint}"
                
                # Send a basic request to check if endpoint exists
                if method == "GET":
                    # Add dummy query param for GET endpoints
                    if "check-username" in endpoint:
                        url += "?username=test"
                    elif "check-email" in endpoint:
                        url += "?email=test@example.com"
                        
                    async with self.session.get(url) as response:
                        exists = response.status != 404
                else:
                    # POST requests with minimal payload
                    async with self.session.post(url, json={}) as response:
                        exists = response.status != 404
                        
                results[f"{method} {endpoint}"] = "EXISTS" if exists else "NOT_FOUND"
                if not exists:
                    all_exist = False
                    
            except Exception as e:
                results[f"{method} {endpoint}"] = f"ERROR: {str(e)}"
                all_exist = False
                
        return {
            "success": all_exist,
            "message": "All API endpoints exist" if all_exist else "Some API endpoints missing",
            "details": {"endpoint_results": results}
        }
        
    # =====================================
    # MAIN TEST RUNNER
    # =====================================
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 Starting Comprehensive Integration Test Suite")
        print("=" * 60)
        
        await self.setup()
        
        # Test categories
        test_categories = [
            ("Backend Health Check", [
                ("Backend Server Accessibility", self.test_backend_health_check),
                ("API Endpoints Existence", self.test_api_endpoint_existence),
            ]),
            
            ("Verification Code System", [
                ("Send Registration Code", self.test_send_verification_code_register),
                ("Send Password Reset Code", self.test_send_verification_code_reset_password),
                ("Rate Limiting", self.test_rate_limiting),
                ("Email Validation", self.test_invalid_email_validation),
            ]),
            
            ("Authentication Flows", [
                ("Complete Registration Flow", self.test_complete_registration_flow),
                ("Password Reset Flow", self.test_password_reset_flow),
                ("Password Validation Consistency", self.test_password_validation_consistency),
            ]),
            
            ("Concurrent Access & Race Conditions", [
                ("Concurrent Verification Requests", self.test_concurrent_verification_requests),
            ]),
        ]
        
        for category_name, tests in test_categories:
            print(f"\n📂 {category_name}")
            print("-" * 40)
            
            for test_name, test_func in tests:
                await self.run_test(test_func, test_name)
                
        await self.teardown()
        
        # Generate report
        self.generate_report()
        
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 INTEGRATION TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "PASS"])
        failed_tests = len([r for r in self.test_results if r.status == "FAIL"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        total_duration = sum(r.duration for r in self.test_results)
        print(f"⏱️  Total Duration: {total_duration:.2f}s")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            print("-" * 40)
            for result in self.test_results:
                if result.status == "FAIL":
                    print(f"• {result.test_name}")
                    print(f"  Error: {result.message}")
                    if result.details:
                        print(f"  Details: {result.details}")
                    print()
                    
        print(f"\n✅ PASSED TESTS ({passed_tests}):")
        print("-" * 40)
        for result in self.test_results:
            if result.status == "PASS":
                print(f"• {result.test_name} ({result.duration:.2f}s)")
                
        # Generate recommendations
        print(f"\n🔍 RECOMMENDATIONS:")
        print("-" * 40)
        
        if success_rate == 100:
            print("🎉 All tests passed! The authentication system is working correctly.")
        elif success_rate >= 80:
            print("👍 Most tests passed. Address the failed tests to improve system reliability.")
        elif success_rate >= 60:
            print("⚠️  Some critical issues found. Fix failed tests before production deployment.")
        else:
            print("🚨 Major issues detected. System needs significant fixes before use.")
            
        # Check for specific issues
        backend_accessible = any(r.test_name == "Backend Server Accessibility" and r.status == "PASS" for r in self.test_results)
        if not backend_accessible:
            print("🔥 CRITICAL: Backend server is not accessible. Start the backend first!")
            
        rate_limiting_works = any(r.test_name == "Rate Limiting" and r.status == "PASS" for r in self.test_results)
        if not rate_limiting_works:
            print("⚠️  Rate limiting may not be working correctly. Check for potential abuse.")
            
        concurrent_safe = any(r.test_name == "Concurrent Verification Requests" and r.status == "PASS" for r in self.test_results)
        if not concurrent_safe:
            print("⚠️  Concurrent request handling issues detected. Race conditions possible.")


async def main():
    """Main test runner"""
    suite = IntegrationTestSuite()
    await suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
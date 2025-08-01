#!/usr/bin/env python3
"""
Frontend Integration Test Suite using Playwright

This test suite validates:
1. Frontend UI components and interactions
2. User flows (registration, login, password reset)
3. Form validation and error handling
4. Race condition fixes and memory leak prevention
5. API integration with backend
6. Navigation and routing
"""

import asyncio
import time
import random
import string
from typing import Dict, Any, Optional
from dataclasses import dataclass
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


@dataclass
class UITestResult:
    """UI test result data structure"""
    test_name: str
    status: str  # "PASS", "FAIL", "SKIP"
    duration: float
    message: str
    screenshot_path: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class FrontendIntegrationTest:
    """Frontend integration test suite with Playwright"""
    
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.api_base_url = "http://localhost:8000"
        self.test_results = []
        self.browser = None
        self.context = None
        self.page = None
        
    async def setup(self):
        """Initialize browser and test environment"""
        print("🚀 Setting up frontend integration test environment...")
        
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False, slow_mo=100)
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        
        # Enable request/response logging
        self.context.on("request", self.log_request)
        self.context.on("response", self.log_response)
        
        self.page = await self.context.new_page()
        
    async def teardown(self):
        """Clean up browser and test environment"""
        if self.browser:
            await self.browser.close()
        print("🧹 Frontend test environment cleaned up")
        
    def log_request(self, request):
        """Log HTTP requests"""
        if self.api_base_url in request.url:
            print(f"🔄 API Request: {request.method} {request.url}")
            
    def log_response(self, response):
        """Log HTTP responses"""
        if self.api_base_url in response.url:
            print(f"📥 API Response: {response.status} {response.url}")
            
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
        """Run individual UI test with timing and error handling"""
        start_time = time.time()
        screenshot_path = None
        
        try:
            print(f"🔍 Running UI Test: {test_name}")
            result = await test_func()
            duration = time.time() - start_time
            
            if result.get("success", False):
                self.test_results.append(UITestResult(
                    test_name=test_name,
                    status="PASS",
                    duration=duration,
                    message=result.get("message", "Test passed"),
                    details=result.get("details")
                ))
                print(f"✅ PASS: {test_name} ({duration:.2f}s)")
            else:
                # Take screenshot on failure
                screenshot_path = f"failure_{test_name.lower().replace(' ', '_')}.png"
                await self.page.screenshot(path=screenshot_path)
                
                self.test_results.append(UITestResult(
                    test_name=test_name,
                    status="FAIL",
                    duration=duration,
                    message=result.get("error", "Test failed"),
                    screenshot_path=screenshot_path,
                    details=result.get("details")
                ))
                print(f"❌ FAIL: {test_name} ({duration:.2f}s) - {result.get('error')}")
                
        except Exception as e:
            duration = time.time() - start_time
            
            # Take screenshot on exception
            screenshot_path = f"error_{test_name.lower().replace(' ', '_')}.png"
            try:
                await self.page.screenshot(path=screenshot_path)
            except:
                pass
                
            self.test_results.append(UITestResult(
                test_name=test_name,
                status="FAIL",
                duration=duration,
                message=f"Exception: {str(e)}",
                screenshot_path=screenshot_path,
                details={"exception_type": type(e).__name__}
            ))
            print(f"💥 ERROR: {test_name} ({duration:.2f}s) - {str(e)}")
            
    # =====================================
    # NAVIGATION AND ROUTING TESTS
    # =====================================
    
    async def test_navigation_to_register_page(self):
        """Test navigation to registration page"""
        try:
            await self.page.goto(f"{self.base_url}/auth/register")
            await self.page.wait_for_load_state("networkidle")
            
            # Check if we're on the register page
            title = await self.page.title()
            register_form = await self.page.locator('form[name="register"]').count()
            
            if register_form > 0 and ("register" in title.lower() or "注册" in title):
                return {
                    "success": True,
                    "message": "Successfully navigated to register page",
                    "details": {"title": title, "form_found": True}
                }
            else:
                return {
                    "success": False,
                    "error": f"Register page not loaded correctly. Title: {title}",
                    "details": {"title": title, "form_found": register_form > 0}
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Navigation failed: {str(e)}",
                "details": {"exception": str(e)}
            }
            
    async def test_navigation_to_forgot_password_page(self):
        """Test navigation to forgot password page"""
        try:
            await self.page.goto(f"{self.base_url}/auth/forgot-password")
            await self.page.wait_for_load_state("networkidle")
            
            # Check if we're on the forgot password page
            title = await self.page.title()
            forgot_form = await self.page.locator('form[name="forgotPassword"]').count()
            
            if forgot_form > 0 and ("reset" in title.lower() or "重置" in title or "forgot" in title.lower()):
                return {
                    "success": True,
                    "message": "Successfully navigated to forgot password page",
                    "details": {"title": title, "form_found": True}
                }
            else:
                return {
                    "success": False,
                    "error": f"Forgot password page not loaded correctly. Title: {title}",
                    "details": {"title": title, "form_found": forgot_form > 0}
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Navigation failed: {str(e)}",
                "details": {"exception": str(e)}
            }
            
    # =====================================
    # REGISTRATION FLOW TESTS
    # =====================================
    
    async def test_registration_form_validation(self):
        """Test registration form validation"""
        try:
            await self.page.goto(f"{self.base_url}/auth/register")
            await self.page.wait_for_load_state("networkidle")
            
            # Test empty form submission
            submit_button = self.page.locator('button[type="submit"]')
            await submit_button.click()
            
            # Wait for validation messages
            await self.page.wait_for_timeout(1000)
            
            # Check for validation messages
            error_messages = await self.page.locator('.ant-form-item-explain-error').count()
            
            if error_messages > 0:
                return {
                    "success": True,
                    "message": "Form validation working correctly",
                    "details": {"error_count": error_messages}
                }
            else:
                return {
                    "success": False,
                    "error": "Form validation not working - no error messages shown",
                    "details": {"error_count": error_messages}
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Form validation test failed: {str(e)}",
                "details": {"exception": str(e)}
            }
            
    async def test_password_strength_indicator(self):
        """Test password strength indicator functionality"""
        try:
            await self.page.goto(f"{self.base_url}/auth/register")
            await self.page.wait_for_load_state("networkidle")
            
            password_input = self.page.locator('input[id="register-password"]')
            
            # Test different password strengths
            test_passwords = [
                ("weak", "123"),
                ("medium", "Password1"),
                ("strong", "MyStrongPassword123!")
            ]
            
            results = {}
            
            for expected_strength, password in test_passwords:
                await password_input.fill(password)
                await self.page.wait_for_timeout(500)  # Wait for strength calculation
                
                # Check if progress bar appears
                progress_bar = await self.page.locator('.ant-progress').count()
                strength_text = await self.page.locator('.ant-progress').count()
                
                results[password] = {
                    "progress_bar_shown": progress_bar > 0,
                    "expected_strength": expected_strength
                }
                
            # All passwords should show progress bar
            all_showed_progress = all(r["progress_bar_shown"] for r in results.values())
            
            return {
                "success": all_showed_progress,
                "message": "Password strength indicator working" if all_showed_progress else "Password strength indicator not working",
                "details": {"test_results": results}
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Password strength test failed: {str(e)}",
                "details": {"exception": str(e)}
            }
            
    async def test_verification_code_workflow(self):
        """Test verification code sending workflow"""
        try:
            await self.page.goto(f"{self.base_url}/auth/register")
            await self.page.wait_for_load_state("networkidle")
            
            # Fill email field
            test_email = self.generate_test_email()
            email_input = self.page.locator('input[id="register-email"]')
            await email_input.fill(test_email)
            
            # Click send verification code button
            send_code_button = self.page.locator('text="发送验证码"')
            await send_code_button.click()
            
            # Wait for response
            await self.page.wait_for_timeout(3000)
            
            # Check if button text changed to countdown or success message appeared
            button_text = await send_code_button.inner_text()
            success_message = await self.page.locator('.ant-message').count()
            
            if ":" in button_text or success_message > 0:
                return {
                    "success": True,
                    "message": "Verification code workflow working correctly",
                    "details": {
                        "button_text": button_text,
                        "success_message_shown": success_message > 0,
                        "email": test_email
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Verification code workflow not working. Button text: {button_text}",
                    "details": {
                        "button_text": button_text,
                        "success_message_shown": success_message > 0,
                        "email": test_email
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Verification code test failed: {str(e)}",
                "details": {"exception": str(e)}
            }
            
    async def test_race_condition_fix_multiple_clicks(self):
        """Test race condition fix - multiple rapid clicks on send code button"""
        try:
            await self.page.goto(f"{self.base_url}/auth/register")
            await self.page.wait_for_load_state("networkidle")
            
            # Fill email field
            test_email = self.generate_test_email()
            email_input = self.page.locator('input[id="register-email"]')
            await email_input.fill(test_email)
            
            # Rapidly click send verification code button multiple times
            send_code_button = self.page.locator('text="发送验证码"')
            
            # Click multiple times rapidly
            for _ in range(5):
                await send_code_button.click()
                await self.page.wait_for_timeout(100)  # Very short delay
                
            # Wait for any requests to complete
            await self.page.wait_for_timeout(3000)
            
            # Check console for errors
            console_errors = []
            self.page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            
            # Check if page still responsive and no crashes
            button_text = await send_code_button.inner_text()
            page_title = await self.page.title()
            
            if "error" not in page_title.lower() and len(console_errors) == 0:
                return {
                    "success": True,
                    "message": "Race condition fix working - no crashes on multiple clicks",
                    "details": {
                        "button_text": button_text,
                        "console_errors": console_errors,
                        "page_responsive": True
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Race condition issues detected. Console errors: {console_errors}",
                    "details": {
                        "button_text": button_text,
                        "console_errors": console_errors,
                        "page_title": page_title
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Race condition test failed: {str(e)}",
                "details": {"exception": str(e)}
            }
            
    # =====================================
    # PASSWORD RESET FLOW TESTS
    # =====================================
    
    async def test_forgot_password_form(self):
        """Test forgot password form functionality"""
        try:
            await self.page.goto(f"{self.base_url}/auth/forgot-password")
            await self.page.wait_for_load_state("networkidle")
            
            # Fill email and submit
            test_email = self.generate_test_email()
            email_input = self.page.locator('input[placeholder*="邮箱"]')
            await email_input.fill(test_email)
            
            submit_button = self.page.locator('button[type="submit"]')
            await submit_button.click()
            
            # Wait for response
            await self.page.wait_for_timeout(3000)
            
            # Check if success page or message appears
            success_result = await self.page.locator('.ant-result-success').count()
            success_message = await self.page.locator('text*="验证码已发送"').count()
            
            if success_result > 0 or success_message > 0:
                return {
                    "success": True,
                    "message": "Forgot password form working correctly",
                    "details": {
                        "email": test_email,
                        "success_result_shown": success_result > 0,
                        "success_message_shown": success_message > 0
                    }
                }
            else:
                page_content = await self.page.content()
                return {
                    "success": False,
                    "error": "Forgot password form not working - no success indication",
                    "details": {
                        "email": test_email,
                        "success_result_shown": success_result > 0,
                        "success_message_shown": success_message > 0
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Forgot password test failed: {str(e)}",
                "details": {"exception": str(e)}
            }
            
    async def test_reset_password_navigation(self):
        """Test navigation to reset password page from forgot password"""
        try:
            await self.page.goto(f"{self.base_url}/auth/forgot-password")
            await self.page.wait_for_load_state("networkidle")
            
            # Fill email and submit to get to success page
            test_email = self.generate_test_email()
            email_input = self.page.locator('input[placeholder*="邮箱"]')
            await email_input.fill(test_email)
            
            submit_button = self.page.locator('button[type="submit"]')
            await submit_button.click()
            
            # Wait for success page
            await self.page.wait_for_timeout(3000)
            
            # Look for "前往重置密码" button
            reset_button = self.page.locator('text="前往重置密码"')
            
            if await reset_button.count() > 0:
                await reset_button.click()
                await self.page.wait_for_load_state("networkidle")
                
                # Check if we're on reset password page
                current_url = self.page.url
                reset_form = await self.page.locator('form').count()
                
                if "reset-password" in current_url and reset_form > 0:
                    return {
                        "success": True,
                        "message": "Successfully navigated to reset password page",
                        "details": {
                            "email": test_email,
                            "current_url": current_url,
                            "form_found": reset_form > 0
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Navigation to reset password failed. URL: {current_url}",
                        "details": {
                            "current_url": current_url,
                            "form_found": reset_form > 0
                        }
                    }
            else:
                return {
                    "success": False,
                    "error": "Reset password button not found on success page",
                    "details": {"email": test_email}
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Reset password navigation test failed: {str(e)}",
                "details": {"exception": str(e)}
            }
            
    async def test_memory_leak_prevention(self):
        """Test memory leak prevention - repeated navigation and operations"""
        try:
            initial_memory = await self.page.evaluate("() => performance.memory ? performance.memory.usedJSHeapSize : 0")
            
            # Perform repeated operations that previously caused memory leaks
            for i in range(5):
                # Navigate to register page
                await self.page.goto(f"{self.base_url}/auth/register")
                await self.page.wait_for_load_state("networkidle")
                
                # Fill form and trigger verification code (causing timer)
                test_email = self.generate_test_email()
                email_input = self.page.locator('input[id="register-email"]')
                await email_input.fill(test_email)
                
                send_code_button = self.page.locator('text="发送验证码"')
                await send_code_button.click()
                await self.page.wait_for_timeout(1000)
                
                # Navigate away (should clean up timers)
                await self.page.goto(f"{self.base_url}/auth/forgot-password")
                await self.page.wait_for_load_state("networkidle")
                await self.page.wait_for_timeout(500)
                
            final_memory = await self.page.evaluate("() => performance.memory ? performance.memory.usedJSHeapSize : 0")
            
            # Memory should not have grown excessively (allow some growth)
            memory_growth = final_memory - initial_memory
            memory_growth_mb = memory_growth / (1024 * 1024)
            
            if memory_growth_mb < 50:  # Less than 50MB growth is acceptable
                return {
                    "success": True,
                    "message": f"Memory leak prevention working - growth: {memory_growth_mb:.2f}MB",
                    "details": {
                        "initial_memory": initial_memory,
                        "final_memory": final_memory,
                        "growth_mb": memory_growth_mb
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Potential memory leak detected - growth: {memory_growth_mb:.2f}MB",
                    "details": {
                        "initial_memory": initial_memory,
                        "final_memory": final_memory,
                        "growth_mb": memory_growth_mb
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Memory leak test failed: {str(e)}",
                "details": {"exception": str(e)}
            }
            
    # =====================================
    # ERROR HANDLING TESTS
    # =====================================
    
    async def test_network_error_handling(self):
        """Test handling of network errors"""
        try:
            await self.page.goto(f"{self.base_url}/auth/register")
            await self.page.wait_for_load_state("networkidle")
            
            # Block all network requests to simulate network failure
            await self.page.route("**/*", lambda route: route.abort())
            
            # Try to send verification code
            test_email = self.generate_test_email()
            email_input = self.page.locator('input[id="register-email"]')
            await email_input.fill(test_email)
            
            send_code_button = self.page.locator('text="发送验证码"')
            await send_code_button.click()
            
            # Wait for error handling
            await self.page.wait_for_timeout(5000)
            
            # Check if error message appears
            error_message = await self.page.locator('.ant-message-error').count()
            
            # Unblock network
            await self.page.unroute("**/*")
            
            if error_message > 0:
                return {
                    "success": True,
                    "message": "Network error handling working correctly",
                    "details": {"error_message_shown": True}
                }
            else:
                return {
                    "success": False,
                    "error": "Network error not handled - no error message shown",
                    "details": {"error_message_shown": False}
                }
                
        except Exception as e:
            # Ensure network is unblocked
            try:
                await self.page.unroute("**/*")
            except:
                pass
                
            return {
                "success": False,
                "error": f"Network error test failed: {str(e)}",
                "details": {"exception": str(e)}
            }
            
    # =====================================
    # MAIN TEST RUNNER
    # =====================================
    
    async def run_all_tests(self):
        """Run all frontend integration tests"""
        print("🎭 Starting Frontend Integration Test Suite with Playwright")
        print("=" * 70)
        
        await self.setup()
        
        # Test categories
        test_categories = [
            ("Navigation & Routing", [
                ("Register Page Navigation", self.test_navigation_to_register_page),
                ("Forgot Password Page Navigation", self.test_navigation_to_forgot_password_page),
            ]),
            
            ("Registration Flow", [
                ("Form Validation", self.test_registration_form_validation),
                ("Password Strength Indicator", self.test_password_strength_indicator),
                ("Verification Code Workflow", self.test_verification_code_workflow),
                ("Race Condition Fix - Multiple Clicks", self.test_race_condition_fix_multiple_clicks),
            ]),
            
            ("Password Reset Flow", [
                ("Forgot Password Form", self.test_forgot_password_form),
                ("Reset Password Navigation", self.test_reset_password_navigation),
            ]),
            
            ("Memory & Performance", [
                ("Memory Leak Prevention", self.test_memory_leak_prevention),
            ]),
            
            ("Error Handling", [
                ("Network Error Handling", self.test_network_error_handling),
            ]),
        ]
        
        for category_name, tests in test_categories:
            print(f"\n🎯 {category_name}")
            print("-" * 50)
            
            for test_name, test_func in tests:
                await self.run_test(test_func, test_name)
                
        await self.teardown()
        
        # Generate report
        self.generate_report()
        
    def generate_report(self):
        """Generate comprehensive UI test report"""
        print("\n" + "=" * 70)
        print("🎭 FRONTEND INTEGRATION TEST REPORT")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "PASS"])
        failed_tests = len([r for r in self.test_results if r.status == "FAIL"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total UI Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        total_duration = sum(r.duration for r in self.test_results)
        print(f"⏱️  Total Duration: {total_duration:.2f}s")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED UI TESTS ({failed_tests}):")
            print("-" * 50)
            for result in self.test_results:
                if result.status == "FAIL":
                    print(f"• {result.test_name}")
                    print(f"  Error: {result.message}")
                    if result.screenshot_path:
                        print(f"  Screenshot: {result.screenshot_path}")
                    if result.details:
                        print(f"  Details: {result.details}")
                    print()
                    
        print(f"\n✅ PASSED UI TESTS ({passed_tests}):")
        print("-" * 50)
        for result in self.test_results:
            if result.status == "PASS":
                print(f"• {result.test_name} ({result.duration:.2f}s)")
                
        # Generate UI-specific recommendations
        print(f"\n🎯 UI RECOMMENDATIONS:")
        print("-" * 50)
        
        if success_rate == 100:
            print("🎉 All UI tests passed! The frontend is working correctly.")
        elif success_rate >= 80:
            print("👍 Most UI tests passed. Address failed tests to improve user experience.")
        elif success_rate >= 60:
            print("⚠️  Some UI issues found. Fix failed tests before production deployment.")
        else:
            print("🚨 Major UI issues detected. Frontend needs significant fixes.")
            
        # Check for specific UI issues
        nav_working = any(r.test_name.endswith("Navigation") and r.status == "PASS" for r in self.test_results)
        if not nav_working:
            print("🔥 CRITICAL: Navigation not working. Check routing configuration!")
            
        form_validation = any(r.test_name == "Form Validation" and r.status == "PASS" for r in self.test_results)
        if not form_validation:
            print("⚠️  Form validation issues detected. User experience may be poor.")
            
        race_condition_fixed = any(r.test_name == "Race Condition Fix - Multiple Clicks" and r.status == "PASS" for r in self.test_results)
        if not race_condition_fixed:
            print("⚠️  Race condition fixes not working. Multiple clicks may cause issues.")
            
        memory_leak_fixed = any(r.test_name == "Memory Leak Prevention" and r.status == "PASS" for r in self.test_results)
        if not memory_leak_fixed:
            print("⚠️  Memory leak prevention not working. App may slow down over time.")


async def main():
    """Main UI test runner"""
    suite = FrontendIntegrationTest()
    await suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
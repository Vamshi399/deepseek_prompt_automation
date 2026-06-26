# input the prompt in deepseek openend and input the prompt in the deepseek chat from input_prompts file and then click the submit button and then get the response from the deepseek chat and wait for the submit button to appear and give the second prompt and so on till the loop condition gets invalidated

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# --- Configuration & Selectors ---
CHAT_INPUT_SELECTOR = "textarea[placeholder*='Message DeepSeek']"
SUBMIT_BUTTON_SELECTOR = "div[role='button'].ds-button--primary"
SUBMIT_BUTTON_DISABLED_SELECTOR = "div[role='button'].ds-button--disabled"
CONTINUE_BUTTON_SELECTOR = "div[role='button'] span.ds-button__content"
RESPONSE_SELECTOR = "div[data-message-author-role='assistant'] .markdown-body"
LOADING_INDICATOR_SELECTOR = "div.ds-icon-loading"
STOP_GENERATING_BUTTON_SELECTOR = "div[role='button'] .ds-icon-stop"

def wait_for_response_completion(driver, wait, timeout=180):
    """
    Wait for the response to complete by checking for:
    1. Stop button disappears
    2. No loading indicators
    3. Response content stabilizes (no changes for a few seconds)
    4. Submit button becomes enabled
    """
    try:
        # First, wait for stop/loading indicator to disappear
        print("   Waiting for stop/loading indicators to disappear...")
        
        # Check for stop button and wait for it to disappear
        try:
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, STOP_GENERATING_BUTTON_SELECTOR)))
            print("   ✓ Stop button disappeared")
        except Exception as e:
            print(f"   ℹ Stop button not found or already gone: {e}")
        
        # Wait for any loading indicator to disappear
        try:
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, LOADING_INDICATOR_SELECTOR)))
            print("   ✓ Loading indicator disappeared")
        except Exception as e:
            print(f"   ℹ Loading indicator not found or already gone: {e}")
        
        # Wait for the response content to stabilize (no changes for 3 seconds)
        print("   Waiting for response content to stabilize...")
        last_response = ""
        stable_count = 0
        start_time = time.time()
        
        while time.time() - start_time < 60:  # Max 60 seconds to stabilize
            try:
                response_elements = driver.find_elements(By.CSS_SELECTOR, RESPONSE_SELECTOR)
                if response_elements:
                    current_response = response_elements[-1].text
                    
                    # Check if response length has changed
                    if len(current_response) == len(last_response):
                        stable_count += 1
                    else:
                        stable_count = 0
                        last_response = current_response
                        print(f"   Response still growing... (current length: {len(current_response)})")
                    
                    if stable_count >= 3:  # No changes for 3 checks (3 seconds)
                        print(f"   ✓ Response stabilized (length: {len(current_response)})")
                        break
                else:
                    continue
            except Exception as e:
                print(f"   ⚠ Error checking response: {e}")
                time.sleep(1)
                continue
            
            time.sleep(1)
        
        # Now wait for submit button to become clickable (enabled)
        print("   Waiting for submit button to become enabled...")
        submit_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, SUBMIT_BUTTON_SELECTOR))
        )
        print("   ✓ Submit button is now enabled")
        
        # Additional wait to ensure UI is fully updated
        time.sleep(2)
        
        # Check for Continue button which might appear for long responses
        continue_buttons = driver.find_elements(By.XPATH, "//span[text()='Continue']/ancestor::div[@role='button']")
        if continue_buttons:
            print("--- Clicking Continue button ---")
            continue_buttons[0].click()
            time.sleep(2)
            
            # Wait for generation to complete after clicking Continue
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, STOP_GENERATING_BUTTON_SELECTOR)))
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, SUBMIT_BUTTON_SELECTOR)))
            time.sleep(2)
            
        return True
        
    except Exception as e:
        print(f"⚠ Warning: Error while waiting for response completion: {e}")
        # Add extra safety delay
        print("Adding extra 15 seconds safety delay...")
        time.sleep(15)
        return False

def automate_prompts(prompts_list):
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 120)
    
    try:
        # Find the DeepSeek tab
        target_handle = None
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            if "chat.deepseek.com" in driver.current_url:
                print("Found existing DeepSeek tab.")
                target_handle = handle
                break
                
        if not target_handle:
            print("Error: Could not find DeepSeek tab. Please open it manually.")
            return []
        
        # Wait for the page to be fully loaded
        time.sleep(2)
        
        # Process each prompt in sequence
        for idx, prompt in enumerate(prompts_list, 1):
            print(f"\n{'='*50}")
            print(f"Processing prompt {idx}/{len(prompts_list)}")
            print(f"Prompt: {prompt[:100]}..." if len(prompt) > 100 else f"Prompt: {prompt}")
            print(f"{'='*50}")
            
            # Wait for the chat input to be available and enter the prompt
            try:
                # Clear any existing text in the input
                chat_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, CHAT_INPUT_SELECTOR)))
                chat_input.clear()
                time.sleep(0.5)  # Small delay after clear
                chat_input.send_keys(prompt)
                print("✓ Prompt entered")
            except Exception as e:
                print(f"✗ Error entering prompt: {e}")
                continue
            
            # Wait for and click the submit button
            try:
                # Wait for submit button to be clickable
                submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, SUBMIT_BUTTON_SELECTOR)))
                submit_button.click()
                print("✓ Submit button clicked")
            except Exception as e:
                print(f"✗ Error clicking submit button: {e}")
                continue
            
            # Wait for the response to complete before proceeding to next prompt
            print("\nWaiting for response completion...")
            if wait_for_response_completion(driver, wait):
                print("✓ Response completed successfully")
            else:
                print("⚠ Response may not have completed properly. Adding extra delay...")
                time.sleep(20)  # Extra safety delay
            
            # Additional delay between prompts to ensure everything is clean
            time.sleep(3)
            print(f"✓ Completed prompt {idx}")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("\nAll prompts processed!")
        # Don't close the browser

if __name__ == "__main__":
    # Example usage:
    my_prompts = []
    
    # Using a smaller range for demonstration purposes
    for problem_number in range(3706, 3708):
        prompt = f"Please provide the most time- and space-optimized Python 3 solution for LeetCode Problem {problem_number}. Include a detailed explanation of the logic, dry-run, a step-by-step time & space complexity analysis (using Big-O notation), and ensure it handles all edge cases."
        my_prompts.append(prompt)
    
    if my_prompts:
        automate_prompts(my_prompts)
    else:
        print("No prompts found in the input file to process.")
# input the prompt in deepseek openend and input the prompt in the deepseek chat and then click the submit button and then get the response from the deepseek chat and wait for the submit button to appear and give the second prompt and so on till the loop condition gets invalidated

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# --- Configuration & Selectors ---
# These CSS selectors are for the DeepSeek Chat UI.

CHAT_INPUT_SELECTOR = "textarea[placeholder*='Message DeepSeek']"
SUBMIT_BUTTON_SELECTOR = "div[role='button'].ds-button--primary"
SUBMIT_BUTTON_DISABLED_SELECTOR = "div[role='button'].ds-button--disabled"
CONTINUE_BUTTON_SELECTOR = "div[role='button'] span.ds-button__content" # Targets the span with "Continue"
RESPONSE_SELECTOR = "div[data-message-author-role='assistant'] .markdown-body"


def automate_prompts(prompts_list):
    # Connect to an existing Chrome instance using remote debugging
    # Note: You MUST start Chrome from the terminal with the remote debugging flag:
    # e.g., chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\ChromeProfile"
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 120) # Wait up to 120 seconds for elements/responses
    
    try:
        target_handle = None
        # Switch to the DeepSeek tab if multiple tabs are open
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            if "chat.deepseek.com" in driver.current_url:
                print("Found existing DeepSeek tab.")
                target_handle = handle
                break
        if not target_handle:
            print(f"Error: Could not find an open tab with URL containing 'chat.deepseek.com'. Please open it manually and re-run the script.")
            return []
        
        # Loop through prompts until the list is exhausted (loop condition invalidated)
        for prompt in prompts_list:

            # Count message containers before sending a new prompt to identify the new one later
            # responses_before = len(driver.find_elements(By.CSS_SELECTOR, ASSISTANT_MESSAGE_SELECTOR))

            # 1. Wait for the chat input and enter the prompt
            chat_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, CHAT_INPUT_SELECTOR)))
            chat_input.clear()
            chat_input.send_keys(prompt)
            
            # 2. Wait for the submit button and click it
            submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, SUBMIT_BUTTON_SELECTOR)))
            submit_button.click()
            
            # 3. Get the response from the DeepSeek chat
            # A brief pause to allow the full response to be streamed.
            time.sleep(10) 
            # Wait for the UI to be ready for the next prompt.
            # The disabled button appears when generation is complete, signaling readiness for new input.
            # Or, a "Continue" button may appear for long responses.
            finished_or_paused = EC.any_of(
                EC.presence_of_element_located((By.CSS_SELECTOR, SUBMIT_BUTTON_DISABLED_SELECTOR)),
                EC.presence_of_element_located((By.XPATH, "//span[text()='Continue']/ancestor::div[@role='button']"))
            )
            element = wait.until(finished_or_paused)
            if "Continue" in element.text:
                print("--- Clicking Continue button ---")
                element.click()
                # After clicking continue, wait for the generation to finish again
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SUBMIT_BUTTON_DISABLED_SELECTOR)))
        
    finally:
        # Prevent closing the existing browser session when the script finishes
        pass

if __name__ == "__main__":
    # Example usage:
    my_prompts = []
    
    # Using a smaller range for demonstration purposes
    for problem_number in range(3706, 3708):
        prompt = f"Please provide the most time- and space-optimized Python 3 solution for LeetCode Problem {problem_number}. Include a detailed explanation of the logic, dry-run, a step-by-step time & space complexity analysis (using Big-O notation), and ensure it handles all edge cases."
        my_prompts.append(prompt)
    
    automate_prompts(my_prompts)
    

"""
PART 2: Human-like Behavior Module
This module contains all functions related to simulating human browsing behavior
to avoid bot detection. Import this into your main stealth driver script.
"""

import time
import random

def human_like_delay(min_seconds=1, max_seconds=3):
    """
    Add random delays to mimic human behavior
    
    Args:
        min_seconds (float): Minimum delay time
        max_seconds (float): Maximum delay time
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def human_like_typing(element, text):
    """
    Type text with human-like delays between keystrokes
    
    Args:
        element: Selenium WebElement to type into
        text (str): Text to type
    """
    element.clear()
    human_like_delay(0.5, 1.0)  # Pause before typing
    
    for char in text:
        element.send_keys(char)
        # Random typing speed between 50ms and 200ms per character
        time.sleep(random.uniform(0.05, 0.2))
    
    human_like_delay(0.3, 0.7)  # Pause after typing

def simulate_human_browsing(driver):
    """
    Simulate realistic human browsing behavior
    
    Args:
        driver: Selenium WebDriver instance
    """
    print("Simulating human browsing behavior...")
    
    # Random mouse movements (simulated through JavaScript)
    driver.execute_script("""
        var event = new MouseEvent('mousemove', {
            clientX: Math.random() * window.innerWidth,
            clientY: Math.random() * window.innerHeight
        });
        document.dispatchEvent(event);
    """)
    
    human_like_delay(1, 2)
    
    # Simulate reading the page (scroll down slowly)
    driver.execute_script("window.scrollTo(0, 200);")
    human_like_delay(0.5, 1)
    driver.execute_script("window.scrollTo(0, 400);")
    human_like_delay(0.5, 1)
    driver.execute_script("window.scrollTo(0, 0);")  # Scroll back to top
    
    human_like_delay(1, 2)

def random_mouse_movement(driver):
    """
    Generate random mouse movements across the page
    
    Args:
        driver: Selenium WebDriver instance
    """
    movements = random.randint(2, 5)  # Random number of movements
    
    for _ in range(movements):
        x = random.randint(100, 1800)
        y = random.randint(100, 900)
        
        driver.execute_script(f"""
            var event = new MouseEvent('mousemove', {{
                clientX: {x},
                clientY: {y}
            }});
            document.dispatchEvent(event);
        """)
        
        human_like_delay(0.1, 0.3)

def simulate_reading_behavior(driver, reading_time=None):
    """
    Simulate human reading behavior with eye movement patterns
    
    Args:
        driver: Selenium WebDriver instance
        reading_time (float): Optional specific reading time, otherwise random
    """
    if reading_time is None:
        reading_time = random.uniform(3, 8)
    
    print(f"Simulating reading for {reading_time:.1f} seconds...")
    
    # Simulate reading patterns - scroll down slowly, pause, scroll back up
    scroll_positions = [0, 150, 300, 450, 300, 150, 0]
    
    for position in scroll_positions:
        driver.execute_script(f"window.scrollTo(0, {position});")
        human_like_delay(reading_time / len(scroll_positions) * 0.8, 
                        reading_time / len(scroll_positions) * 1.2)

def human_like_form_interaction(element, text, typing_style="normal"):
    """
    Advanced human-like form interaction with different typing styles
    
    Args:
        element: Selenium WebElement
        text (str): Text to enter
        typing_style (str): "slow", "normal", "fast", or "variable"
    """
    element.clear()
    human_like_delay(0.3, 0.8)  # Pause before typing
    
    # Different typing speeds based on style
    if typing_style == "slow":
        char_delay_range = (0.15, 0.35)
    elif typing_style == "fast":
        char_delay_range = (0.03, 0.08)
    elif typing_style == "variable":
        char_delay_range = (0.02, 0.4)  # Very variable
    else:  # normal
        char_delay_range = (0.05, 0.2)
    
    # Simulate occasional pauses (thinking)
    words = text.split()
    
    for i, word in enumerate(words):
        # Type the word
        for char in word:
            element.send_keys(char)
            time.sleep(random.uniform(*char_delay_range))
        
        # Add space if not the last word
        if i < len(words) - 1:
            element.send_keys(" ")
            
            # Occasionally pause between words (thinking)
            if random.random() < 0.3:  # 30% chance
                human_like_delay(0.5, 1.5)
    
    # Final pause after typing
    human_like_delay(0.2, 0.6)

def simulate_distraction(driver):
    """
    Simulate human distraction - looking away, checking other tabs, etc.
    
    Args:
        driver: Selenium WebDriver instance
    """
    print("Simulating human distraction...")
    
    # Simulate losing focus (like checking another tab)
    driver.execute_script("window.blur();")
    human_like_delay(2, 5)
    driver.execute_script("window.focus();")
    
    # Random mouse movements after "returning attention"
    random_mouse_movement(driver)

def human_like_page_load_behavior(driver, url):
    """
    Simulate realistic human behavior during page loading
    
    Args:
        driver: Selenium WebDriver instance
        url (str): URL to navigate to
    """
    print(f"Navigating to {url} with human-like behavior...")
    
    # Navigate to page
    driver.get(url)
    
    # Simulate waiting for page to load (human would wait and watch)
    human_like_delay(1, 3)
    
    # Simulate initial page scan (quick scroll to see page length)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
    human_like_delay(0.5, 1)
    driver.execute_script("window.scrollTo(0, 0);")
    
    # Brief pause as human processes the page
    human_like_delay(2, 4)

# Configuration constants for easy adjustment
class HumanBehaviorConfig:
    """Configuration class for human behavior parameters"""
    
    # Typing speeds (seconds between characters)
    TYPING_SPEED_SLOW = (0.15, 0.35)
    TYPING_SPEED_NORMAL = (0.05, 0.2)
    TYPING_SPEED_FAST = (0.03, 0.08)
    
    # Delay ranges (seconds)
    SHORT_DELAY = (0.5, 1.5)
    MEDIUM_DELAY = (1, 3)
    LONG_DELAY = (3, 6)
    
    # Mouse movement ranges
    MOUSE_MOVEMENT_COUNT = (2, 5)
    MOUSE_X_RANGE = (100, 1800)
    MOUSE_Y_RANGE = (100, 900)
    
    # Reading behavior
    READING_TIME_RANGE = (3, 8)
    DISTRACTION_PROBABILITY = 0.3  # 30% chance of distraction

# Example usage functions
def demonstrate_human_behavior(driver):
    """
    Demonstration function showing various human behaviors
    This is useful for testing and learning about the module
    """
    print("=== Demonstrating Human Behavior Module ===")
    
    print("1. Human-like delay...")
    human_like_delay(1, 2)
    
    print("2. Simulating browsing behavior...")
    simulate_human_browsing(driver)
    
    print("3. Random mouse movements...")
    random_mouse_movement(driver)
    
    print("4. Reading simulation...")
    simulate_reading_behavior(driver, 5)
    
    print("5. Distraction simulation...")
    simulate_distraction(driver)
    
    print("=== Human Behavior Demo Complete ===")

if __name__ == "__main__":
    print("Human Behavior Module - Part 2")
    print("This module provides functions for simulating human-like browsing behavior.")
    print("Import these functions into your main stealth driver script.")
    print("\nAvailable functions:")
    print("- human_like_delay(min_sec, max_sec)")
    print("- human_like_typing(element, text)")
    print("- simulate_human_browsing(driver)")
    print("- random_mouse_movement(driver)")
    print("- simulate_reading_behavior(driver)")
    print("- human_like_form_interaction(element, text, style)")
    print("- simulate_distraction(driver)")
    print("- human_like_page_load_behavior(driver, url)")

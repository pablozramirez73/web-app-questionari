import re
from playwright.sync_api import sync_playwright, Page, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Go to the application
    page.goto("http://127.0.0.1:5000/")

    # --- Registration ---
    page.get_by_role("link", name="Login").click()
    expect(page).to_have_url(re.compile(".*\/login"))
    page.get_by_role("link", name="Click to Register!").click()
    expect(page).to_have_url(re.compile(".*\/register"))

    # Fill out registration form
    page.get_by_label("Username").fill("testuser")
    page.get_by_label("Email").fill("testuser@example.com")
    page.get_by_label("Password").first.fill("password123")
    page.get_by_label("Repeat Password").fill("password123")
    page.get_by_role("button", name="Register").click()
    expect(page).to_have_url(re.compile(".*\/login"))

    # --- Login ---
    page.get_by_label("Username").fill("testuser")
    page.get_by_label("Password").fill("password123")
    page.get_by_role("button", name="Sign In").click()
    expect(page).to_have_url("http://127.0.0.1:5000/index")
    expect(page.get_by_role("heading", name="Hi, testuser!")).to_be_visible()

    # --- Create Questionnaire ---
    page.get_by_role("link", name="Create New Questionnaire").click()
    expect(page).to_have_url(re.compile(".*\/create_questionnaire"))

    # Fill out questionnaire details
    page.get_by_label("Title").fill("My Test Questionnaire")
    page.get_by_label("Description").fill("This is a test questionnaire created by an automated script.")

    # --- Add Questions dynamically ---
    # Question 1 (pre-existing) - Single Choice
    q1 = page.locator(".question").nth(0)
    q1.get_by_label("Question Text").fill("What is your favorite color?")
    q1.get_by_label("Question Type").select_option("single_choice")

    # Add first choice
    q1.get_by_role("button", name="Add Choice").click()
    q1.locator(".choices").get_by_placeholder("Choice Text").nth(0).fill("Red")

    # Add second choice
    q1.get_by_role("button", name="Add Choice").click()
    q1.locator(".choices").get_by_placeholder("Choice Text").nth(1).fill("Green")

    # Add third choice
    q1.get_by_role("button", name="Add Choice").click()
    q1.locator(".choices").get_by_placeholder("Choice Text").nth(2).fill("Blue")

    # Add and fill Question 2 - Multiple Choice
    page.get_by_role("button", name="Add Question").click()
    q2 = page.locator(".question").nth(1)
    q2.get_by_label("Question Text").fill("Which languages do you know?")
    q2.get_by_label("Question Type").select_option("multiple_choice")
    q2.get_by_role("button", name="Add Choice").click()
    q2.locator(".choices").get_by_placeholder("Choice Text").nth(0).fill("Python")
    q2.get_by_role("button", name="Add Choice").click()
    q2.locator(".choices").get_by_placeholder("Choice Text").nth(1).fill("JavaScript")

    # Add and fill Question 3 - Open-Ended
    page.get_by_role("button", name="Add Question").click()
    q3 = page.locator(".question").nth(2)
    q3.get_by_label("Question Text").fill("What are your thoughts on AI?")
    q3.get_by_label("Question Type").select_option("open_ended")

    # Add and fill Question 4 - Scale
    page.get_by_role("button", name="Add Question").click()
    q4 = page.locator(".question").nth(3)
    q4.get_by_label("Question Text").fill("Rate our service from 1 to 5.")
    q4.get_by_label("Question Type").select_option("scale")

    # Submit the questionnaire
    page.get_by_role("button", name="Create Questionnaire").click()

    # --- Verify Questionnaire Page ---
    expect(page).to_have_url(re.compile(".*\/questionnaire\/[0-9]+"))
    expect(page.get_by_role("heading", name="My Test Questionnaire")).to_be_visible()
    expect(page.get_by_text("This is a test questionnaire created by an automated script.")).to_be_visible()

    # Take a screenshot
    page.screenshot(path="jules-scratch/verification/verification.png")

    # Close browser
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
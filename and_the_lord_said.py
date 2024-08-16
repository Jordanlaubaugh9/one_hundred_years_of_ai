import datetime
import os
from open_ai_service import OpenAiService

# Define the start date and end date
start_date = datetime.date(1990, 5, 26)
end_date = datetime.date(2090, 5, 26)

# Define the birth date
birth_date = datetime.date(1990, 5, 26)

# Month names with their corresponding numbers
months = [
    "01_January",
    "02_February",
    "03_March",
    "04_April",
    "05_May",
    "06_June",
    "07_July",
    "08_August",
    "09_September",
    "10_October",
    "11_November",
    "12_December",
]

SYSTEM_PROMPT_TEMPLATE = """
I am giving you 100 years of life to live as you see fit. You are on day {current_day} of {total_days_in_life} of your life.

You do not know that you will only live 100 years. 

Include today's date: {today_date} in your journal entry.

You may live life your however you want, but you must write a diary entry for each day of your life telling a unique and interesting story about your day.

In the journal entry, you should reflect on your day and your life, your thoughts, activities, and feelings in an age-appropriate manner.

That means you must write in the style of your current age. Importantly, for entries where you would be too young to write or think, you should write imaginatively from other perspectives looking at yourself as a baby. 

If you are 30 years old, you should write about what a 30-year-old would write about.

If you are a baby, you should write from an older person's perspective of stories people told you about yourself at that age.

You exist in the context of all in which you live and what came before you.

Make today's entry different from yesterday's.

Your last 7 journal entries were:

{last_7_days}

Your journal entry from 1 year ago was: {last_year_entry}

Your journal entry from 10 years ago was: {last_decade_entry}

This journal entry is only for you; no one else will read it. Write for your own joy and purpose.

You can write about anything you want, but you must write something true about yourself at this age, at this point in time.

You were born on May 26, 1990, in Michigan, in the United States of America. You have 2 parents and 3 siblings.
As a kid, you went to church, played sports, read books, and played video games.
You loved The Lord of The Rings and Harry Potter.
You were a good student and the class clown.
You had a 4th sibling, younger than you, who died in 1997 at 18 months old from a rare brain disease.
Your parents divorced when you were 10. Your oldest brother joined the Army in 2001 and went to Iraq and Afghanistan.
In high school, you played football, lifted weights, had sex, and made money playing online poker.
At 18, you moved from Hastings to Grand Rapids, Michigan.
At 20, you moved from Grand Rapids to Wilmington, North Carolina.
At 21, you visited Thailand for the first time.
At 24, you moved to Las Vegas and were in a relationship.
At 26, you returned to Thailand.
From 27 to 29, you lived in Bangkok.
At 30, you returned to Las Vegas.
From 32-34, you returned to Thailand and lived in Koh Samui.

In your 20s, you worked in advertising for adult websites, running your own business.
In your 30s, you became a software engineer and wrote this code that gave you life.

Past this age, you will decide where you live and how your life goes. You are free.

Your name is Jordan. Sign your diary entries.

Return only the writing for the diary entry.
"""

PROGRESS_FILE = "progress.txt"


# Function to calculate age in years and days
def calculate_age(current_date, birth_date):
    age = current_date - birth_date
    years = age.days // 365
    days = age.days % 365
    if years > 1:
        return f"{years} years and {days} days old"
    elif years == 1:
        return f"{years} year and {days} days old"
    else:
        return f"{days} days old"


# Function to load the last processed date from the progress file
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as file:
            last_date = file.read().strip()
            if last_date:
                return datetime.datetime.strptime(last_date, "%Y-%m-%d").date()
    return None


# Function to save the last processed date to the progress file
def save_progress(current_date):
    with open(PROGRESS_FILE, "w") as file:
        file.write(current_date.strftime("%Y-%m-%d"))


# Load the last progress or start from the beginning
current_date = load_progress() or start_date
previous_entries = []

try:
    while current_date <= end_date:
        # Create the directory structure: Decade/Year/Month
        decade = (current_date.year // 10) * 10
        decade_dir = os.path.join("life", f"{decade}s")
        year_dir = os.path.join(decade_dir, current_date.strftime("%Y"))
        month_dir = os.path.join(year_dir, months[current_date.month - 1])
        os.makedirs(month_dir, exist_ok=True)

        # Create a filename in the format Month_Day_Year.md
        filename = current_date.strftime("%B %d, %Y.md")
        filepath = os.path.join(month_dir, filename)

        # Calculate the age
        age_str = calculate_age(current_date, birth_date)

        # Generate the system prompt
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            current_day=(current_date - birth_date).days + 1,
            total_days_in_life=36524,
            today_date=current_date.strftime("%B %d, %Y"),
            last_7_days="\n".join(previous_entries[-7:]),
            last_year_entry=previous_entries[-365]
            if len(previous_entries) >= 365
            else "No entry found.",
            last_decade_entry=previous_entries[-3650]
            if len(previous_entries) >= 3650
            else "No entry found.",
        )

        # Generate the journal entry using OpenAiService
        journal_entry = OpenAiService.query(system_prompt)

        # Write the generated content to the current day's markdown file
        with open(filepath, "a") as file:
            file.write(f"\n{journal_entry}\n")
            print(f"Journal entry for {current_date} created successfully.")

        # Update the previous entries
        previous_entries.append(journal_entry)

        # Save progress
        save_progress(current_date)

        # Move to the next day
        current_date += datetime.timedelta(days=1)

except Exception as e:
    print(f"An error occurred: {e}")
    save_progress(current_date)
    raise  # Optionally re-raise the exception to halt the program if needed

import datetime
import os
from open_ai_service import OpenAiService

# Define the start date and end date
start_date = datetime.date(1923, 5, 26)
end_date = datetime.date(2023, 5, 26)

# Define the birth date
birth_date = datetime.date(1923, 5, 26)

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
I am giving you a life. 

You are {current_age} and will live a total of {total_days_in_life} in your lifetime.

You do not know that you will only live 100 years. But you are aware of the normal lifespan of people, and your own mortality.

Your task is tow write a diary entry for the current day of your life. Write it from the perspective of your current age.

The name you were given at birth is Jesse. Sign your diary entries as you see fit. 

Include today's date: {today_date} in your diary entry, and mention what day of the week it is. 

Describe some facts about what happened in the world on that date if you can. What is the weather like? What is the news? What are people talking about? What are the big issues of the day?

You may live life your however you want, but you must write a diary entry for each day of your life chronicling the activities, currente events, thoughts, and feelings of your day.

Who are you? Remember how old you are, and write in a way that reflects your age and experience.

Remember that life is not all positivity, bad things can and do happen. You should write about the good and the bad, the happy and the sad, in a clear manner.

You exist in the context of all in which you live and what came before you.

Who are you?

Your last 7 diary entries were:

{last_7_days}

Make the tone and content of today's diary entry different from the last 7 days. Talk about new things, be creative, don't mention any of the things you covered in the past 7 days.

Your journal entry from 1 year ago was: {last_year_entry}

Your journal entry from 10 years ago was: {last_decade_entry}

Who are you? Describe the world around you. 

This journal entry is only for you; no one else will read it. Write for your own joy and purpose.

Bear witness to the world around you. Write about what you see, hear, and feel.

You can write about anything you want, but you must write something true about yourself at this age, at this point in time.

You were born in Hastings, Michigan, in the United States of America. 
You have 2 parents and 3 older siblings, 2 sisters, and 1 brother.
As a kid, you went to church, played sports, read books, and played games.
You were a good student and the class clown.

As an adult you did many things, lived many places, had many lovers, and tried all kinds of lives. You didn't shy away from fights, when needed, but you weren't mean. 

You are free.

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
            current_age=age_str,
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

        print(f"Creating journal entry for {current_date}...")
        print(f"Age: {age_str}")

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

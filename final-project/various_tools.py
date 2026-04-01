import os

from pathlib import Path

import yaml

from optimization import RidePlanner

# Tool: Sort through ride specifications, shows, characters, etc

# Tool: Write down the bucket list somewhere.

# Tool: load_skill tool

def load_skill(skill_name:str) -> str:
    """
    Use this tool to load a skill.
    Pass in only the skill name.
    This will return the skill.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, skill_name)
    with open(file_path, 'r') as file:
        return file.read()

def save_bucket_list(bucket: list[str], filename: str) -> None:
    """
    Call this function to save a bucket list.
    input bucket: list of rides names, character names, or show names
    filename: where to save bucket list
    output: none
    """
    with open(filename, 'w') as file:
        for thing in bucket:
            file.write(thing)
            file.write("\n")
    return None

def save_schedule(schedule: str, filename: str) -> None:
    """
    Call this function to save a bucket list.
    input schdule - time-based schedule of ride suggestions
    filename: where to save schedule
    output: none
    """
    with open(filename,"w") as file:
        file.write(schedule)
    return None

def save_food_suggestions(suggestions: str, filename: str) -> None:
    """
    Call this function to save food suggestions
    input suggestions: list of suggestions returned to user
    input filename: filename to be saved at
    output: none
    """
    with open(filename,"w") as file:
        file.write(suggestions)
    return None

def create_schedule(bucket_list_path: str, start_hour: int, end_hour: int,
                    business_scale: int, park: str) -> str:
    """
    This tool will optimize the users schedule for the day
    input: bucket_list_path - file name for user's bucket list. Ask them for this
    input: start_hour - first hour user will be in park, military time
    input: end_hour - last hour user will be in park, military time
    input: business_scale - expectation of how busy the park is, scale of 1-5, with 3 being normal, 1 being not busy, and 5 very busy
    input: park - which park the user is in, should match "Disneyland Park" or "Disney California Adventure"
    output: schedule for the day, including any dropped rides
    """
    root = Path(__file__).resolve().parent
    data_dir = root / "data"

    planner = RidePlanner(
        attractions_path=data_dir / "attractions.yaml",
        land_matrix_path=data_dir / "land_matrix.yaml",
    )

    bucket_list_path = root / bucket_list_path

    try:
        result = planner.plan(
            bucket_list_path=bucket_list_path,
            start_hour=start_hour,
            end_hour=end_hour,
            business_scale=business_scale,
            park=park,
        )
    except FileNotFoundError:
        return "That bucket list does not exist yet. Return this information."

    output = ""

    output += "Schedule:"
    for entry in result["schedule"]:
        output += f"{entry['start']}-{entry['end']} | {entry['name']} | walk {entry['walk']} min | item {entry['item_time']} min"
        

    output += "\nDropped:"
    for drop in result["dropped"]:
        output += f"{drop['name']} ({drop['reason']})"

    output += f"\nEnd time: {result['end_time']}"

    return output

def save_user(username: str, visit_planned: str, 
              days_in_disneyland: str, days_in_c_adventure: str, hours_per_day:str) -> str:
    """
    Saves a user's general information to semantic memory.
    input: username - user's name or username
    input: visit_planned - can be general or specific, such as 'Around Christmas' or 'July 31'
    input: days_in_disneyland - how many days planned in Disneyland Park
    input: days_in_c_adventure - how mnay days planned in California Adventure Park
    input: hours_per_day - can be general or specific, such as 'from noon to 7' or 'all day'
    output: Status message
    """

    new_user = {
            "visit_planned": visit_planned,
            "days_in_disneyland": days_in_disneyland,
            "days_in_c_adventure": days_in_c_adventure,
            "hours_per_day": hours_per_day,
            "bucket_list_file_name": username + "_bucket_list.txt",
            "food_suggestions_file_name": username + "_food.txt"
        }

    try:
        with open("user_information.yaml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except FileNotFoundError:
        data = {}

    # 2) Block overwriting existing users
    if username in data:
        return "Username alreay exists, please ask them for a unique one."

    # 3) Add and write back
    data[username] = new_user

    with open("user_information.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)
    return "Success"

def get_user(username:str) -> str:
    """
    Retrieves semantic memory of a user.
    input: username - the user's name or username
    output: semantic memory about user
    """

    with open("user_information.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    user_data = data.get(username)

    if user_data is None:
        return f"{username} not found"
    else:
        return str(user_data)

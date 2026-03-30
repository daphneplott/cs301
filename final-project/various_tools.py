import os

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
        file.write(bucket)
    return None

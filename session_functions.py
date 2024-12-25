from global_settings import SESSION_FILE, STORAGE_PATH
import yaml
import os


def save_session(state):
    """
    Save the current application state to a YAML file.

    Args:
        state (dict): Dictionary containing the current application state to be saved.
    """
    state_to_save = {key: value for key, value in state.items()}
    with open(SESSION_FILE, "w") as file:
        yaml.dump(state_to_save, file)


def load_session(state):
    """
    Load a previously saved session state from a YAML file.

    Args:
        state (dict): Dictionary to store the loaded session state.

    Returns:
        bool: True if session was successfully loaded, False if file doesn't exist
              or there was an error loading the file.
    """
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as file:
            try:
                loaded_state = yaml.safe_load(file) or {}
                for key, value in loaded_state.items():
                    state[key] = value
                return True
            except yaml.YAMLError as e:
                return False
    return False


def delete_session(state):
    """
    Delete the current session file and clean up associated storage.

    This function:
    1. Removes the session file if it exists
    2. Deletes all files in the storage directory
    3. Clears the provided state dictionary

    Args:
        state (dict): Dictionary containing the current application state to be cleared.
    """
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    for filename in os.listdir(STORAGE_PATH):
        file_path = os.path.join(STORAGE_PATH, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.remove(file_path)
    for key in list(state.keys()):
        del state[key]

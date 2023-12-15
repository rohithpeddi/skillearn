import json
import os
import shutil
import time
from label_studio_sdk import Client
from tqdm import tqdm


def create_annotations_backup(project_name, project_id, backup_path, timestamp, api_url, API_KEY):
    # Initialize the Label Studio client with the project name
    client = Client(url=api_url, api_key=API_KEY)

    # Get annotations for the project
    project = client.get_project(project_id)
    annotations = project.export_tasks()

    # Generate a human-readable timestamp for the backup file name
    # Move the backup directory to its final location with the timestamped name
    final_backup_path = os.path.join(backup_path, f'{timestamp}/')
    os.makedirs(final_backup_path, exist_ok=True)
    final_backup_path = os.path.join(final_backup_path, project_name)
    final_backup_path = final_backup_path.replace('mp4', 'json')

    with open(final_backup_path, 'w') as backup_file:
        json.dump(annotations, backup_file)
    print(f"Backup created for project '{project_name}' at '{final_backup_path}'")

def backup_annotations_for_all_projects(backup_dir, api_url='http://localhost:8080/', API_KEY='d5e92d10e3fe2f7d117475758783be3058d5b21b'):
    # Initialize the Label Studio client
    client = Client(url=api_url, api_key=API_KEY)

    # Get all the project names
    projects = client.get_projects()
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")

    for project in tqdm(projects):
        project_id = project.id
        project_name = project.title
        create_annotations_backup(project_name, project_id, backup_dir, timestamp, api_url, API_KEY)

# Usage example
backup_dir = "./annotations_backup/"

backup_annotations_for_all_projects(backup_dir)

import argparse

from label_studio_sdk import Client


def create_project(args):
    # Set the API URL, project name, and XML file
    api_url = args.api_url
    # video_file_path = f'data/error_dataset/recordings/{project_name}_360p.mp4'
    API_KEY = args.api_auth_token

    # Create a Label Studio client with authentication
    ls = Client(url=api_url, api_key=API_KEY)
    projects = ls.get_projects()

    # Delete all projects
    print("Deleting all projects")
    for project in projects:
        ls.delete_project(project.id)

if __name__ == '__main__':
    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_url', type=str, default='http://localhost:8080/', help='URL of Label Studio API')
    parser.add_argument('--api_auth_token', type=str, default='d5e92d10e3fe2f7d117475758783be3058d5b21b',
                        help='Authorization token for Label Studio API')
    args = parser.parse_args()
    create_project(args)

import argparse

from label_studio_sdk import Client


def create_project(args):
    # Set the API URL, project name, and XML file
    api_url = args.api_url
    project_name = args.project_name
    label_config_file = args.label_config
    # video_file_path = f'data/error_dataset/recordings/{project_name}_360p.mp4'
    API_KEY = args.api_auth_token

    # Create a Label Studio client with authentication
    ls = Client(url=api_url, api_key=API_KEY)
    with open(label_config_file, 'r') as xml_file:
        xml_string = xml_file.read()

    projects = ls.get_projects()

    # Delete all projects
    # print("Deleting all projects")
    # for project in projects:
    #     ls.delete_project(project.id)
    # exit()

    # Check if the project name has been used previously
    project_already_there = False
    for project in projects:
        if project.title == f'{project_name}':
            print(f'{project_name} has been used previously for project ID {project.id}.')
            project_already_there = True
            break
    if not project_already_there:
        print(f'{project_name} has not been used previously.')
        # Create a project with the specified name and XML file
        project = ls.start_project(
                title=f'{project_name}',
                label_config=xml_string
        )

        # Print the project ID
        print(f'Project ID: {project.id}')
        # Not working - Video is loading but not the audio
        video_url = f'http://localhost/{project_name}'
        # project.import_tasks(
        #         [
        #             {'video_url': video_url},
        #         ]
        # )
        # Print the task ID
        # print(f'Task ID: {task.id}')
        # task = project.upload_file(video_file_path)
        # project.import_tasks(
        #     [
        #         {'video_url': 'file:///data/error_dataset/recordings/13_45_360p.mp4'}
        #     ]
        # )


if __name__ == '__main__':
    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_name', type=str, required=True, help='Name of the Label Studio project')
    parser.add_argument('--video_path', type=str, required=True, help='Path to video file to upload')
    parser.add_argument('--label_config', type=str, default=None, help='Path to Label Studio label config file')
    parser.add_argument('--api_url', type=str, default='http://localhost:8080/', help='URL of Label Studio API')
    parser.add_argument('--api_auth_token', type=str, default='d5e92d10e3fe2f7d117475758783be3058d5b21b',
                        help='Authorization token for Label Studio API')
    args = parser.parse_args()
    create_project(args)

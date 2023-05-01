import os

import requests
import argparse


def create_project(args):
    # Find the project ID for the given project name
    project_id = None
    response = requests.get(f'{args.api_url}/projects/', headers={'Authorization': f'Token {args.auth_token}'})
    print(response.json())
    if response.ok:
        if response.json()['count'] != 0:
            for project in response.json()['results']:
                if project['title'] == args.project_name:
                    project_id = project['id']
                    break

    # If project doesn't exist, create it
    if not project_id:
        payload = {
            'project': args.project_name,
            'LabelConfig': (open(args.label_config, 'rb'), 'application/json')
        }
        headers = {'Authorization': f'Token {args.auth_token}'}
        response = requests.post(f'{args.api_url}/projects/', files=payload, headers=headers)

        # Print the response
        # print(response.json())
        # response = requests.post(f'{args.api_url}/projects/', json={'name': args.project_name},
        #                          headers={'Authorization': f'Token {args.auth_token}'})
        if response.ok:
            project_id = response.json()['id']
            print(f'Created new Label Studio project "{args.project_name}" with ID {project_id}')

    # Upload video file to the project
    #     with open(args.video_path, 'rb') as f:
    #         print(f)
    #         response = requests.post(f'{args.api_url}/projects/{str(project_id)}', headers={
    #             'Authorization': f'Token {args.auth_token}',
    #             'Content-Disposition': f'attachment; filename="{os.path.basename(args.video_path)}"',
    #             'Content-Type': 'video/mp4',
    #             'Project': str(project_id),
    #             'LabelConfig': args.label_config or ''
    #         }, data=f)
    #     if response.ok:
    #         print(f'Uploaded {args.video_path} to project {args.project_name} with ID {project_id}')
    #     else:
    #         print(f'Failed to upload {args.video_path}: {response.content.decode()}')


if __name__ == '__main__':
    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_name', type=str, required=True, help='Name of the Label Studio project')
    parser.add_argument('--video_path', type=str, required=True, help='Path to video file to upload')
    parser.add_argument('--label_config', type=str, default=None, help='Path to Label Studio label config file')
    parser.add_argument('--api_url', type=str, default='http://localhost:8080/api', help='URL of Label Studio API')
    parser.add_argument('--auth_token', type=str, default='d5e92d10e3fe2f7d117475758783be3058d5b21b', help='Authorization token for Label Studio API')
    args = parser.parse_args()
    create_project(args)
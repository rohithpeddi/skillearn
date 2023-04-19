import os
import argparse
import requests

# Define command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--project_name', type=str, required=True, help='Name of the Label Studio project')
parser.add_argument('--video_path', type=str, required=True, help='Path to video file to upload')
parser.add_argument('--label_config', type=str, default=None, help='Path to Label Studio label config file')
parser.add_argument('--api_url', type=str, default='http://localhost:8080/api', help='URL of Label Studio API')
parser.add_argument('--auth_token', type=str, default=None, help='Authorization token for Label Studio API')
args = parser.parse_args()

# Find the project ID for the given project name
project_id = None
response = requests.get(f'{args.api_url}/projects/', headers={'Authorization': f'Token {args.auth_token}'})
if response.ok:
    for project in response.json():
        if project['name'] == args.project_name:
            project_id = project['id']
            break

# If project doesn't exist, create it
if not project_id:
    response = requests.post(f'{args.api_url}/projects/', json={'name': args.project_name},
                             headers={'Authorization': f'Token {args.auth_token}'})
    if response.ok:
        project_id = response.json()['id']
        print(f'Created new Label Studio project "{args.project_name}" with ID {project_id}')

# Upload video file to the project
with open(args.video_path, 'rb') as f:
    response = requests.post(f'{args.api_url}/data/upload', headers={
        'Authorization': f'Token {args.auth_token}',
        'Content-Disposition': f'attachment; filename="{os.path.basename(args.video_path)}"',
        'Content-Type': 'application/octet-stream',
        'Project': str(project_id),
        'LabelConfig': args.label_config or ''
    }, data=f)
if response.ok:
    print(f'Uploaded {args.video_path} to project {args.project_name} with ID {project_id}')
else:
    print(f'Failed to upload {args.video_path}: {response.content.decode()}')

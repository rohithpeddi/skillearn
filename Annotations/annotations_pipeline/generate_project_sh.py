import os
import sys



def generate_recipe_xml(steps: list, recording_id: str):
    xml_string = '<View>\n'
    xml_string += f'  <Header value="Labeling Recording ID {recording_id}"/>\n'
    xml_string += '  <Video name="video" value="$video_url" sync="audio"/>\n'
    xml_string += '  <View style="display:flex;align-items:start;gap:8px;flex-direction:column">\n'
    xml_string += '    <AudioPlus name="audio" value="$video_url" sync="video" speed="true"/>\n'
    xml_string += '    <View>\n'
    xml_string += '      <Filter toName="action" minlength="0" name="filter"/>\n'
    xml_string += '      <Labels name="action" toName="audio" choice="single" showInline="true">\n'
    xml_string += '        <Label value="Type Action." background="#000000"/>\n'
    for step in steps:
        xml_string += f"<Label value=\"S{step['step_number']}: {step['modified_description']}\"  background=\"#FF0000\"/>\n"
    xml_string += '      </Labels>\n'
    xml_string += '    </View>\n'
    xml_string += '  </View>\n'
    xml_string += '  <View visibleWhen="region-selected" whenLabelValue="Type Action.">\n'
    xml_string += '    <Header value="Provide Transcription"/>\n'
    xml_string += '    <TextArea name="transcription" toName="audio" rows="2" editable="true" perRegion="true" required="false"/>\n'
    xml_string += '  </View>\n'
    xml_string += '</View>'
    return xml_string


def save_xml(xml_string: str, file_name: str):
    with open(file_name, 'w') as file:
        file.write(xml_string)


def get_recipe_steps(recording_id):
    db_service = FirebaseService()
    fetched_recording_details = db_service.fetch_recording(recording_id)
    step_array = []
    for idx, step in enumerate(fetched_recording_details['steps']):
        if 'modified_description' not in step:
            description = step['description']
        else:
            description = step['modified_description']
        step_array.append({'step_number': idx, 'modified_description': description})
    # description = fetched_recording_details['description']
    # step_array = [{'step_number': i, 'modified_description': s['modified_description']}
    #               print(s) for i, s in enumerate(fetched_recording_details['steps'])]
    # print(step_array)
    return step_array


def create_bash_file_for_project_generation(recording_id, xml_file_path, video_save_path):
    project_name = f'{recording_id}_360p.mp4'
    video_path = f'{video_save_path}/{recording_id}_360p.mp4'
    label_config = f'{xml_file_path}/{recording_id}.xml'
    command = f'python create_project_sdk.py --project_name {project_name} --video_path {video_path} --label_config {label_config}'
    return command


if __name__ == '__main__':
    datacollection_path = "/home/sxa180157/Projects/error_dataset/actioncompetence"
    # os.environ["PYTHONPATH"] = f"{datacollection_path}:{os.environ.get('PYTHONPATH')}"
    sys.path.append(datacollection_path)

    from datacollection.user_app.backend.app.services.firebase_service import FirebaseService
    video_save_path = '/data/error_dataset/recordings'
    downloaded_files_recording_id = os.listdir(video_save_path)
    recipe_steps_dict = {}
    command = ""
    for recording_id in downloaded_files_recording_id:
        recording_id = recording_id.split('_')[0] + "_" + recording_id.split('_')[1]
        recipe_steps_dict[recording_id] = get_recipe_steps(recording_id)
        recipe_xml = generate_recipe_xml(recipe_steps_dict[recording_id], recording_id)
        folder = f'xml_files'
        if not os.path.exists(folder):
            os.makedirs(folder)
        save_xml(recipe_xml, f'{folder}/{recording_id}.xml')
        command += create_bash_file_for_project_generation(recording_id, folder, video_save_path) + "\n"

    with open("create_projects.sh", "w") as f:
        f.write(f"#!/bin/bash\n\n{command}")

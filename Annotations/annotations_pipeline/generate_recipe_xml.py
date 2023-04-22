
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
        xml_string += f"<Label value=\"{step}\"  background=\"#FF0000\"/>\n"
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


if __name__ == '__main__':
    recording_id = 'recording_id'
    recipe_xml = generate_recipe_xml(['step1', 'step2', 'step3'], recording_id)
    save_xml(recipe_xml, f'{recording_id}.xml')
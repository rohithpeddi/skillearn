import React, {useState} from 'react';
import axios from 'axios';
import './RecordingStepPreparation.css';
import RecordingStepPreparationMistakeList from "./RecordingStepPreparationMistakeListCard";
import API_BASE_URL from "../../config";

const RecordingStepPreparation = (props) => {
	
	const {recording, setRecording, mistakeTags, stepIndex} = props;
	
	const [selectedItems, setSelectedItems] = useState(new Set());
	const [mistakeText, setMistakeText] = useState('');
	const [stepDescription, setStepDescription] = useState('');
	
	const resetState = () => {
		setSelectedItems(new Set());
		setMistakeText('');
		setStepDescription('');
	};
	
	const handleCheckboxChange = (item, checked) => {
		const newSelectedItems = new Set(selectedItems);
		
		if (checked) {
			newSelectedItems.add(item);
		} else {
			newSelectedItems.delete(item);
		}
		
		setSelectedItems(newSelectedItems);
	};
	
	const handleMistakeTextChange = (e) => {
		setMistakeText(e.target.value);
	};
	
	const handleUpdateStepDescriptionChange = (e) => {
		setStepDescription(e.target.value);
	};
	
	const handleClick = async () => {
		if (selectedItems.size === 0) {
			alert('Please select at least one mistake tag.');
			return;
		} else if (mistakeText === '') {
			alert('Please enter a description of the mistake.');
			return;
		}
		if (stepDescription !== '') {
			recording.steps[stepIndex].modified_description = stepDescription;
		}
		
		if (!recording.steps[stepIndex].mistakes) {
			recording.steps[stepIndex].mistakes = [];
		}
		
		recording.steps[stepIndex].mistakes.push({
			tag: [...selectedItems.values()][0],
			description: mistakeText
		});
		
		let url = `${API_BASE_URL}/recordings/${recording.id}`;
		axios.post(url, recording)
			.then((recordingResponse) => {
				if (recordingResponse.data) {
					setRecording(recordingResponse.data);
					resetState();
				}
			})
			.catch((apiError) => {
				alert('Error during API call: ' + apiError)
				console.error('Error during API call:', apiError);
			});
	};
	
	const handleDeleteAllStepMistakes = async () => {
		recording.steps[stepIndex].mistakes = [];
		let url = `${API_BASE_URL}/recordings/${recording.id}`;
		axios.post(url, recording)
			.then((recordingResponse) => {
				if (recordingResponse.data) {
					setRecording(recordingResponse.data);
				}
			})
			.catch((apiError) => {
				alert('Error during API call: ' + apiError)
				console.error('Error during API call:', apiError);
			});
	};
	
	const handleDeleteStepMistake = async (mistakeIndex) => {
		recording.steps[stepIndex].mistakes.splice(mistakeIndex, 1);
		let url = `${API_BASE_URL}/recordings/${recording.id}`;
		axios.post(url, recording)
			.then((recordingResponse) => {
				if (recordingResponse.data) {
					setRecording(recordingResponse.data);
				}
			})
			.catch((apiError) => {
				alert('Error during API call: ' + apiError)
				console.error('Error during API call:', apiError);
			});
	};
	
	return (
		<div className="recStepPrepContainer">
			
			{
				recording.steps[stepIndex].mistakes && recording.steps[stepIndex].mistakes.length > 0 ? (
					<RecordingStepPreparationMistakeList recording={recording}
				                                     stepIndex={stepIndex}
				                                     handleDeleteStepMistake={handleDeleteStepMistake}
				                                     handleDeleteAllStepMistakes={handleDeleteAllStepMistakes} />
					
			
					): null
			}
			
			
			<div className="recStepPrepUpdateMistakeContainer">
				<div className="recStepPrepOriginalText">
					Original Description: {recording.steps[stepIndex].description}
				</div>
				
				<div className="recStepPrepMistakeTags">
					{mistakeTags.map((item) => (
						<div key={item} className="mistakeTagBox">
							<input
								className="mistakeTagCheckbox"
								type="checkbox"
								checked={selectedItems.has(item)}
								onChange={(e) => handleCheckboxChange(item, e.target.checked)}
							/>
							<label className="mistakeTagLabel">{item}</label>
						</div>
					))}
				</div>
				
				<div className="recStepPrepMistakeDescription">
					<div className="recStepPrepMistakeDescriptionText">
						Mistake Description:
					</div>
					<div className="recStepPrepInputText">
						<input className="inputTextField" type="text" value={mistakeText} onChange={handleMistakeTextChange} />
					</div>
				</div>
				
				<div className="recStepPrepUpdateStepDescription">
					<div className="recStepPrepUpdateStepDescriptionText">
						Updated Step Description:
					</div>
					<div className="recStepPrepInputText">
						<input className="inputTextField" type="text" value={stepDescription} onChange={handleUpdateStepDescriptionChange} />
					</div>
				</div>
				
				<button onClick={handleClick} className="recStepPrepUpdateButton">
					Update Mistakes
				</button>
			</div>
		
		</div>
	);
};

export default RecordingStepPreparation;

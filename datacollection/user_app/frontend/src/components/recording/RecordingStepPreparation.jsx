import React, {useEffect, useState} from 'react';
import axios from 'axios';
import './RecordingStepPreparation.css';

const RecordingStepPreparation = (props) => {
	
	const {recording, setRecording, mistakeTags, step, stepIndex} = props;
	
	const [preselectedItems, setPreselectedItems] = useState([]);
	
	useEffect( () => {
		if (step.mistakes && step.mistakes.length > 0) {
			const preselectedItems = step.mistakes.map((mistake) => mistake.tag);
			setPreselectedItems(preselectedItems);
		}
	}, [step]);
	
	const [selectedItems, setSelectedItems] = useState(new Set(preselectedItems));
	
	const [mistakeText, setMistakeText] = useState('');
	const [stepDescription, setStepDescription] = useState('');
	
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
		
		const payload = {
			selectedItems: Array.from(selectedItems),
		};
		
		try {
			const response = await axios.post('https://api.example.com/endpoint', payload);
			console.log(response.data);
		} catch (error) {
			console.error('Error during API call:', error);
		}
	};
	
	return (
		<div className="recStepPrepContainer">
			<div className="recStepPrepOriginalText">
				Original Description: {step.description}
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
	);
};

export default RecordingStepPreparation;

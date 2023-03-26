import React, { useState } from 'react';
import './RecordingStepPreparationMistakeList.css';

const RecordingStepPreparationMistakeList = ({ recording, stepIndex, handleDeleteAllStepMistakes, handleDeleteStepMistake }) => {
	const [deleteEnabled, setDeleteEnabled] = useState(false);
	
	const toggleDelete = () => {
		setDeleteEnabled(!deleteEnabled);
	};
	
	const handleDeleteAll = () => {
		handleDeleteAllStepMistakes();
	};
	
	const handleDeleteItem = (mistake) => {
		handleDeleteStepMistake(mistake);
	};
	
	return (
		<div className="recStepPrepMistakeListContainer">
			<div className="recStepPrepMistakeList">
				{recording.steps[stepIndex].mistakes.map((mistake, mistakeIndex) => (
					<div key={mistake.description} className="recStepPrepMistake">
						<div className="recStepPrepMistakeTag">
							{mistake.tag}
						</div>
						<div className="recStepPrepMistakeDescription">
							{mistake.description}
						</div>
						{deleteEnabled && (
							<button
								className="recStepPrepMistakeDelete"
								onClick={() => handleDeleteItem(mistakeIndex)}
							>
								Delete
							</button>
						)}
					</div>
				))}
			</div>
			<div className="recStepPrepMistakeListActions">
				<button onClick={toggleDelete}>
					{deleteEnabled ? 'Disable Delete' : 'Enable Delete'}
				</button>
				{deleteEnabled && (
					<button onClick={handleDeleteAll}>Delete All</button>
				)}
			</div>
		</div>
	);
};

export default RecordingStepPreparationMistakeList;

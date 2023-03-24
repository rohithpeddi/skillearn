import React, { useState } from "react";
import { Stepper, Step, StepLabel, Button } from "@mui/material";
import AppBar from "../atoms/AppBar";
import styles from "./Recording.css";
import RecordingSelection from "./RecordingSelection";

const Recording = (props) => {
	
	const {userData, environment, activities, setUserData, setActivities, setEnvironment} = props;
	
	const [activeStep, setActiveStep] = useState(0);
	const [recording, setRecording] = useState(false);
	
	const steps = ["Activity Selection", "Activity Preparation", "Activity Recording", "Activity Recording Review"];
	
	const handleNext = () => {
		setActiveStep((prevActiveStep) => prevActiveStep + 1);
	};
	
	const handleBack = () => {
		setActiveStep((prevActiveStep) => prevActiveStep - 1);
	};
	
	const getContent = (stepIndex) => {
		switch (stepIndex) {
			case 0:
				return ( <div>
					<RecordingSelection userData={userData}
				                                environment={environment}
				                                activities={activities}
				                                recording={recording}
				                                setUserData={setUserData}
				                                setEnvironment={setEnvironment}
				                                setActivities={setActivities}
                                                setRecording={setRecording}	/>
					</div>);
			case 1:
				return <div>Content for Step 2</div>;
			case 2:
				return <div>Content for Step 3</div>;
			case 3:
				return <div>Content for Step 4</div>;
			default:
				return <div>Unknown step</div>;
		}
	};
	
	return (
		
		<div className={styles.recordingContainer}>
			<div className={styles.recordingHeader}>
				<AppBar userData={userData} />
			</div>
			
			<div className={styles.recordingStepperContainer}>
				<Stepper activeStep={activeStep} alternativeLabel>
					{steps.map((label) => (
						<Step key={label}>
							<StepLabel>{label}</StepLabel>
						</Step>
					))}
				</Stepper>
				
				<div className={styles.recordingContent}>
					{
						getContent(activeStep)
					}
				</div>
				
				<div className={styles.recordingButtonContainer}>
					<Button
						disabled={activeStep === 0}
						onClick={handleBack}
						style={{ marginRight: "8px" }}
					>
						Back
					</Button>
					<Button
						variant="contained"
						color="primary"
						onClick={handleNext}
						disabled={activeStep === steps.length - 1}
					>
						{activeStep === steps.length - 1 ? "Finish" : "Next"}
					</Button>
				</div>
			</div>
		</div>
		
	);
};

export default Recording;
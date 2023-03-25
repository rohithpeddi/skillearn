import React, {useEffect, useState} from "react";
import { Stepper, Step, StepLabel, Button } from "@mui/material";
import AppBar from "../atoms/AppBar";
import styles from "./Recording.css";
import RecordingSelection from "./RecordingSelection";
import RecordingPreparation from "./RecordingPreparation";
import RecordingRecording from "./RecordingRecording";
import axios from "axios";

const Recording = (props) => {
	
	const {userData, environment, activities, setUserData, setActivities, setEnvironment} = props;
	
	const [activeStep, setActiveStep] = useState(0);
	const [recording, setRecording] = useState(false);
	
	const [mistakeTags, setMistakeTags] = useState([]);
	
	useEffect(() => {
		axios.get("http://localhost:5000/mistake_tags")
			.then((response) => {
				setMistakeTags(response.data);
				console.log(response.data);
			})
			.catch((error) => {
				console.log(error);
			});
	}, []);
	
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
				return ( <div>
							<RecordingPreparation userData={userData}
							                        environment={environment}
							                        activities={activities}
								                    recording={recording}
								                    setUserData={setUserData}
								                    setEnvironment={setEnvironment}
								                    setActivities={setActivities}
								                    setRecording={setRecording}
					                                mistakeTags={mistakeTags}	/>
						</div>);
			case 2:
				return ( <div>
					<RecordingRecording userData={userData}
					                      environment={environment}
					                      activities={activities}
					                      recording={recording}
					                      setUserData={setUserData}
					                      setEnvironment={setEnvironment}
					                      setActivities={setActivities}
					                      setRecording={setRecording}	/>
				</div>);
			case 3:
				return ( <div>
					<RecordingPreparation userData={userData}
					                      environment={environment}
					                      activities={activities}
					                      recording={recording}
					                      setUserData={setUserData}
					                      setEnvironment={setEnvironment}
					                      setActivities={setActivities}
					                      setRecording={setRecording}
					                      mistakeTags={mistakeTags}	/>
					</div>);
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
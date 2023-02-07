import Box from "@mui/material/Box";
import DataCollectionSelect from "./DataCollectionSelect";
import DataCollectionAccordion from "./DataCollectionAccordion";
import {useState} from "react";
import DataCollectionGrid from "./DataCollectionGrid";
import './DataCollection.css';

const DataCollection = () => {
    const activity = ["COFFEE", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", "r9", "r10"];
    const place = ["PL1", "PL2", "PL3", "PL4", "PL5", "PL6", "PL7"];
    const person = ["P1", "P2", "P3", "P4", "P5", "P6"];
    const recording_number = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    const activity_type = ["STANDARD", "ERROR"];
    const step_description = [' Complete description corresponding to step1 is here',
        'Complete description corresponding to step2 is here',
        'Complete description corresponding to step3 is here',
        'Complete description corresponding to step4 is here',
        'Complete description corresponding to step5 is here',
        'Complete description corresponding to step6 is here',
        'Complete description corresponding to step7 is here',
        'Complete description corresponding to step8 is here'];

    const [selectedActivity, setSelectedActivity] = useState("");
    const [selectedPlace, setSelectedPlace] = useState("");
    const [selectedPerson, setSelectedPerson] = useState("");
    const [selectedRecordingNumber, setSelectedRecordingNumber] = useState("");
    const [selectedActivityType, setSelectedActivityType] = useState("");
    const [inputIPAddress, setInputIPAddress] = useState("");

    const props = {
        selectedActivity,
        selectedPlace,
        selectedPerson,
        selectedRecordingNumber,
        selectedActivityType,
        inputIPAddress,
        setSelectedActivity,
        setSelectedPlace,
        setSelectedPerson,
        setSelectedRecordingNumber,
        setSelectedActivityType,
        setInputIPAddress,
        activity,
        place,
        person,
        recording_number,
        activity_type,
        step_description
    };


    return (
        <Box className="data_collection">
            <Box>
                <DataCollectionSelect {...props} />
            </Box>
            <Box>
                <DataCollectionAccordion selectedActivity={selectedActivity} step_description={step_description}
                                         selectedType={selectedActivityType}/>
            </Box>
            <Box>
                <DataCollectionGrid headerName={"STEP COMPLETION STATUS"}/>
                <DataCollectionGrid headerName={"UPLOAD QUEUE"}/>
            </Box>

        </Box>
    );
};

export default DataCollection;

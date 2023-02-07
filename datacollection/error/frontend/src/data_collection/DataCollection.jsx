import Box from "@mui/material/Box";
import DataCollectionSelect from "./DataCollectionSelect";
import DataCollectionAccordion from "./DataCollectionAccordion";
import {useEffect, useState} from "react";
import DataCollectionGrid from "./DataCollectionGrid";
import './DataCollection.css';

const DataCollection = () => {
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    const [selectedActivity, setSelectedActivity] = useState("");
    const [selectedPlace, setSelectedPlace] = useState("");
    const [selectedPerson, setSelectedPerson] = useState("");
    const [selectedRecordingNumber, setSelectedRecordingNumber] = useState("");
    const [selectedActivityType, setSelectedActivityType] = useState("");
    const [inputIPAddress, setInputIPAddress] = useState("");

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const response = await fetch('http://localhost:5000/info');
                const json = await response.json();
                setData(json);
            } catch (error) {
                setError(error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) {
        return <div>Loading...</div>;
    }
    else if (error) {
        return <div>Error: {error.message}</div>;
    }
    else {
        const activity = Object.keys(data.activities);
        const place = Object.keys(data.places);
        const person = Object.keys(data.persons);
        const recording_number = Object.keys(data.recording_numbers)
        const activity_type = ["STANDARD", "ERROR"];

        const step_description = [' Complete description corresponding to step1 is here',
            'Complete description corresponding to step2 is here',
            'Complete description corresponding to step3 is here',
            'Complete description corresponding to step4 is here',
            'Complete description corresponding to step5 is here',
            'Complete description corresponding to step6 is here',
            'Complete description corresponding to step7 is here',
            'Complete description corresponding to step8 is here'];

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
    }

};

export default DataCollection;
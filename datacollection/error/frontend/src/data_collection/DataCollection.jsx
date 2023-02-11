import Box from "@mui/material/Box";
import DataCollectionSelect from "./DataCollectionSelect";
import DataCollectionAccordion from "./DataCollectionAccordion";
import {useEffect, useState} from "react";
import DataCollectionGrid from "./DataCollectionGrid";
import './DataCollection.css';
import axios from "axios";
import _ from "lodash";
import * as React from "react";

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
    const [stepsCompleted, setStepsCompleted] = useState(['dummy S1']);

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

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get("http://localhost:5000/record/status", {
                    params: {
                        activity: selectedActivity,
                        place_id: selectedPlace,
                        person_id: selectedPerson,
                        recording_number: selectedRecordingNumber,
                        is_error: selectedActivityType === "ERROR",
                        device_ip: inputIPAddress
                    }
                });
                console.log(response);
                if (_.isNull(response.data.recording_status)) {
                    setStepsCompleted(['dummy S1']);
                } else {
                    setStepsCompleted(Object.keys(response.data.recording_status.steps));
                }

            } catch (error) {
                console.log(error);
            }

        };
        if (selectedActivity && selectedPlace && selectedPerson && selectedRecordingNumber && selectedActivityType && inputIPAddress) {
            fetchData();
        }
    }, [selectedActivity, selectedPlace, selectedPerson, selectedRecordingNumber, selectedActivityType, inputIPAddress]);

    if (loading) {
        return <div>Loading...</div>;
    } else if (error) {
        return <div>Error: {error.message}</div>;
    } else {
        const activity = data.activities;
        const place = data.places;
        const person = data.persons;
        const recording_number = data.recording_numbers;
        const activity_type = ["STANDARD", "ERROR"];
        let step_description_mapping;
        if (data && selectedActivity) {
            step_description_mapping = data.activities[selectedActivity];
        } else {
            step_description_mapping = {
                "s1": "just a dummy step description. Please select an activity"
            }
        }

        const props = {
            selectedActivity,
            selectedPlace,
            selectedPerson,
            selectedRecordingNumber,
            selectedActivityType,
            inputIPAddress,
            stepsCompleted,
            setSelectedActivity,
            setSelectedPlace,
            setSelectedPerson,
            setSelectedRecordingNumber,
            setSelectedActivityType,
            setInputIPAddress,
            setStepsCompleted,
            activity,
            place,
            person,
            recording_number,
            activity_type,
            step_description_mapping
        };

        return (<Box className="data_collection">
            <Box>
                <DataCollectionSelect {...props} />
            </Box>
            <Box>
                <DataCollectionAccordion {...props}/>
            </Box>
            <Box>
                <Box>
                    <DataCollectionGrid headerName={"STEP COMPLETION STATUS"} stepsCompleted={stepsCompleted}/>
                </Box>
            </Box>

        </Box>);
    }

};

export default DataCollection;
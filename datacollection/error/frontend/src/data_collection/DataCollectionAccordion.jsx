import {Accordion, AccordionDetails, AccordionSummary, Button, Typography} from "@mui/material";
import Box from "@mui/material/Box";
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import './DataCollectionAccordion.css';
import axios from "axios";
import {useState} from "react";



const handleClick = async (endpoint, params, setSubprocessId) => {
    try {
        const response = await axios.post(endpoint, null,{params});
        console.log(response);
        if (endpoint==="http://localhost:5000/record/activity/start") {
            setSubprocessId(response.data["subprocess_id"]);
        }
    } catch (e) {
        console.log(endpoint + e);
    } finally {
        console.log(endpoint + " loading is done")
    }
};

const displayAccordionPanels = (props) => {
    return Object.entries(props.step_description_mapping).map(([key, value]) => (<Accordion key={key}>
        <AccordionSummary expandIcon={<ExpandMoreIcon/>}>
            <Box className="data_collection_accordion_summary">
                <Typography variant="h6">{key}</Typography>
                <Typography variant="h6" marginLeft="5rem">{value}</Typography>
            </Box>
        </AccordionSummary>
        <AccordionDetails>
            <Box>
                <Box className="data_collection_accordion_details_child_box1">
                    <Button variant="outlined" onClick= {() => handleClick("http://localhost:5000/record/step/start", {
                        activity: props.selectedActivity,
                        place_id: props.selectedPlace,
                        person_id: props.selectedPerson,
                        recording_number: props.selectedRecordingNumber,
                        step_id: key,
                        is_error: props.selectedActivityType==="ERROR"
                    })}>START</Button>
                    <Button variant="outlined" onClick={() => handleClick("http://localhost:5000/record/step/stop", {
                        activity: props.selectedActivity,
                        place_id: props.selectedPlace,
                        person_id: props.selectedPerson,
                        recording_number: props.selectedRecordingNumber,
                        step_id: key,
                        is_error: props.selectedActivityType==="ERROR"
                    })}>STOP</Button>
                    <Button variant="outlined" onClick={() => handleClick("http://localhost:5000/delete", {
                        activity: props.selectedActivity,
                        place_id: props.selectedPlace,
                        person_id: props.selectedPerson,
                        recording_number: props.selectedRecordingNumber,
                        step_id: key,
                        is_error: props.selectedActivityType==="ERROR"
                    })}>DELETE</Button>
                </Box>
                {props.selectedActivityType === "ERROR" && (<Box className="data_collection_accordion_details_child_box2">
                    <Typography variant="h6">ERROR TAGS</Typography>
                    <Box className="data_collection_accordion_details_child_box2_btn">
                        <Button variant="outlined">T1</Button>
                        <Button variant="outlined">T2</Button>
                        <Button variant="outlined">T3</Button>
                        <Button variant="outlined">T4</Button>
                        <Button variant="outlined">T5</Button>
                        <Button variant="outlined">T6</Button>
                        <Button variant="outlined">T7</Button>
                        <Button variant="outlined">T8</Button>
                    </Box>
                </Box>)}
            </Box>

        </AccordionDetails>
    </Accordion>))
}

const DataCollectionAccordion = (props) => {
    const [subprocessId, setSubprocessId] = useState(null);
    return (<Box className="data_collection_accordion">
        <Box className="data_collection_accordion_heading_btn">
            <Typography variant="h2" align="center"> {props.selectedActivity}</Typography>
            <Box className="data_collection_accordion_heading_all_btn">
                <Button variant="outlined" onClick={() => handleClick("http://localhost:5000/record/activity/start", {
                    activity: props.selectedActivity,
                    place_id: props.selectedPlace,
                    person_id: props.selectedPerson,
                    recording_number: props.selectedRecordingNumber,
                    is_error: props.is_error==="ERROR",
                    device_ip: props.device_ip
                }, setSubprocessId)}>START</Button>
                <Button variant="outlined" onClick={() => handleClick("http://localhost:5000/record/activity/stop", {
                    subprocess_id: subprocessId
                })}>STOP</Button>
            </Box>
        </Box>
        <Box className="data_collection_accordion_panels">
            {displayAccordionPanels(props)}
        </Box>
    </Box>)

}

export default DataCollectionAccordion;
import React from "react";
import {FormControl, Select, TextField, Typography} from "@mui/material";
import MenuItem from "@mui/material/MenuItem";
import Box from "@mui/material/Box";
import './DataCollectionSelect.css';

function convert(arr) {
    return arr.map((element) => {
        return {value: element, label: element}
    });
}

function BasicSelect({arr, setSelected, heading_title}) {

    const handleChange = (event) => {
        setSelected(event.target.value);
    };

    const convertedToKeyValueArray = convert(arr)
    const menuItems = convertedToKeyValueArray.map((item, index) => (
        <MenuItem key={index} value={item.value}>{item.label}</MenuItem>));

    return (<Box className="data_collection_select_child_panel">
        <FormControl fullWidth>
            <Select id="demo-simple-select" value={heading_title} onChange={handleChange}>
                {menuItems}
            </Select>
        </FormControl>
    </Box>);
}

function BasicTextField({setInputIPAddress}) {

    const handleChange = (event) => {
        setInputIPAddress(event.target.value);
    };
    return (
        <TextField id="outlined-basic" variant="outlined" onChange={handleChange}/>
    );
}

const DataCollectionSelect = (props) => {

    return (<Box className="data_collection_select_parent_box">
        <Box className="data_collection_select_child_box">
            <Typography variant="h6" align="left">ACTIVITY</Typography>
            <BasicSelect arr={props.activity} setSelected={props.setSelectedActivity}
                         heading_title={props.selectedActivity}/>
        </Box>
        <Box className="data_collection_select_child_box">
            <Typography variant="h6" align="left">PLACE</Typography>
            <BasicSelect arr={props.place} setSelected={props.setSelectedPlace}
                         heading_title={props.selectedPlace}/>
        </Box>
        <Box className="data_collection_select_child_box">
            <Typography variant="h6" align="left">PERSON</Typography>
            <BasicSelect arr={props.person} setSelected={props.setSelectedPerson}
                         heading_title={props.selectedPerson}/>
        </Box>
        <Box className="data_collection_select_child_box">
            <Typography variant="h6" align="left">RECORDING NUMBER</Typography>
            <BasicSelect arr={props.recording_number} setSelected={props.setSelectedRecordingNumber}
                         heading_title={props.selectedRecordingNumber}/>
        </Box>
        <Box className="data_collection_select_child_box">
            <Typography variant="h6" align="left">TYPE</Typography>
            <BasicSelect arr={props.activity_type} setSelected={props.setSelectedActivityType}
                         heading_title={props.selectedActivityType}/>
        </Box>
        <Box className="data_collection_select_child_box">
            <Typography variant="h6" align="left">IP ADDRESS</Typography>
            <BasicTextField setInputIPAddress={props.setInputIPAddress}/>
        </Box>

    </Box>);

}

export default DataCollectionSelect;
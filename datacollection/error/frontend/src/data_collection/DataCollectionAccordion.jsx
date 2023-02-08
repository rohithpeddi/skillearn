import {Accordion, AccordionDetails, AccordionSummary, Button, Typography} from "@mui/material";
import Box from "@mui/material/Box";
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import './DataCollectionAccordion.css';

const displayAccordionPanels = ({selectedType, step_description_mapping}) => {
    return Object.entries(step_description_mapping).map(([key, value]) => (<Accordion key={key}>
        <AccordionSummary expandIcon={<ExpandMoreIcon/>}>
            <Box className="data_collection_accordion_summary">
                <Typography variant="h6">{key}</Typography>
                <Typography variant="h6" marginLeft="5rem">{value}</Typography>
            </Box>
        </AccordionSummary>
        <AccordionDetails>
            <Box>
                <Box className="data_collection_accordion_details_child_box1">
                    <Button variant="outlined">START</Button>
                    <Button variant="outlined">STOP</Button>
                    <Button variant="outlined">DELETE</Button>
                </Box>
                {selectedType === "ERROR" && (<Box className="data_collection_accordion_details_child_box2">
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

const DataCollectionAccordion = ({selectedActivity, step_description_mapping, selectedType}) => {

    return (<Box className="data_collection_accordion">
        <Box className="data_collection_accordion_heading_btn">
            <Typography variant="h2" align="center"> {selectedActivity}</Typography>
            <Box className="data_collection_accordion_heading_all_btn">
                <Button variant="outlined">START</Button>
                <Button variant="outlined">STOP</Button>
            </Box>
        </Box>
        <Box className="data_collection_accordion_panels">
            {displayAccordionPanels({selectedType, step_description_mapping})}
        </Box>
    </Box>)

}

export default DataCollectionAccordion;
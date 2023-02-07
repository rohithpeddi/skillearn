import {Accordion, AccordionDetails, AccordionSummary, Button, Typography} from "@mui/material";
import Box from "@mui/material/Box";
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import './DataCollectionAccordion.css';

const displayAccordionPanels = ({step_description}) => {
    return step_description.map((heading_element, index) => (<Accordion key={index}>
        <AccordionSummary expandIcon={<ExpandMoreIcon/>}>
            <Box className="horizontal_align">
                <Typography variant="h6">{"STEP - " + (index + 1) + " "}</Typography>
                <Typography variant="h6" marginLeft="5rem">{heading_element}</Typography>
            </Box>
        </AccordionSummary>
        <AccordionDetails>
            <Box className="horizontal_align">
                <Button variant="outlined">START</Button>
                <Button variant="outlined">STOP</Button>
                <Button variant="outlined">DELETE</Button>
            </Box>
        </AccordionDetails>
    </Accordion>))
}

const DataCollectionAccordion = ({step_description}) => {

    return (<Box className="stepsBox">
        {displayAccordionPanels({step_description})}
    </Box>)

}

export default DataCollectionAccordion;
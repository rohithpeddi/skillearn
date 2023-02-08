import Box from "@mui/material/Box";
import {Grid, Paper, styled, Typography} from "@mui/material";
import {green} from "@mui/material/colors";
import './DataCollectionGrid.css';
import * as React from 'react';

const Item = styled(Paper)(({theme}) => ({
    backgroundColor: green, textAlign: 'center', color: theme.palette.text.secondary,
}));

const generateDiv = ({stepsCompleted}) => {
    //replace this with onclick upload button - use useState for setting up response
    return stepsCompleted.map((elem, index) => {
        return (<Grid item xs={4} alignContent="center" key={index}>
            <Item>{stepsCompleted[stepsCompleted.length - index - 1]}</Item>
        </Grid>);
    });
}

const DataCollectionGrid = ({headerName, stepsCompleted}) => {
    return (
        <Box className="data_collection_grid">
            <Typography variant="h6" align="center" borderBottom="2px solid"> {headerName}</Typography>
            <Grid container spacing={2} alignItems="center" justifyContent="center" columns={5}>
                {generateDiv({stepsCompleted})}
            </Grid>
        </Box>
    )

}
export default DataCollectionGrid;
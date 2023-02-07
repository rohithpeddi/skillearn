import Box from "@mui/material/Box";
import {Grid, Paper, styled, Typography} from "@mui/material";
import {green} from "@mui/material/colors";
import './DataCollectionGrid.css';
import * as React from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';

function DenseTable() {
    const res = ['Data 1', 'Data 2', 'Data 3', 'Data 4', 'Data 5', 'Data 6', 'Data 7', 'Data 8', 'Data 9'];

    return res.map((elem, index) => {
        return (
            <TableBody>
                <TableRow key={index}>
                    <TableCell align="center">{elem}</TableCell>
                    <TableCell align="center">Uploading</TableCell>
                </TableRow>
            </TableBody>

        );
    });
}

const Item = styled(Paper)(({theme}) => ({
    backgroundColor: green,
    textAlign: 'center',
    color: theme.palette.text.secondary,
}));

const generateDiv = () => {
    //replace this with onclick upload button - use useState for setting up response
    const res = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'S11', 'S12', 'S13', 'S14', 'S15', 'S16', 'S17', 'S18', 'S19', 'S20', 'S21', 'S22', 'S23', 'S24', 'S25', 'S26', 'S27', 'S28'];
    return res.map((elem, index) => {
        return (<Grid item xs={4} alignContent="center">
            <Item>{res[res.length - index - 1]}</Item>
        </Grid>);
    });
}

const DataCollectionGrid = ({headerName}) => {

    if (headerName === "STEP COMPLETION STATUS") {
        return (
            <Box className="data_collection_grid">
                <Typography variant="h6" align="center" borderBottom="2px solid"> {headerName}</Typography>
                <Grid container spacing={2} alignItems="center" justifyContent="center" columns={5}>
                    {generateDiv()}
                </Grid>
            </Box>
        )
    } else {
        return (
            <Box className="data_collection_grid">
                <Typography variant="h6" align="center" borderBottom="2px solid"> {headerName}</Typography>
                <TableContainer component={Paper}>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell align="center">DATA TYPE</TableCell>
                                <TableCell align="center">STATUS</TableCell>
                            </TableRow>
                        </TableHead>
                        {DenseTable()}
                    </Table>
                </TableContainer>
            </Box>
        )
    }
}
export default DataCollectionGrid;
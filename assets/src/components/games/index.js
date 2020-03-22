import React from 'react';
import Grid from "@material-ui/core/Grid/Grid";
import TextField from "@material-ui/core/TextField/TextField";
import Input from "@material-ui/core/Input/Input";
import Button from "@material-ui/core/Button/Button";
import {makeStyles} from "@material-ui/core";
import Typography from '@material-ui/core/Typography';
import logo from "images/logo512.png";

const useStyles = makeStyles(() => ({
    nameInput: {
        backgroundColor: 'white'
    }
}));


export default function Games() {
    const [gameName, setGameName] = React.useState('');
    const inputClasses = useStyles();

    const handleSubmit = () => {
        alert('join/create game')
    };

    return (
        <Grid
            container
            direction="column"
            justify="center"
            alignItems="center"
            spacing={8}
        >
            <Grid item>
                <Typography>Find a game!</Typography>
            </Grid>
            <Grid item>
                <img src={logo} className="App-logo" alt="logo" />
            </Grid>
            <Grid item>
                <Grid
                    container
                    direction="row"
                    justify="center"
                    alignItems="center"
                    spacing={4}
                >
                    <Grid item>
                        <TextField
                            id="username-text-field"
                            className={inputClasses.nameInput}
                            required
                            label='Game name?'
                            variant='filled'
                            onChange={(event) => setGameName(event.target.value)}
                        >
                            <Input
                                value={gameName}
                            />
                        </TextField>
                    </Grid>
                    <Grid item>
                        <Button
                            variant='contained'
                            onClick={handleSubmit}
                        >Submit</Button>
                    </Grid>
                </Grid>
            </Grid>
        </Grid>
    )
}
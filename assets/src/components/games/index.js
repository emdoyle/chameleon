import React from 'react';
import axios from "axios";
import { useHistory } from 'react-router-dom';
import Grid from "@material-ui/core/Grid/Grid";
import TextField from "@material-ui/core/TextField/TextField";
import Input from "@material-ui/core/Input/Input";
import Button from "@material-ui/core/Button/Button";
import {makeStyles} from "@material-ui/core";
import Typography from '@material-ui/core/Typography';
import logo from "../../images/logo512.png";

const useStyles = makeStyles(() => ({
    nameInput: {
        backgroundColor: 'white'
    }
}));


export default function Games() {
    const history = useHistory();
    const [gameName, setGameName] = React.useState('');
    const inputClasses = useStyles();
    React.useEffect(() => {
        axios.get('/api/v1/session').then(response => {
            if (response.data.has_session && response.data.has_game) {
                history.push('/chameleon')
            }
        }).catch(error => console.log(error))
    }, []);
    const handleSubmit = () => {
        axios.post('/api/v1/games', {
            gameName
        }).then(() => history.push('/chameleon')).catch(error => console.log(error))
    };
    const handleJoin = () => {
        axios.get('api/v1/games', {
            params: {
                gameName
            }
        }).then(() => history.push('/chameleon')).catch(error => console.log(error))
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
                            onClick={handleJoin}
                        >Join</Button>
                    </Grid>
                    <Grid item>
                        <Button
                            variant='contained'
                            onClick={handleSubmit}
                        >Create</Button>
                    </Grid>
                </Grid>
            </Grid>
        </Grid>
    )
}
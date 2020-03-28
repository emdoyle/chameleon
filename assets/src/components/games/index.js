import React from 'react';
import axios from "axios";
import { useHistory } from 'react-router-dom';
import Grid from "@material-ui/core/Grid/Grid";
import {makeStyles} from "@material-ui/core";
import TextInput from "../utils/TextInput";
import logo from "../../images/logo512.png";

const useStyles = makeStyles(() => ({
    gameInput: {
        padding: '1vh 1vh 1vh 1vh',
        border: '2px solid #000',
        borderRadius: '10px',
        backgroundColor: 'white',
    }
}));


export default function Games() {
    const history = useHistory();
    const [gameName, setGameName] = React.useState('');
    const styleClasses = useStyles();
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
        >
            <Grid item>
                <img src={logo} className="App-logo" alt="logo" />
            </Grid>
            <Grid item>
                <div className={styleClasses.gameInput}>
                    <TextInput
                        id="username-text-field"
                        label="Game name?"
                        onChange={(event) => setGameName(event.target.value)}
                        value={gameName}
                        onSubmit={handleSubmit}
                        buttonText="Create"
                        altButton
                        onAltSubmit={handleJoin}
                        altButtonText="Join"
                    />
                </div>
            </Grid>
        </Grid>
    )
}
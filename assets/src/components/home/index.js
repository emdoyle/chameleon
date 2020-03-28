import React from 'react';
import { useHistory } from 'react-router-dom';
import axios from 'axios';
import TextField from '@material-ui/core/TextField';
import Input from '@material-ui/core/Input';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import { makeStyles } from '@material-ui/core/styles';
import logo from '../../images/logo512.png';


const useStyles = makeStyles(() => ({
    nameInput: {
        backgroundColor: 'white'
    }
}));

export default function HomePage() {
    const history = useHistory();
    React.useEffect(() => {
        axios.get('/api/v1/session').then(response => {
            if (response.data.has_session && response.data.has_game) {
                history.push('/chameleon')
            } else if (response.data.has_session){
                history.push("/games");
            }
        }).catch(error => console.log(error))
    }, []);
    const [username, setUsername] = React.useState('');
    const inputClasses = useStyles();

    const handleSubmit = () => {
        axios.post('/api/v1/user', {
            username
        }).then(() => {
            history.push("/games");
        }).catch(error => {
            console.log(error);
        })
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
                            label='What is your name?'
                            variant='filled'
                            onChange={(event) => setUsername(event.target.value)}
                        >
                            <Input
                                value={username}
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
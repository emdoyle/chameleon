import React from 'react';
import { useHistory } from 'react-router-dom';
import axios from 'axios';
import Grid from '@material-ui/core/Grid';
import { makeStyles } from '@material-ui/core/styles';
import TextInput from "../utils/TextInput";
import logo from '../../images/logo512.png';


const useStyles = makeStyles(() => ({
    nameInput: {
        padding: '1vh 1vh 1vh 1vh',
        border: '2px solid #000',
        borderRadius: '10px',
        backgroundColor: 'white',
    }
}));

export default function HomePage() {
    const history = useHistory();
    const styleClasses = useStyles();
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
        >
            <Grid item>
                <img src={logo} className="App-logo" alt="logo" />
            </Grid>
            <Grid item>
                <div className={styleClasses.nameInput}>
                    <TextInput
                        value={username}
                        onChange={(event) => setUsername(event.target.value)}
                        onSubmit={handleSubmit}
                        label="What is your name?"
                    />
                </div>
            </Grid>
        </Grid>
    )
}
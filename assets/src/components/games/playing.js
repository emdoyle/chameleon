import React from 'react';
import axios from 'axios';
import { useHistory } from 'react-router-dom';
import Grid from '@material-ui/core/Grid';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TableContainer from '@material-ui/core/TableContainer';
import Paper from '@material-ui/core/Paper';
import Input from "@material-ui/core/Input/Input";
import TextField from "@material-ui/core/TextField/TextField";
import Button from "@material-ui/core/Button/Button";
import {makeStyles} from "@material-ui/core";

const useStyles = makeStyles(() => ({
    clueInput: {
        backgroundColor: 'white'
    }
}));


export default function PlayingChameleon() {
    const history = useHistory();
    const inputClasses = useStyles();
    const [userId, setUserId] = React.useState('');
    const [gameId, setGameId] = React.useState('');
    const [yourClue, setYourClue] = React.useState('');
    const [otherPlayers, setOtherPlayers] = React.useState([
        {name: 'Evan', id: '1'},
        {name: 'Isik', id: '2'}
    ]);
    const [guesses, setGuesses] = React.useState({
        '1': 'evans guess',
        '2': 'isiks guess'
    });
    React.useEffect(() => {
        axios.get('/api/v1/user').then(response => {
            if (response.data.user_id && response.data.game_id) {
                setUserId(response.data.user_id);
                setGameId(response.data.game_id);
                // also should make websocket connection
            } else {
                history.push('/')
            }
        }).catch(error => console.log(error))
    }, []);
    const submitYourClue = () => {
        axios.post('api/v1/clues', {
            userId,
            clue: yourClue
        }).then(response => {
            console.log(response.data)
        }).catch(error => console.log(error))
    };
    return (
        <Grid
            container
            direction="column"
            justify="space-between"
            alignItems="stretch"
        >
            <Grid item>
                <TableContainer component={Paper}>
                    <Table>
                        <TableHead>
                            <TableCell>User</TableCell>
                            <TableCell>Clue given</TableCell>
                        </TableHead>
                        <TableBody>
                            {otherPlayers.map(player => (
                                <TableRow key={player.name}>
                                    <TableCell>{player.name}</TableCell>
                                    <TableCell>{guesses[player.id] || '...'}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Grid>
            <Grid item>
                <Grid
                    container
                    direction="row"
                    justify="center"
                    alignItems="baseline"
                >
                    <Grid item>
                        <TextField
                            id="clue-text-field"
                            className={inputClasses.clueInput}
                            required
                            label='Give a clue!'
                            variant='filled'
                            onChange={(event) => setYourClue(event.target.value)}
                        >
                            <Input
                                value={yourClue}
                            />
                        </TextField>
                    </Grid>
                    <Grid item>
                        <Button
                            variant='contained'
                            onClick={submitYourClue}
                        >Submit</Button>
                    </Grid>
                </Grid>
            </Grid>
        </Grid>
    )
}
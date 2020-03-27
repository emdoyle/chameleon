import React from 'react';
import axios from 'axios';
import { useHistory } from 'react-router-dom';
import Grid from '@material-ui/core/Grid';
import { makeStyles } from "@material-ui/core/styles";
import ReadyInput from "./ReadyInput";
import ClueInput from "./ClueInput";
import PlayersTable from "./PlayersTable";

const useStyles = makeStyles(() => ({
    userTable: {
        minHeight: '65vh',
        minWidth: '75vw',
    },
    footer: {
        minHeight: '15vh',
        minWidth: '100vw',
        backgroundColor: 'white'
    },
}));


const websocketURL = new URL('/websocket', window.location.href);
websocketURL.protocol = websocketURL.protocol.replace('http', 'ws');


export default function PlayingChameleon() {
    const history = useHistory();
    const styleClasses = useStyles();
    const [websocket, setWebsocket] = React.useState(null);
    const [yourClue, setYourClue] = React.useState('');
    const [ready, setReady] = React.useState(false);
    const [phase, setPhase] = React.useState('');
    const [players, setPlayers] = React.useState([]);
    const [clues, setClues] = React.useState({});
    React.useEffect(() => {
        axios.get('/api/v1/session').then(response => {
            if (response.data.has_session && response.data.has_game) {
                console.log('running effect');
                const ws = new WebSocket(websocketURL.href);
                ws.onopen = () => ws.send(JSON.stringify({
                    'kind': 'players'
                }));
                ws.onmessage = event => {
                    const data = JSON.parse(event.data);
                    setPlayers(data.players || []);
                    setPhase(data.round.phase);
                };
                ws.onclose = () => console.log("Figure out how to reconnect");
                setWebsocket(ws)
            } else {
                history.push('/')
            }
        }).catch(error => console.log(error));

        return () => {
            if (websocket) {
                websocket.close()
            }
        }
    }, []);
    const submitYourClue = () => {
        if (websocket) {
            websocket.send(JSON.stringify({'data': 'hello'}))
        }
    };

    // dictionary or other structured data?
    const getPrimaryInput = () => {
        if (!phase) {
            return <React.Fragment />
        }
        if (phase === 'set_up') {
            return (
                <ReadyInput
                    value={ready}
                    onChange={(event) => {
                        setReady(event.target.checked);
                        websocket.send(JSON.stringify({
                            'kind': 'ready',
                            'ready': event.target.checked
                        }))
                    }}
                />
            )
        }
        if (phase === 'clues') {
            return (
                <ClueInput
                    value={yourClue}
                    onChange={(event) => setYourClue(event.target.value)}
                    onSubmit={submitYourClue}
                />
            )
        }
    };

    return (
        <Grid
            container
            direction="column"
            justify="space-between"
            alignItems="center"
            spacing={4}
        >
            <div className={styleClasses.userTable}>
                <Grid item>
                    <PlayersTable
                        players={players}
                        clues={clues}
                    />
                </Grid>
            </div>
            <div className={styleClasses.footer}>
                <Grid item>
                    {getPrimaryInput()}
                </Grid>
            </div>
        </Grid>
    )
}
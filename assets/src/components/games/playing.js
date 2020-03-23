import React from 'react';
import axios from 'axios';
import { useHistory } from 'react-router-dom';
import Grid from '@material-ui/core/Grid';
import { makeStyles } from "@material-ui/core/styles";
import ClueInput from "components/games/ClueInput";
import PlayersTable from "components/games/PlayersTable";

const useStyles = makeStyles(() => ({
    mainContent: {
        marginLeft: '2vw',
        marginRight: '2vw',
        minWidth: '75vw',
    },
    userTable: {
        minHeight: '65vh'
    }
}));


const websocketURL = new URL('/websocket', window.location.href);
websocketURL.protocol = websocketURL.protocol.replace('http', 'ws');


export default function PlayingChameleon() {
    const history = useHistory();
    const styleClasses = useStyles();
    const [websocket, setWebsocket] = React.useState(null);
    const [userId, setUserId] = React.useState('');
    const [gameId, setGameId] = React.useState('');
    const [yourClue, setYourClue] = React.useState('');
    const [players, setPlayers] = React.useState([
        {name: 'Evan', id: '1'},
        {name: 'Isik', id: '2'}
    ]);
    const [clues, setClues] = React.useState({
        '1': 'evans clue',
        '2': 'isiks clue'
    });
    React.useEffect(() => {
        axios.get('/api/v1/user').then(response => {
            if (response.data.user_id && response.data.game_id) {
                console.log('running effect');
                setUserId(response.data.user_id);
                setGameId(response.data.game_id);
                // don't actually need these IDs
                const ws = new WebSocket(websocketURL.href);
                ws.onopen = () => ws.send(JSON.stringify({'data': 'connected'}));
                ws.onmessage = event => {
                    const data = JSON.parse(event.data);
                    setPlayers(data.players || []);
                    if (data.round && data.round.clue && data.round.clue.clues) {
                        setClues(data.round.clue.clues)
                    }
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
    return (
        <div className={styleClasses.mainContent}>
            <Grid
                container
                direction="column"
                justify="space-between"
                alignItems="stretch"
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
                <Grid item>
                    <ClueInput
                        value={yourClue}
                        onChange={(event) => setYourClue(event.target.value)}
                        onSubmit={submitYourClue}
                    />
                </Grid>
            </Grid>
        </div>
    )
}
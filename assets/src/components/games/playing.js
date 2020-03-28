import React from 'react';
import axios from 'axios';
import { useHistory } from 'react-router-dom';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import { makeStyles } from "@material-ui/core/styles";
import ReadyInput from "./ReadyInput";
import ClueInput from "./ClueInput";
import GuessInput from "./GuessInput";
import VoteInput from "./VoteInput";
import PlayersTable from "./PlayersTable";
import CardModal from "./CardModal";
import CategoryCard from "./CategoryCard";

const useStyles = makeStyles(() => ({
    mainContent: {
        height: '65vh',
        width: '100vw',
    },
    footer: {
        minHeight: '25vh',
        minWidth: '100vw',
        backgroundColor: 'white',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center'
    },
    userTable: {
        minHeight: '100%',
        minWidth: '40%'
    },
    categoryCard: {
        minHeight: '100%',
        maxWidth: '45%'
    }
}));


const websocketURL = new URL('/websocket', window.location.href);
websocketURL.protocol = websocketURL.protocol.replace('http', 'ws');


export default function PlayingChameleon() {
    const history = useHistory();
    const styleClasses = useStyles();
    const [websocket, setWebsocket] = React.useState(null);
    const [yourClue, setYourClue] = React.useState('');
    const [yourGuess, setYourGuess] = React.useState('');
    const [yourVote, setYourVote] = React.useState('');
    const [voteLockedIn, setVoteLockedIn] = React.useState(false);
    const [ready, setReady] = React.useState(false);
    const [phase, setPhase] = React.useState('');
    const [players, setPlayers] = React.useState([]);
    const [clues, setClues] = React.useState({});
    const [showModalButton, setShowModalButton] = React.useState(true);
    const [showModal, setShowModal] = React.useState(false);
    const [cardImagePath, setCardImagePath] = React.useState('keycard.jpeg');  // remove later
    const [showCategoryCard, setShowCategoryCard] = React.useState(false);
    const [categoryImagePath, setCategoryImagePath] = React.useState('category.jpeg');  // remove later
    React.useEffect(() => {
        axios.get('/api/v1/session').then(response => {
            if (response.data.has_session && response.data.has_game) {
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

    const submitYourGuess = () => {
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
        if (phase === 'clue') {
            // pass prop to identify if it is user's turn to give clue
            return (
                <ClueInput
                    value={yourClue}
                    onChange={(event) => setYourClue(event.target.value)}
                    onSubmit={submitYourClue}
                />
            )
        }
        if (phase === 'vote') {
            return (
                <VoteInput
                    textValue={yourVote}
                    onTextChange={(event) => setYourVote(event.target.value)}
                    checked={voteLockedIn}
                    onCheckboxChange={(event) => setVoteLockedIn(event.target.checked)}
                />
            )
        }
        if (phase === 'guess') {
            // pass prop to identify if user is chameleon
            return (
                <GuessInput
                    value={yourGuess}
                    onChange={(event) => setYourGuess(event.target.value)}
                    onSubmit={submitYourGuess}
                />
            )
        }
    };

    return (
        <React.Fragment>
            <Grid
                container
                direction="column"
                justify="space-between"
                alignItems="center"
            >
                <div className={styleClasses.mainContent}>
                    <Grid item>
                        <Grid
                            container
                            direction="row"
                            justify="space-around"
                            alignItems="center"
                        >
                            <div className={styleClasses.userTable}>
                                <Grid item>
                                    <PlayersTable
                                        players={players}
                                        clues={clues}
                                    />
                                </Grid>
                            </div>
                            {showCategoryCard && ( // should probably just use gameState and calculate the rest of this stuff
                                <div className={styleClasses.categoryCard}>
                                    <Grid item>
                                        <CategoryCard imgSrc={categoryImagePath} />
                                    </Grid>
                                </div>
                            )}
                        </Grid>
                    </Grid>
                </div>
                <div className={styleClasses.footer}>
                    <Grid item>
                        {getPrimaryInput()}
                    </Grid>
                    <Grid item style={{paddingTop: '2vh'}}>
                        {showModalButton && (
                            <Button
                                variant="contained"
                                onClick={() => setShowModal(true)}
                            >Show Card</Button>
                        )}
                    </Grid>
                </div>
            </Grid>
            <CardModal
                open={showModal}
                imgSrc={cardImagePath}
                onClose={() => setShowModal(false)}
            />
        </React.Fragment>
    )
}
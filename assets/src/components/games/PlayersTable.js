import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TableContainer from '@material-ui/core/TableContainer';
import Paper from '@material-ui/core/Paper';
import React from "react";


export default function PlayersTable(props) {
    // TODO: just make players a dictionary by session id or something
    const players = props.sessionOrdering.map(sessionId => (
        (props.players || []).find(player => player.session_id === sessionId) || null
    )).filter(item => Boolean(item));
    const clues = props.clues || {};
    const votes = props.votes || {};

    return (
        <TableContainer component={Paper}>
            <Table>
                <TableHead>
                    <TableCell>User</TableCell>
                    <TableCell>Clue given</TableCell>
                    <TableCell>Vote</TableCell>
                </TableHead>
                <TableBody>
                    {players.map(player => (
                        <TableRow key={player.username}>
                            <TableCell style={{width: '20%'}}>{player.username}</TableCell>
                            <TableCell style={{width: '50%'}}>{clues[player.id] || '...'}</TableCell>
                            <TableCell style={{width: '30%'}}>{votes[player.session_id] || '...'}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    )
}
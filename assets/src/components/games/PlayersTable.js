import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TableContainer from '@material-ui/core/TableContainer';
import Paper from '@material-ui/core/Paper';
import React from "react";


export default function PlayersTable(props) {
    const players = props.players || [];
    const clues = props.clues || {};
    const votes = props.votes || {};

    return (
        <TableContainer component={Paper}>
            <Table>
                <TableHead>
                    <TableCell>User</TableCell>
                    {props.showReady && (<TableCell>Ready?</TableCell>)}
                    {props.showRestart && (<TableCell>Restart?</TableCell>)}
                    <TableCell>Clue given</TableCell>
                    <TableCell>Vote</TableCell>
                </TableHead>
                <TableBody>
                    {players.map(player => (
                        <TableRow key={`players-table-row-${player.username}`}>
                            <TableCell style={{width: '20%'}}>{player.username}</TableCell>
                            {props.showReady && (
                                <TableCell style={{width: '20%'}}>{
                                    player.ready ? "Ready" : "Not ready"
                                }</TableCell>
                            )}
                            {props.showRestart && (
                                <TableCell style={{width: '20%'}}>{
                                    player.restart ? "Playing again!" : "Undecided"
                                }</TableCell>
                            )}
                            <TableCell style={{width: '50%'}}>{clues[player.id] || '...'}</TableCell>
                            <TableCell style={{width: '30%'}}>{votes[player.session_id] || '...'}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    )
}
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

    return (
        <TableContainer component={Paper}>
            <Table>
                <TableHead>
                    <TableCell>User</TableCell>
                    <TableCell>Clue given</TableCell>
                </TableHead>
                <TableBody>
                    {players.map(player => (
                        <TableRow key={player.username}>
                            <TableCell>{player.username}</TableCell>
                            <TableCell>{clues[player.id] || '...'}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    )
}
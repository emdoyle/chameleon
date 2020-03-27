import React from 'react';
import axios from "axios";
import { useHistory } from 'react-router-dom';
import Button from '@material-ui/core/Button';
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles(() => ({
    button: {
        float: 'right',
    }
}));


export default function LeaveSessionButton() {
    const history = useHistory();
    const styleClasses = useStyles();
    const leaveSession = () => {
        axios.post('/api/v1/session').then(() => history.push('/')).catch(error => console.log(error))
    };
    return (
        <div className={styleClasses.button}>
            <Button
                onClick={leaveSession}
            >Leave session</Button>
        </div>
    )
}
import React from 'react';
import Modal from '@material-ui/core/Modal';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles(theme => ({
    modal: {
        position: 'absolute',
        top: '50%',
        left: '50%',
        width: '50vw',
        height: '50vh',
        display: 'flex',
        direction: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        transform: 'translate(-50%, -50%)',
        background: theme.palette.background.paper,
        border: '2px solid #000',
        boxShadow: theme.shadows[5],
        padding: theme.spacing(2, 4, 3),
    },
    modalContent: {
        width: '80%',
        height: '60%',
        display: 'flex',
        direction: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        fontSize: '48px'
    }
}));


export default function WinnerModal(props) {
    const styleClasses = useStyles();
    return (
        <Modal
            open={props.open}
            onClose={props.onClose}
            disableAutoFocus
        >
            <div className={styleClasses.modal}>
                <div className={styleClasses.modalContent}>{`The winner is: ${props.value || ''}!`}</div>
            </div>
        </Modal>
    );
}
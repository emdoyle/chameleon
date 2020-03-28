import React from 'react';
import Modal from '@material-ui/core/Modal';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles(theme => ({
    modal: {
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        background: theme.palette.background.paper,
        border: '2px solid #000',
        boxShadow: theme.shadows[5],
        padding: theme.spacing(2, 4, 3),
    },
}));


export default function CardModal(props) {
    const styleClasses = useStyles();
    const [imageFailed, setImageFailed] = React.useState(false);

    const handleImageLoadError = error => {
        console.log(error);
        setImageFailed(true);
    };

    return (
        <Modal
            open={props.open}
            onClose={props.onClose}
            disableAutoFocus
        >
            <div className={styleClasses.modal}>
                {!Boolean(imageFailed) && (
                    <img alt="Could not load" onError={handleImageLoadError} src={props.imgSrc} />
                )}
            </div>
        </Modal>
    )
}
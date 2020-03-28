import React from 'react';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles(theme => ({
    card: {
        background: theme.palette.background.paper,
        border: '2px solid #000',
    },
    image: {
        maxWidth: '100%',
        height: 'auto'
    }
}));


export default function CategoryCard(props) {
    const styleClasses = useStyles();

    const handleImageLoadError = error => {
        console.log(error);
    };

    return (
        <div className={styleClasses.card}>
            <img
                className={styleClasses.image}
                alt="Could not load"
                onError={handleImageLoadError}
                src={props.imgSrc}
            />
        </div>
    );
}
import React from 'react';
import Input from '@material-ui/core/Input';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles(() => ({
    nameInput: {
        backgroundColor: 'white',
        minWidth: '40vw'
    }
}));


export default function TextInput(props) {
    const styleClasses = useStyles();
    return (
        <Grid
            container
            direction="row"
            justify="center"
            alignItems="center"
            spacing={4}
        >
            <Grid item>
                <TextField
                    id={props.id || 'default-text-field'}
                    className={styleClasses.nameInput}
                    required
                    disabled={Boolean(props.disabled)}
                    label={props.label || ''}
                    variant='outlined'
                    onChange={props.onChange}
                >
                    <Input
                        value={props.value}
                    />
                </TextField>
            </Grid>
            {!Boolean(props.hideButton) && (
                <Grid item>
                    <Button
                        variant='contained'
                        onClick={props.onSubmit}
                    >{props.buttonText || 'Submit'}</Button>
                </Grid>
            )}
        </Grid>
    );
}
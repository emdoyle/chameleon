import React from 'react';
import Grid from "@material-ui/core/Grid";
import Checkbox from "@material-ui/core/Checkbox";
import FormControlLabel from '@material-ui/core/FormControlLabel';
import FormControl from '@material-ui/core/FormControl';
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles(() => ({
    label: {
        color: 'black',
    },
}));


export default function ReadyInput(props) {
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
                <FormControl component="fieldset">
                    <FormControlLabel
                        control={<Checkbox
                            checked={props.value}
                            onChange={props.onChange}
                            name="ready-checkbox"
                        />}
                        label="Ready?"
                        classes={{
                            label: styleClasses.label,
                        }}
                    />
                </FormControl>
            </Grid>
        </Grid>
    )
}

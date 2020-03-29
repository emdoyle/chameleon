import React from 'react';
import Grid from "@material-ui/core/Grid";
import FormControl from "@material-ui/core/FormControl";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import Checkbox from "@material-ui/core/Checkbox";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles(() => ({
    label: {
        color: 'black',
    },
}));


export default function CheckboxInput(props) {
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
                            disabled={Boolean(props.disabled)}
                            checked={props.value}
                            onChange={props.onChange}
                            name={props.name || 'default-checkbox-input'}
                        />}
                        label={props.label}
                        classes={{
                            label: styleClasses.label,
                        }}
                    />
                </FormControl>
            </Grid>
        </Grid>
    )
}
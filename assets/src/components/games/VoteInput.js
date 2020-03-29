import React from 'react';
import Grid from '@material-ui/core/Grid';
import TextInput from "../utils/TextInput";
import CheckboxInput from "../utils/CheckboxInput";


export default function VoteInput(props) {
    return (
        <Grid
            container
            direction="row"
            justify="center"
            alignItems="center"
            spacing={4}
        >
            <Grid item>
                <TextInput
                    label={props.label}
                    value={props.textValue}
                    onChange={props.onTextChange}
                    disabled={Boolean(props.checked)}
                    hideButton
                />
            </Grid>
            <Grid item>
                <CheckboxInput
                    disabled={!Boolean(props.textValue)}
                    value={Boolean(props.checked)}
                    onChange={props.onCheckboxChange}
                    label="Confirm"
                />
            </Grid>
        </Grid>
    )
}
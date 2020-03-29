import React from 'react';
import Grid from '@material-ui/core/Grid';
import Select from "../utils/Select";
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
                <Select
                    label={props.label}
                    value={props.selectedOption}
                    options={props.options}
                    onChange={props.onOptionChange}
                    disabled={Boolean(props.checked)}
                />
            </Grid>
            <Grid item>
                <CheckboxInput
                    disabled={!Boolean(props.selectedOption)}
                    value={Boolean(props.checked)}
                    onChange={props.onCheckboxChange}
                    label="Confirm"
                />
            </Grid>
        </Grid>
    )
}
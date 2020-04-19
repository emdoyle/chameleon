import React from 'react';
import CheckboxInput from "../utils/CheckboxInput";


export default function RestartInput(props) {
    return (
        <CheckboxInput
            onChange={props.onChange}
            value={props.value}
            name="restart-checkbox"
            label="Start a new round?"
        />
    )
}

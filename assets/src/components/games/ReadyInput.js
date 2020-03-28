import React from 'react';
import CheckboxInput from "../utils/CheckboxInput";


export default function ReadyInput(props) {
    return (
        <CheckboxInput
            onChange={props.onChange}
            value={props.value}
            name="ready-checkbox"
            label="Ready?"
        />
    )
}

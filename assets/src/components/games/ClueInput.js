import React from 'react';
import TextInput from '../utils/TextInput';


export default function ClueInput(props) {
    return (!Boolean(props.hidden) && (
            <TextInput
                label={'Give a clue!'}
                onChange={props.onChange}
                value={props.value}
                onSubmit={props.onSubmit}
                buttonText={'Submit'}
            />
        )
    );
}
import React from 'react';
import TextInput from '../utils/TextInput';


export default function GuessInput(props) {
    return (
        <React.Fragment>
        {!Boolean(props.hidden) && (
            <TextInput
                label={'Guess what the word was!'}
                onChange={props.onChange}
                value={props.value}
                onSubmit={props.onSubmit}
                buttonText={'Guess'}
            />
        )}
        </React.Fragment>
    )
}
import React from 'react';
import Select from '@material-ui/core/Select';
import MenuItem from "@material-ui/core/MenuItem";
import FormControl from "@material-ui/core/FormControl";
import InputLabel from "@material-ui/core/InputLabel";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles(theme => ({
    select: {
        backgroundColor: 'white',
        minWidth: '25vw',
    },
    selectItem: {
        minHeight: '5vh',
    }
}));


export default function CustomSelect(props) {
    const styleClasses = useStyles();
    const labelId = props.labelId || 'select-label';
    const options = [{'label': '', 'value': ''}, ...props.options];
    return (
        <div>
            <FormControl className={styleClasses.select} disabled={props.disabled}>
                <InputLabel id={labelId}>{props.label}</InputLabel>
                <Select
                    labelId={labelId}
                    id={props.id || 'default-select-id'}
                    value={props.value}
                    onChange={props.onChange}
                >
                    {options.map(option => (
                        <MenuItem
                            className={styleClasses.selectItem}
                            value={option.value}>{option.label}</MenuItem>
                    ))}
                </Select>
            </FormControl>
        </div>
    );
}
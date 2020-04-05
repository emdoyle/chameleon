import React from 'react';
import 'css/dice.css';

const bigDie = (roll) => {
    switch(roll) {
        case 1:
            return (
                <div className="dice first-face">
                    <span className="dot" />
                </div>
            );
        case 2:
            return (
                <div className="dice second-face">
                    <span className="dot" />
                    <span className="dot" />
                </div>
            );
        case 3:
            return (
                <div className="dice third-face">
                    <span className="dot" />
                    <span className="dot" />
                    <span className="dot" />
                </div>
            );
        case 4:
            return (
                <div className="dice fourth-face">
                    <div className="dot-column">
                        <span className="dot" />
                        <span className="dot" />
                    </div>
                    <div className="dot-column">
                        <span className="dot" />
                        <span className="dot" />
                    </div>
                </div>
            );
        case 5:
            return (
                <div className="dice fifth-face">
                    <div className="dot-column">
                        <span className="dot" />
                        <span className="dot" />
                    </div>
                    <div className="dot-column">
                        <span className="dot" />
                    </div>
                    <div className="dot-column">
                        <span className="dot" />
                        <span className="dot" />
                    </div>
                </div>
            );
        case 6:
            return (
                <div className="dice sixth-face">
                    <div className="dot-column">
                        <span className="dot" />
                        <span className="dot" />
                        <span className="dot" />
                    </div>
                    <div className="dot-column">
                        <span className="dot" />
                        <span className="dot" />
                        <span className="dot" />
                    </div>
                </div>
            );
        default:
            console.log('Dice must receive roll');
            return <React.Fragment />
    }
};
const smallDie = (roll) => {
    return (
        <div style={{
            maxWidth: '100px',
            maxHeight: '100px',
        }}>
            <img
                src="small_die.svg"
                alt={`Small die with ${roll}`}
                style={{
                    zIndex: 1
                }}
            />
            <div style={{
                zIndex: 2,
                color: 'white',
                position: 'relative',
                top: '-100px',
                left: '5px'
            }}>{roll}</div>
        </div>
    )
};

export default function Dice(props) {
    // could prop forward to child components later
    if (props.bigDie) {
        return bigDie(props.roll);
    } else if (props.smallDie) {
        return smallDie(props.roll);
    } else {
        console.log('Dice must receive bigDie or smallDie');
        return <React.Fragment />
    }
}

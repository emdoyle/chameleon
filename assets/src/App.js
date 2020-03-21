import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import AndroidIcon from '@material-ui/icons/Android';
import logo from 'images/logo512.png';
import 'css/App.css';

const useStyles = makeStyles(theme => ({
  menuIconPadRight: {
    marginRight: theme.spacing(2),
  },
}));

function App() {
  const classes = useStyles();
  return (
    <div className="App">
      <AppBar color='primary' position='static'>
        <Toolbar>
          <AndroidIcon className={classes.menuIconPadRight} />
          <Typography>Chameleon</Typography>
        </Toolbar>
      </AppBar>
      <div className="App-main">
        <img src={logo} className="App-logo" alt="logo" />
      </div>
    </div>
  );
}

export default App;

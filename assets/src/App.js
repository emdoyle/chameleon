import React from 'react';
import {
    BrowserRouter as Router,
    Switch,
    Route,
} from 'react-router-dom';
import { makeStyles } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import VisibilityIcon from '@material-ui/icons/Visibility';
import HomePage from 'components/home';
import 'css/App.css';

const useStyles = makeStyles(theme => ({
    menuIconPadRight: {
        marginRight: theme.spacing(2),
    },
}));

function App() {
  const classes = useStyles();
  return (
      <Router>
          <div className="App">
          <AppBar color='primary' position='static'>
              <Toolbar>
                  <VisibilityIcon className={classes.menuIconPadRight} />
                  <Typography>Chameleon</Typography>
              </Toolbar>
          </AppBar>
          <div className="App-main">
              <Switch>
                  <Route path={"/"}>
                      <HomePage/>
                  </Route>
              </Switch>
          </div>
        </div>
      </Router>
  );
}

export default App;

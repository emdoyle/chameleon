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
import Games from 'components/games';
import Chameleon from 'components/games/playing';
import LeaveSessionButton from 'components/utils/LeaveSessionButton';
import 'css/App.css';

const useStyles = makeStyles(theme => ({
    menuIconPadRight: {
        marginRight: theme.spacing(2),
    },
    toolbarRoot: {
        flexGrow: 1,
    },
    siteTitle: {
        flexGrow: 1,
        textAlign: 'left',
    },
}));

function App() {
  const styleClasses = useStyles();
  return (
      <Router>
          <div className="App">
              <div className="App-header">
              <div className={styleClasses.toolbarRoot}>
              <AppBar color='primary' position='static'>
                  <Toolbar>
                      <VisibilityIcon className={styleClasses.menuIconPadRight} />
                      <Typography
                          className={styleClasses.siteTitle}
                      >Chameleon</Typography>
                      <LeaveSessionButton/>
                  </Toolbar>
              </AppBar>
              </div>
              </div>
          <div className="App-main">
              <Switch>
                  <Route path={"/games"}>
                      <Games/>
                  </Route>
                  <Route path={"/chameleon"}>
                      <Chameleon/>
                  </Route>
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

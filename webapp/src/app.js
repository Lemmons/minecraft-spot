import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from 'material-ui/styles';
import AppBar from 'material-ui/AppBar';
import Toolbar from 'material-ui/Toolbar';
import Typography from 'material-ui/Typography';
import Button from 'material-ui/Button';
import IconButton from 'material-ui/IconButton';
import MenuIcon from '@material-ui/icons/Menu';

import { StartServerButton, StopServerButton, ServerStatus } from './server';


const styles = {
  root: {
    flexGrow: 1,
  },
  flex: {
    flex: 1,
  },
  menuButton: {
    marginLeft: -12,
    marginRight: 20,
  },
};

function LoginTitleBar(props) {
  const { classes } = props;
  const { isAuthenticated } = props.auth;

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="title" color="inherit" className={classes.flex}>
          Minecraft Spot Controls
        </Typography>
        <StartServerButton {...props}/>
        <StopServerButton {...props}/>
        {
          !isAuthenticated() && (
          <Button
            color="inherit"
            onClick={() => props.auth.login()}
          >
            Login
          </Button>
          )
        }
        {
          isAuthenticated() && (
          <div>
            <Button
              color="inherit"
              onClick={() => props.auth.logout()}
            >
              Logout
            </Button>
          </div>
          )
        }
      </Toolbar>
    </AppBar>
  );
}

function App(props) {
  const { classes } = props;

  return (
    <div>
      <div className={classes.root}>
        <LoginTitleBar {...props}/>
      </div>
      <ServerStatus {...props}/>
    </div>
  );
}

App.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(App);

import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from 'material-ui/styles';
import AppBar from 'material-ui/AppBar';
import Toolbar from 'material-ui/Toolbar';
import Typography from 'material-ui/Typography';
import Button from 'material-ui/Button';
import IconButton from 'material-ui/IconButton';
import MenuIcon from '@material-ui/icons/Menu';

import Auth from './auth.js';


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

class App extends React.Component {
  login() {
    this.props.auth.login();
  }

  logout() {
    this.props.auth.logout();
  }

  render() {
    const { classes } = this.props;
    const { isAuthenticated } = this.props.auth;

    return (
      <div>
        <div className={classes.root}>
          <AppBar position="static">
            <Toolbar>
              {/* <IconButton className={classes.menuButton} color="inherit" aria-label="Menu"> */}
                {/* <MenuIcon /> */}
              {/* </IconButton> */}
              <Typography variant="title" color="inherit" className={classes.flex}>
                Minecraft Spot Controls
              </Typography>
              {
                !isAuthenticated() && (
                <Button
                  color="inherit"
                  onClick={this.login.bind(this)}
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
                  >
                    Start Server
                  </Button>
                  <Button
                    color="inherit"
                  >
                    Stop Server
                  </Button>
                  <Button
                    color="inherit"
                    onClick={this.logout.bind(this)}
                  >
                    Logout
                  </Button>
                </div>
                )
              }
            </Toolbar>
          </AppBar>
        </div>
      </div>
    );
  }
}

App.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(App);

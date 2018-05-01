import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from 'material-ui/styles';
import AppBar from 'material-ui/AppBar';
import Toolbar from 'material-ui/Toolbar';
import Typography from 'material-ui/Typography';
import Button from 'material-ui/Button';
import IconButton from 'material-ui/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import Snackbar from 'material-ui/Snackbar';
import red from 'material-ui/colors/red';

import ServerStatus from './server';


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
  error: {
    color: 'white',
    backgroundColor: red[900],
  }
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
        {
          !isAuthenticated() && (
          <Button
            className={classes.menuButton}
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
              className={classes.menuButton}
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

class App extends React.Component {
  state = {
    open: true
  }

  handleCloseError() {
    this.setState({ open: false });
    this.props.auth.clearError();
  };

  render(){
    const { classes, ...others } = this.props;
    return (
      <div>
        <div className={classes.root}>
          <LoginTitleBar {...this.props}/>
        </div>
        { this.props.auth.hasError() && (
          <Snackbar
            anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
            message={this.props.auth.hasError()}
            open={this.state.open}
            onClose={this.handleCloseError.bind(this)}
            SnackbarContentProps={{
              className: classes.error,
            }}
          />
          )
        }
        {
          this.props.auth.isAuthenticated() && (
            <ServerStatus {...others}/>
          )
        }
      </div>
    );
  }
}

App.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(App);

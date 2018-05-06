import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from 'material-ui/styles';
import Button from 'material-ui/Button';
import List, {
  ListItem,
  ListItemSecondaryAction,
  ListItemText,
} from 'material-ui/List';
import { InputAdornment } from 'material-ui/Input';
import Divider from 'material-ui/Divider';
import TextField from 'material-ui/TextField';
import Switch from 'material-ui/Switch';
import Grid from 'material-ui/Grid';
import Paper from 'material-ui/Paper';
import Typography from 'material-ui/Typography';
import axios from 'axios';
import ReactInterval from 'react-interval';

import { API_CONFIG } from './config';


const styles = theme => ({
  root: {
    flexGrow: 1,
  },
  paper: {
    padding: theme.spacing.unit * 2,
    textAlign: 'center',
    color: theme.palette.text.secondary,
  },
  textField: {
    marginLeft: theme.spacing.unit,
    marginRight: theme.spacing.unit,
    width: 100,
  },
  title: {
    fontSize: 14,
  },
  button: {
    margin: theme.spacing.unit,
  },
});

class ServerStatus extends React.Component {
  constructor(props) {
    super(props);
    this.classes = this.props.classes;
    this.state = {
      desiredCapacity: -1,
      status: "unknown",
      poll: false,
      autoPoll: false,
      pollInterval: 30000,
    };
  }

  componentDidMount() {
    this.tick();
  }

  tick() {
    console.log('server status: tick');
    if (this.props.auth.isAuthenticated() ) {
      const headers = { 'Authorization': `Bearer ${this.props.auth.getAccessToken()}` }
      axios.get(`${API_CONFIG.api_url}/minecraft/status`, { headers })
        .then(response => {
          var serverStatus = 'Unknown'
          if (['Stopped', 'Stopping'].indexOf(response.data.status) >= 0 &&
            response.data.desired_capacity >= 1) {
            serverStatus = 'Starting';
          }
          else if (['Starting', 'Running'].indexOf(response.data.status) >= 0 &&
            response.data.desired_capacity == 0) {
            serverStatus = 'Stopping';
          }
          else {
            serverStatus = response.data.status;
          }

          var poll = false;
          if (['Starting', 'Stopping'].indexOf(serverStatus) >= 0) {
            poll = true;
          }

          this.setState({
            desiredCapacity: response.data.desired_capacity,
            status: serverStatus,
            autoPoll: poll
          });
        })
        .catch(error => {
          console.log(error);
          this.setState({
            status: "Unknown",
            message: error.message
          });
        });
    }
  }

  isStoppedOrStopping() {
    if (['Stopped', 'Stopping'].indexOf(this.state.status) >= 0) {
      return true;
    }
    return false;
  }

  isStartedOrStarting() {
    if (['Running', 'Starting'].indexOf(this.state.status) >= 0) {
      return true;
    }
    return false;
  }

  startServer() {
    console.log('Starting');
    const headers = { 'Authorization': `Bearer ${this.props.auth.getAccessToken()}` }

    axios.get(`${API_CONFIG.api_url}/minecraft/start`, { headers })
      .then(response => {
        this.setState({ message: response.data.message });
        this.tick();
      })
      .catch(error => this.setState({ message: error.message }));
  }

  stopServer() {
    console.log('Stopping');
    const headers = { 'Authorization': `Bearer ${this.props.auth.getAccessToken()}` }

    axios.get(`${API_CONFIG.api_url}/minecraft/stop`, { headers })
      .then(response => {
        this.setState({ message: response.data.message });
        this.tick();
      })
      .catch(error => this.setState({ message: error.message }));
  }

  handlePollToggle(event, checked) {
    this.setState({
      poll: checked
    });
  }

  handlePollInterval(event) {
    this.setState({
      pollInterval: parseInt(event.target.value) * 1000
    });
  }

  render() {
    return (
      <div className={this.classes.root}>
        <ReactInterval
          timeout={this.state.pollInterval}
          enabled={this.state.poll || this.state.autoPoll}
          callback={this.tick.bind(this)} />
        <Grid container spacing={24}>
          <Grid item xs={12} sm={6} md={4}>
            <Paper className={this.classes.paper}>
              <Typography className={this.classes.title} color="textSecondary">
                Server Status
              </Typography>
              <List>
                <ListItem>
                  <ListItemSecondaryAction>
                    { this.isStoppedOrStopping() && (
                      <Button
                        variant="raised"
                        color="secondary"
                        onClick={this.startServer.bind(this)} >
                        Start Server
                      </Button>
                    )}
                    { this.isStartedOrStarting() && (
                      <Button
                        variant="raised"
                        color="secondary"
                        onClick={this.stopServer.bind(this)} >
                        Stop Server
                      </Button>
                    )}
                  </ListItemSecondaryAction>
                </ListItem>
                <ListItem>
                  <ListItemText primary="Status" />
                  <ListItemSecondaryAction>
                    {this.state.status}
                  </ListItemSecondaryAction>
                </ListItem>
                { false ? <ListItem>
                  <ListItemText primary="Desired Instance Count" />
                  <ListItemSecondaryAction>
                    {this.state.desiredCapacity.toString()}
                  </ListItemSecondaryAction>
                </ListItem> : null }
              </List>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Paper className={this.classes.paper}>
              <Typography className={this.classes.title} color="textSecondary">
                Status Update Controls
              </Typography>
              <List>
                <ListItem>
                  <ListItemText primary="Server Status" />
                  <ListItemSecondaryAction>
                    <Button
                      variant="raised"
                      color="secondary"
                      onClick={this.tick.bind(this)}
                      className={this.classes.button} >
                      Refresh
                    </Button>
                  </ListItemSecondaryAction>
                </ListItem>
                { this.state.autoPoll ? <ListItem>
                  <ListItemText primary="Auto-refreshing" />
                  <ListItemSecondaryAction>
                    every {this.state.pollInterval / 1000}s
                  </ListItemSecondaryAction>
                </ListItem> : null }
                { false ? <ListItem>
                  <ListItemText primary="Auto-refresh" />
                  <ListItemSecondaryAction>
                    <Switch
                      onChange={this.handlePollToggle.bind(this)}
                      checked={this.state.poll}
                    />
                  </ListItemSecondaryAction>
                </ListItem> : null }
                { this.state.poll ? <ListItem>
                  <ListItemText primary="Refresh Interval" />
                  <ListItemSecondaryAction>
                    <TextField
                      id="number"
                      value={this.state.pollInterval / 1000}
                      onChange={this.handlePollInterval.bind(this)}
                      type="number"
                      disabled={!this.state.poll}
                      className={this.classes.textField}
                      InputLabelProps={{
                        shrink: true,
                      }}
                      InputProps={{
                        startAdornment: <InputAdornment position="start">Sec</InputAdornment>,
                      }}
                      margin="normal"
                    />
                  </ListItemSecondaryAction>
                </ListItem> : null }
              </List>
            </Paper>
          </Grid>
        </Grid>
      </div>
    );
  }
}

ServerStatus.propTypes = {
    classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(ServerStatus);

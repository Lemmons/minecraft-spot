import React from 'react';
import Button from 'material-ui/Button';
import axios from 'axios';

import { API_CONFIG } from './config';

export class StartServerButton extends React.Component {
  start() {
    console.log('Starting');
    const headers = { 'Authorization': `Bearer ${this.props.auth.getAccessToken()}` }

    axios.get(`${API_CONFIG.api_url}/minecraft/start`, { headers })
      .then(response => this.setState({ message: response.data.message }))
      .catch(error => this.setState({ message: error.message }));
  }

  render() {
    return (
      <div>
        {
          this.props.auth.isAuthenticated() && (
            <Button
              color="inherit"
              onClick={this.start.bind(this)}
            >
              Start Server
            </Button>
          )
        }
      </div>
    );
  }
}

export class StopServerButton extends React.Component {
  stop() {
    console.log('Stopping');
    const headers = { 'Authorization': `Bearer ${this.props.auth.getAccessToken()}` }

    axios.get(`${API_CONFIG.api_url}/minecraft/stop`, { headers })
      .then(response => this.setState({ message: response.data.message }))
      .catch(error => this.setState({ message: error.message }));
  }

  render() {
    return (
      <div>
        {
          this.props.auth.isAuthenticated() && (
            <Button
              color="inherit"
              onClick={this.stop.bind(this)}
            >
              Stop Server
            </Button>
          )
        }
      </div>
    );
  }
}

export class ServerStatus extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      desiredCapacity: -1,
      status: "unknown"
    };
    this.tick()
  }

  componentDidMount() {
    this.timerID = setInterval(
      () => this.tick(),
      10000
    );
  }

  componentWillUnmount() {
    clearInterval(this.timerID);
  }

  tick() {
    if (this.props.auth.isAuthenticated()) {
      const headers = { 'Authorization': `Bearer ${this.props.auth.getAccessToken()}` }
      axios.get(`${API_CONFIG.api_url}/minecraft/status`, { headers })
        .then(response => this.setState({
          desiredCapacity: response.data.desired_capacity,
          status: response.data.status
        }))
        .catch(error => this.setState({
          status: "Unknown",
          message: error.message
        }));
    }
  }

  render() {
    return (
      <div>
        {
          this.props.auth.isAuthenticated() && (
          <div>
            <h3>Server Status: {this.state.status}</h3>
            <h3>Desired Instance Count: {this.state.desiredCapacity.toString()}</h3>
          </div>
          )
        }
      </div>
    );
  }
}

import axios from 'axios';
import { API_CONFIG } from './config';

export default class Control {
  constructor(auth) {
    this.auth = auth;
  }

  start() {
    const { getAccessToken } = this.auth;
    const api_url = API_CONFIG.api_url;
    const headers = { 'Authorization': `Bearer ${getAccessToken()}` }

    axios.get(`${API_CONFIG.api_url}/minecraft/start`, { headers })
      .then(response => this.setState({ message: response.data.message }))
      .catch(error => this.setState({ message: error.message }));
  }

  stop() {
    const { getAccessToken } = this.auth;
    const api_url = API_CONFIG.api_url;
    const headers = { 'Authorization': `Bearer ${getAccessToken()}` }

    axios.get(`${API_CONFIG.api_url}/minecraft/stop`, { headers })
      .then(response => this.setState({ message: response.data.message }))
      .catch(error => this.setState({ message: error.message }));
  }

  status() {
  }
}

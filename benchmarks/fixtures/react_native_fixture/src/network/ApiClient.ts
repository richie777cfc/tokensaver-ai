import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'https://example.com/api',
});

export async function fetchStatus() {
  return apiClient.get('/status');
}

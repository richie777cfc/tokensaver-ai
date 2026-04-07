import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:3001',
});

export const fetchUsers = () => apiClient.get('/api/users');
export const createUser = (data: any) => apiClient.post('/api/users', data);
export const fetchPosts = () => apiClient.get('/api/posts');
export const deletePost = (id: string) => apiClient.delete(`/api/posts/${id}`);

export async function fetchHealth() {
  return fetch('/api/health');
}

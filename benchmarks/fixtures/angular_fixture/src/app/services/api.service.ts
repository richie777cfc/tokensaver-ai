import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getUsers() {
    return this.http.get('/api/users');
  }

  createUser(data: any) {
    return this.http.post('/api/users', data);
  }

  getPost(id: string) {
    return this.http.get(`/api/posts/${id}`);
  }

  deletePost(id: string) {
    return this.http.delete(`/api/posts/${id}`);
  }

  updateSettings(settings: any) {
    return this.http.put('/api/settings', settings);
  }
}

import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'dashboard', loadComponent: () => import('./components/dashboard.component') },
  { path: 'profile/:id', component: ProfileComponent },
  { path: 'settings', component: SettingsComponent },
  { path: 'admin', children: [
    { path: 'users', component: AdminUsersComponent },
    { path: 'reports', component: AdminReportsComponent },
  ]},
];

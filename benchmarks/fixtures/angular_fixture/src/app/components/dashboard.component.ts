import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-dashboard',
  template: '<div>Dashboard</div>',
})
export class DashboardComponent {
  constructor(private router: Router) {}

  goToProfile(id: string) {
    this.router.navigate(['/profile', id]);
  }

  goToSettings() {
    this.router.navigateByUrl('/settings');
  }

  get analyticsKey() {
    return environment.analyticsKey;
  }
}

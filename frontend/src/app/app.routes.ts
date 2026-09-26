import { Routes } from '@angular/router';
import { authGuard, guestGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  {
    path: 'login',
    canActivate: [guestGuard],
    loadComponent: () => import('./pages/auth/login.component').then(m => m.LoginComponent),
  },
  {
    path: 'signup',
    canActivate: [guestGuard],
    loadComponent: () => import('./pages/auth/signup.component').then(m => m.SignupComponent),
  },
  {
    path: 'dashboard',
    canActivate: [authGuard],
    loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent),
  },
  {
    path: 'campaigns/new',
    canActivate: [authGuard],
    loadComponent: () => import('./pages/campaign-create/campaign-create.component').then(m => m.CampaignCreateComponent),
  },
  {
    path: 'campaigns/:id',
    canActivate: [authGuard],
    loadComponent: () => import('./pages/campaign-detail/campaign-detail.component').then(m => m.CampaignDetailComponent),
  },
  {
    path: 'brand-rules',
    canActivate: [authGuard],
    loadComponent: () => import('./pages/brand-rules/brand-rules.component').then(m => m.BrandRulesComponent),
  },
  { path: '**', redirectTo: '/dashboard' },
];

import { Injectable, signal, computed } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap, catchError, of } from 'rxjs';

export type UserRole = 'admin' | 'brand_guardian' | 'campaign_architect' | 'compliance_officer';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
  role: UserRole;
}

export interface UpdateProfilePayload {
  full_name?: string;
  email?: string;
  role?: UserRole;
  password?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly baseUrl = 'http://localhost:8000/api';
  private readonly TOKEN_KEY = 'ong_access_token';
  private readonly USER_KEY = 'ong_user_profile';

  // Signals
  currentUser = signal<User | null>(this.getStoredUser());
  isAuthenticated = computed(() => !!this.currentUser());
  userName = computed(() => this.currentUser()?.full_name || 'Enterprise User');
  userEmail = computed(() => this.currentUser()?.email || '');
  userRole = computed(() => this.currentUser()?.role || 'campaign_architect');

  userRoleLabel = computed(() => {
    const role = this.userRole();
    switch (role) {
      case 'admin':
        return 'System Administrator';
      case 'brand_guardian':
        return 'Brand Guardian';
      case 'campaign_architect':
        return 'Campaign Architect';
      case 'compliance_officer':
        return 'Compliance Officer';
      default:
        return 'Team Member';
    }
  });

  userInitials = computed(() => {
    const name = this.userName().trim();
    if (!name) return 'AC';
    const parts = name.split(/\s+/);
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  });

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    // If token exists, verify session with backend
    if (this.getToken()) {
      this.refreshProfile().subscribe();
    }
  }

  private getStoredUser(): User | null {
    try {
      const data = localStorage.getItem(this.USER_KEY);
      return data ? JSON.parse(data) : null;
    } catch {
      return null;
    }
  }

  getToken(): string | null {
    try {
      return localStorage.getItem(this.TOKEN_KEY);
    } catch {
      return null;
    }
  }

  private setSession(authResult: TokenResponse): void {
    try {
      localStorage.setItem(this.TOKEN_KEY, authResult.access_token);
      localStorage.setItem(this.USER_KEY, JSON.stringify(authResult.user));
    } catch (err) {
      console.warn('Failed to save auth session to localStorage', err);
    }
    this.currentUser.set(authResult.user);
  }

  login(credentials: LoginPayload): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.baseUrl}/auth/login`, credentials).pipe(
      tap(res => this.setSession(res))
    );
  }

  register(payload: RegisterPayload): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.baseUrl}/auth/register`, payload).pipe(
      tap(res => this.setSession(res))
    );
  }

  updateProfile(payload: UpdateProfilePayload): Observable<TokenResponse> {
    const token = this.getToken();
    let headers = new HttpHeaders();
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }
    return this.http.put<TokenResponse>(`${this.baseUrl}/auth/me`, payload, { headers }).pipe(
      tap(res => this.setSession(res))
    );
  }

  refreshProfile(): Observable<User | null> {
    const token = this.getToken();
    if (!token) return of(null);

    return this.http.get<User>(`${this.baseUrl}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    }).pipe(
      tap(user => {
        this.currentUser.set(user);
        try {
          localStorage.setItem(this.USER_KEY, JSON.stringify(user));
        } catch {}
      }),
      catchError(() => {
        this.logout(false);
        return of(null);
      })
    );
  }

  logout(redirect: boolean = true): void {
    try {
      localStorage.removeItem(this.TOKEN_KEY);
      localStorage.removeItem(this.USER_KEY);
    } catch {}
    this.currentUser.set(null);
    if (redirect) {
      this.router.navigate(['/login']);
    }
  }
}

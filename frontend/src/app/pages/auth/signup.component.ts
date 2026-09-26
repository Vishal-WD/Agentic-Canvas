import { Component, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService, UserRole } from '../../services/auth.service';

interface RoleOption {
  id: UserRole;
  title: string;
  desc: string;
  icon: string;
}

@Component({
  selector: 'app-signup',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="auth-page">
      <!-- Ambient Glow Orbs -->
      <div class="ambient-glow orb-blue"></div>
      <div class="ambient-glow orb-gold"></div>

      <!-- Auth Container -->
      <div class="auth-card-container">
        <div class="glass-neu-card">
          <!-- Card Header / Brand -->
          <div class="auth-header">
            <div class="brand-badge-ring">
              <img src="assets/agentic-canvas-logo.png" alt="Agentic Canvas Logo" class="brand-logo" />
            </div>
            <h1 class="auth-title">Create Enterprise Account</h1>
            <p class="auth-subtitle">Join the Agentic Canvas platform with role-based governance</p>
          </div>

          <!-- Error Alert Banner -->
          <div *ngIf="errorMessage()" class="auth-alert error-alert">
            <span class="alert-icon">⚠</span>
            <span class="alert-text">{{ errorMessage() }}</span>
          </div>

          <!-- Signup Form -->
          <form (ngSubmit)="onSubmit()" class="auth-form" #signupForm="ngForm">
            <!-- Full Name Input -->
            <div class="form-group">
              <label for="fullName" class="form-label">Full Name</label>
              <div class="input-well-wrapper">
                <span class="input-prefix-icon">👤</span>
                <input
                  id="fullName"
                  name="fullName"
                  type="text"
                  class="neu-input-well"
                  placeholder="e.g. Dr. Jane Sterling"
                  [(ngModel)]="fullName"
                  required
                  autocomplete="name"
                  [disabled]="isLoading()"
                />
              </div>
            </div>

            <!-- Email Input -->
            <div class="form-group">
              <label for="email" class="form-label">Enterprise Email</label>
              <div class="input-well-wrapper">
                <span class="input-prefix-icon">✉</span>
                <input
                  id="email"
                  name="email"
                  type="email"
                  class="neu-input-well"
                  placeholder="jane.sterling@oandg.ai"
                  [(ngModel)]="email"
                  required
                  autocomplete="username"
                  [disabled]="isLoading()"
                />
              </div>
            </div>

            <!-- Password Input + Strength Meter -->
            <div class="form-group">
              <div class="password-label-row">
                <label for="password" class="form-label">Password</label>
                <span class="strength-label" [style.color]="strengthColor()">{{ strengthText() }}</span>
              </div>
              <div class="input-well-wrapper">
                <span class="input-prefix-icon">🔒</span>
                <input
                  id="password"
                  name="password"
                  [type]="showPassword ? 'text' : 'password'"
                  class="neu-input-well"
                  placeholder="Minimum 6 characters"
                  [(ngModel)]="password"
                  required
                  autocomplete="new-password"
                  [disabled]="isLoading()"
                />
                <button
                  type="button"
                  class="toggle-visibility-btn"
                  (click)="showPassword = !showPassword"
                  [attr.aria-label]="showPassword ? 'Hide password' : 'Show password'"
                  tabindex="-1"
                >
                  {{ showPassword ? '👁' : '👁‍🗨' }}
                </button>
              </div>

              <!-- Password Strength Bar Segments -->
              <div class="strength-meter-row">
                <div class="strength-bar" [class.active]="strengthScore() >= 1" [style.background]="strengthScore() >= 1 ? strengthColor() : ''"></div>
                <div class="strength-bar" [class.active]="strengthScore() >= 2" [style.background]="strengthScore() >= 2 ? strengthColor() : ''"></div>
                <div class="strength-bar" [class.active]="strengthScore() >= 3" [style.background]="strengthScore() >= 3 ? strengthColor() : ''"></div>
                <div class="strength-bar" [class.active]="strengthScore() >= 4" [style.background]="strengthScore() >= 4 ? strengthColor() : ''"></div>
              </div>
            </div>

            <!-- Role Selection Pill Grid -->
            <div class="form-group">
              <label class="form-label">Enterprise Role & Permissions</label>
              <div class="role-pill-grid">
                <div
                  *ngFor="let r of roleOptions"
                  class="role-pill"
                  [class.selected]="selectedRole === r.id"
                  (click)="selectRole(r.id)"
                  role="button"
                  tabindex="0"
                >
                  <div class="role-pill-top">
                    <span class="role-icon">{{ r.icon }}</span>
                    <span class="role-pill-title">{{ r.title }}</span>
                  </div>
                  <span class="role-pill-desc">{{ r.desc }}</span>
                  <div class="role-radio-indicator"></div>
                </div>
              </div>
            </div>

            <!-- Submit Button (Tactile Extruded Gold) -->
            <button
              type="submit"
              class="gold-cta-button"
              [disabled]="isLoading() || !isFormValid()"
              [class.loading]="isLoading()"
            >
              <span *ngIf="!isLoading()" class="btn-content">
                <span>Create Enterprise Account</span>
                <span class="btn-arrow">→</span>
              </span>
              <span *ngIf="isLoading()" class="btn-loading">
                <span class="spinner"></span>
                <span>Registering Security Profile...</span>
              </span>
            </button>
          </form>

          <!-- Footer Link to Login -->
          <div class="auth-footer">
            <p class="footer-text">
              Already have enterprise access?
              <a routerLink="/login" class="gold-link">Sign In</a>
            </p>
          </div>
        </div>

        <!-- System Architecture Seal -->
        <div class="security-footer-badge">
          <span class="lock-shield-icon">🛡</span>
          <span>Role-Based Access Control &bull; ISO Compliance &bull; Audit Trail</span>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .auth-page {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      width: 100vw;
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background-color: var(--ong-midnight);
      background-image:
        radial-gradient(circle at 15% 20%, rgba(22, 82, 141, 0.42) 0%, transparent 45%),
        radial-gradient(circle at 85% 80%, rgba(214, 178, 90, 0.18) 0%, transparent 40%),
        radial-gradient(circle at 50% 50%, rgba(12, 33, 64, 0.9) 0%, transparent 75%);
      overflow-y: auto;
      padding: 24px;
      z-index: 1000;
    }

    .ambient-glow {
      position: absolute;
      border-radius: 50%;
      filter: blur(80px);
      pointer-events: none;
      z-index: 0;
    }
    .orb-blue {
      width: 440px;
      height: 440px;
      background: radial-gradient(circle, rgba(38, 116, 184, 0.28) 0%, transparent 70%);
      top: 5%;
      left: 15%;
    }
    .orb-gold {
      width: 380px;
      height: 380px;
      background: radial-gradient(circle, rgba(214, 178, 90, 0.18) 0%, transparent 70%);
      bottom: 5%;
      right: 15%;
    }

    .auth-card-container {
      position: relative;
      z-index: 1;
      width: 100%;
      max-width: 520px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 16px;
      animation: fadeInCard 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      margin: auto;
    }

    @keyframes fadeInCard {
      from {
        opacity: 0;
        transform: translateY(18px) scale(0.98);
      }
      to {
        opacity: 1;
        transform: translateY(0) scale(1);
      }
    }

    .glass-neu-card {
      width: 100%;
      background: linear-gradient(155deg, rgba(16, 44, 82, 0.72) 0%, rgba(7, 20, 38, 0.88) 100%);
      backdrop-filter: blur(32px) saturate(200%);
      -webkit-backdrop-filter: blur(32px) saturate(200%);
      border-radius: var(--radius-xl);
      border: 1px solid rgba(255, 255, 255, 0.15);
      box-shadow:
        18px 28px 60px rgba(1, 4, 10, 0.88),
        -12px -12px 36px rgba(38, 116, 184, 0.15),
        inset 1px 1.5px 2px rgba(255, 255, 255, 0.3),
        inset -1.5px -1.5px 3px rgba(0, 0, 0, 0.6);
      padding: 34px 34px 28px 34px;
    }

    .auth-header {
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-bottom: 20px;
    }

    .brand-badge-ring {
      width: 56px;
      height: 56px;
      border-radius: 16px;
      padding: 3px;
      background: linear-gradient(135deg, rgba(214, 178, 90, 0.8) 0%, rgba(22, 82, 141, 0.5) 100%);
      box-shadow:
        0 8px 24px rgba(0, 0, 0, 0.5),
        0 0 16px rgba(214, 178, 90, 0.25);
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .brand-logo {
      width: 100%;
      height: 100%;
      object-fit: cover;
      border-radius: 13px;
    }

    .auth-title {
      font-size: 1.45rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: var(--ong-cloud-white);
      margin-bottom: 4px;
    }

    .auth-subtitle {
      font-size: 0.8rem;
      color: var(--ong-slate);
      line-height: 1.35;
      max-width: 360px;
    }

    /* Error Alert */
    .auth-alert {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 11px 15px;
      border-radius: var(--radius-sm);
      margin-bottom: 18px;
      font-size: 0.82rem;
      animation: shake 0.3s ease;
    }

    .error-alert {
      background: rgba(255, 69, 58, 0.12);
      border: 1px solid rgba(255, 69, 58, 0.35);
      color: #FF8077;
    }

    .alert-icon {
      font-size: 1.1rem;
    }

    @keyframes shake {
      0%, 100% { transform: translateX(0); }
      20%, 60% { transform: translateX(-5px); }
      40%, 80% { transform: translateX(5px); }
    }

    /* Form Fields */
    .auth-form {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .form-label {
      font-size: 0.8rem;
      font-weight: 600;
      color: rgba(245, 248, 252, 0.9);
      letter-spacing: 0.02em;
    }

    .password-label-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .strength-label {
      font-size: 0.72rem;
      font-weight: 600;
      letter-spacing: 0.02em;
      transition: color var(--spring-fast);
    }

    .input-well-wrapper {
      position: relative;
      display: flex;
      align-items: center;
    }

    .input-prefix-icon {
      position: absolute;
      left: 14px;
      color: var(--ong-slate);
      font-size: 0.95rem;
      pointer-events: none;
    }

    .neu-input-well {
      width: 100%;
      height: 46px;
      padding: 0 42px 0 40px;
      background: var(--glass-neu-well);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: var(--radius-sm);
      color: var(--ong-cloud-white);
      font-size: 0.88rem;
      font-family: inherit;
      box-shadow: var(--neu-concave-shadow);
      transition: all var(--spring-fast);
      outline: none;
    }

    .neu-input-well:focus {
      border-color: rgba(38, 116, 184, 0.6);
      box-shadow: var(--neu-concave-focus);
    }

    .neu-input-well::placeholder {
      color: rgba(138, 153, 173, 0.55);
    }

    .toggle-visibility-btn {
      position: absolute;
      right: 12px;
      background: transparent;
      border: none;
      color: var(--ong-slate);
      cursor: pointer;
      font-size: 1rem;
      padding: 4px 6px;
      border-radius: 4px;
      transition: color var(--spring-fast);
    }

    .toggle-visibility-btn:hover {
      color: var(--ong-cloud-white);
    }

    /* Strength Meter Bar */
    .strength-meter-row {
      display: flex;
      gap: 6px;
      margin-top: 4px;
    }

    .strength-bar {
      flex: 1;
      height: 4px;
      border-radius: 2px;
      background: rgba(255, 255, 255, 0.08);
      transition: all 0.3s ease;
    }

    /* Role Pill Grid */
    .role-pill-grid {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 8px;
    }

    .role-pill {
      position: relative;
      display: flex;
      flex-direction: column;
      gap: 4px;
      padding: 10px 10px 12px 10px;
      border-radius: var(--radius-sm);
      background: rgba(4, 12, 24, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.08);
      box-shadow: var(--neu-concave-shadow);
      cursor: pointer;
      transition: all var(--spring-fast);
      user-select: none;
    }

    .role-pill:hover {
      background: rgba(22, 82, 141, 0.15);
      border-color: rgba(38, 116, 184, 0.3);
      transform: translateY(-1px);
    }

    .role-pill.selected {
      background: linear-gradient(145deg, rgba(22, 82, 141, 0.35) 0%, rgba(12, 33, 64, 0.6) 100%);
      border-color: var(--ong-guardrail-gold);
      box-shadow:
        0 4px 14px rgba(214, 178, 90, 0.18),
        inset 0 1px 1px rgba(255, 255, 255, 0.2);
    }

    .role-pill-top {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .role-icon {
      font-size: 0.95rem;
    }

    .role-pill-title {
      font-size: 0.76rem;
      font-weight: 600;
      color: var(--ong-cloud-white);
    }

    .role-pill.selected .role-pill-title {
      color: var(--ong-guardrail-gold);
    }

    .role-pill-desc {
      font-size: 0.65rem;
      color: var(--ong-slate);
      line-height: 1.25;
    }

    .role-radio-indicator {
      position: absolute;
      top: 8px;
      right: 8px;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      border: 1.5px solid rgba(138, 153, 173, 0.4);
      transition: all var(--spring-fast);
    }

    .role-pill.selected .role-radio-indicator {
      border-color: var(--ong-guardrail-gold);
      background: var(--ong-guardrail-gold);
      box-shadow: 0 0 6px var(--ong-guardrail-gold);
    }

    /* Tactile Gold Button */
    .gold-cta-button {
      position: relative;
      height: 48px;
      margin-top: 4px;
      border: 1px solid rgba(255, 255, 255, 0.3);
      border-radius: var(--radius-sm);
      background: linear-gradient(135deg, #E2C374 0%, #D6B25A 40%, #B8933D 100%);
      color: #071426;
      font-size: 0.92rem;
      font-weight: 700;
      letter-spacing: -0.01em;
      cursor: pointer;
      box-shadow:
        0 8px 22px rgba(214, 178, 90, 0.35),
        0 2px 6px rgba(0, 0, 0, 0.4),
        inset 0 1.5px 1px rgba(255, 255, 255, 0.6),
        inset 0 -1.5px 2px rgba(0, 0, 0, 0.35);
      transition: all var(--spring-fast);
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .gold-cta-button:hover:not(:disabled) {
      background: linear-gradient(135deg, #ECD188 0%, #DFBD65 40%, #C49E46 100%);
      transform: translateY(-2px);
      box-shadow:
        0 12px 28px rgba(214, 178, 90, 0.48),
        0 3px 8px rgba(0, 0, 0, 0.5),
        inset 0 1.5px 1px rgba(255, 255, 255, 0.8);
    }

    .gold-cta-button:active:not(:disabled) {
      transform: translateY(1px);
      box-shadow:
        0 4px 12px rgba(214, 178, 90, 0.25),
        inset 0 2px 4px rgba(0, 0, 0, 0.4);
    }

    .gold-cta-button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      box-shadow: none;
    }

    .btn-content {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .btn-arrow {
      font-size: 1.1rem;
      transition: transform var(--spring-fast);
    }

    .gold-cta-button:hover .btn-arrow {
      transform: translateX(3px);
    }

    .btn-loading {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 0.88rem;
    }

    .spinner {
      width: 16px;
      height: 16px;
      border: 2px solid rgba(7, 20, 38, 0.3);
      border-top-color: #071426;
      border-radius: 50%;
      animation: spin 0.7s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    /* Footer */
    .auth-footer {
      margin-top: 20px;
      text-align: center;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      padding-top: 16px;
    }

    .footer-text {
      font-size: 0.82rem;
      color: var(--ong-slate);
    }

    .gold-link {
      color: var(--ong-guardrail-gold);
      text-decoration: none;
      font-weight: 600;
      margin-left: 5px;
      transition: color var(--spring-fast);
    }

    .gold-link:hover {
      color: #E8CA7C;
      text-decoration: underline;
    }

    .security-footer-badge {
      display: flex;
      align-items: center;
      gap: 7px;
      font-size: 0.7rem;
      color: rgba(138, 153, 173, 0.65);
      letter-spacing: 0.02em;
    }

    .lock-shield-icon {
      font-size: 0.85rem;
      color: var(--ong-guardrail-gold);
    }

    @media (max-width: 580px) {
      .role-pill-grid {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class SignupComponent {
  fullName = '';
  email = '';
  password = '';
  selectedRole: UserRole = 'campaign_architect';
  showPassword = false;

  isLoading = signal(false);
  errorMessage = signal<string | null>(null);

  readonly roleOptions: RoleOption[] = [
    {
      id: 'brand_guardian',
      title: 'Brand Guardian',
      desc: 'Guardrail policies & validation',
      icon: '🛡'
    },
    {
      id: 'campaign_architect',
      title: 'Architect',
      desc: 'Agent pipelines & canvases',
      icon: '✦'
    },
    {
      id: 'compliance_officer',
      title: 'Compliance',
      desc: 'Deterministic audits & scores',
      icon: '⚖'
    }
  ];

  strengthScore = computed(() => {
    const pwd = this.password;
    if (!pwd) return 0;
    let score = 0;
    if (pwd.length >= 6) score++;
    if (pwd.length >= 10) score++;
    if (/[A-Z]/.test(pwd) && /[a-z]/.test(pwd)) score++;
    if (/[0-9]/.test(pwd) || /[^A-Za-z0-9]/.test(pwd)) score++;
    return score;
  });

  strengthText = computed(() => {
    switch (this.strengthScore()) {
      case 0:
        return 'Password required';
      case 1:
        return 'Weak';
      case 2:
        return 'Moderate';
      case 3:
        return 'Strong';
      case 4:
        return 'Enterprise-Grade';
      default:
        return '';
    }
  });

  strengthColor = computed(() => {
    switch (this.strengthScore()) {
      case 1:
        return '#FF453A';
      case 2:
        return '#D6B25A';
      case 3:
        return '#2674B8';
      case 4:
        return '#30D158';
      default:
        return 'var(--ong-slate)';
    }
  });

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  selectRole(role: UserRole): void {
    this.selectedRole = role;
  }

  isFormValid(): boolean {
    return (
      this.fullName.trim().length >= 2 &&
      this.email.trim().length >= 5 &&
      this.password.length >= 6
    );
  }

  onSubmit(): void {
    if (!this.isFormValid()) return;

    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.authService.register({
      full_name: this.fullName.trim(),
      email: this.email.trim(),
      password: this.password,
      role: this.selectedRole
    }).subscribe({
      next: () => {
        this.isLoading.set(false);
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.isLoading.set(false);
        const detail = err?.error?.detail || 'Registration failed. Please check your information.';
        this.errorMessage.set(detail);
      }
    });
  }
}

import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
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
            <h1 class="auth-title">Agentic Canvas</h1>
            <p class="auth-subtitle">Autonomous Enterprise Orchestration & Brand Compliance</p>
            <div class="auth-tagline">
              <span class="security-dot"></span>
              <span>Enterprise Zero-Trust Authentication</span>
            </div>
          </div>

          <!-- Error Alert Banner -->
          <div *ngIf="errorMessage()" class="auth-alert error-alert">
            <span class="alert-icon">⚠</span>
            <span class="alert-text">{{ errorMessage() }}</span>
          </div>

          <!-- Login Form -->
          <form (ngSubmit)="onSubmit()" class="auth-form" #loginForm="ngForm">
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
                  placeholder="name@oandg.ai"
                  [(ngModel)]="email"
                  required
                  autocomplete="username"
                  [disabled]="isLoading()"
                />
              </div>
            </div>

            <!-- Password Input -->
            <div class="form-group">
              <div class="password-label-row">
                <label for="password" class="form-label">Password</label>
                <span class="helper-note">Encrypted Session</span>
              </div>
              <div class="input-well-wrapper">
                <span class="input-prefix-icon">🔒</span>
                <input
                  id="password"
                  name="password"
                  [type]="showPassword ? 'text' : 'password'"
                  class="neu-input-well"
                  placeholder="Enter your enterprise password"
                  [(ngModel)]="password"
                  required
                  autocomplete="current-password"
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
            </div>

            <!-- 1-Click Demo Fill Pill -->
            <div class="demo-credential-chip" (click)="fillDemoCredentials()" role="button" tabindex="0">
              <div class="demo-chip-left">
                <span class="demo-sparkle">✦</span>
                <div class="demo-info">
                  <span class="demo-title">1-Click Demo Account</span>
                  <span class="demo-email">admin&#64;oandg.ai &bull; Role: Admin</span>
                </div>
              </div>
              <span class="demo-action-badge">Autofill</span>
            </div>

            <!-- Submit Button (Tactile Extruded Gold) -->
            <button
              type="submit"
              class="gold-cta-button"
              [disabled]="isLoading() || !email || !password"
              [class.loading]="isLoading()"
            >
              <span *ngIf="!isLoading()" class="btn-content">
                <span>Authenticate Session</span>
                <span class="btn-arrow">→</span>
              </span>
              <span *ngIf="isLoading()" class="btn-loading">
                <span class="spinner"></span>
                <span>Authorizing Security Credentials...</span>
              </span>
            </button>
          </form>

          <!-- Footer Link to Signup -->
          <div class="auth-footer">
            <p class="footer-text">
              New team member?
              <a routerLink="/signup" class="gold-link">Create Enterprise Account</a>
            </p>
          </div>
        </div>

        <!-- System Architecture Seal -->
        <div class="security-footer-badge">
          <span class="lock-shield-icon">🛡</span>
          <span>Deterministic Brand Guardrails &bull; SHA-256 JWT &bull; ChromaDB RAG</span>
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

    /* Ambient Glow behind the card */
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
      top: 10%;
      left: 20%;
    }
    .orb-gold {
      width: 380px;
      height: 380px;
      background: radial-gradient(circle, rgba(214, 178, 90, 0.18) 0%, transparent 70%);
      bottom: 10%;
      right: 20%;
    }

    .auth-card-container {
      position: relative;
      z-index: 1;
      width: 100%;
      max-width: 460px;
      margin: auto;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 16px;
      animation: fadeInCard 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
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

    /* Glassmorphic Sculpted Card */
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
      padding: 38px 36px 32px 36px;
    }

    /* Header & Brand */
    .auth-header {
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-bottom: 24px;
    }

    .brand-badge-ring {
      width: 64px;
      height: 64px;
      border-radius: 18px;
      padding: 3px;
      background: linear-gradient(135deg, rgba(214, 178, 90, 0.8) 0%, rgba(22, 82, 141, 0.5) 100%);
      box-shadow:
        0 8px 24px rgba(0, 0, 0, 0.5),
        0 0 16px rgba(214, 178, 90, 0.25);
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .brand-logo {
      width: 100%;
      height: 100%;
      object-fit: cover;
      border-radius: 15px;
    }

    .auth-title {
      font-size: 1.55rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: var(--ong-cloud-white);
      margin-bottom: 6px;
    }

    .auth-subtitle {
      font-size: 0.82rem;
      color: var(--ong-slate);
      line-height: 1.4;
      margin-bottom: 12px;
      max-width: 320px;
    }

    .auth-tagline {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      padding: 4px 12px;
      border-radius: var(--radius-pill);
      background: rgba(4, 12, 24, 0.65);
      border: 1px solid rgba(255, 255, 255, 0.08);
      font-size: 0.72rem;
      color: rgba(245, 248, 252, 0.85);
      font-weight: 500;
    }

    .security-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #30D158;
      box-shadow: 0 0 8px #30D158;
    }

    /* Error Alert */
    .auth-alert {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 11px 15px;
      border-radius: var(--radius-sm);
      margin-bottom: 20px;
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
      gap: 18px;
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 7px;
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

    .helper-note {
      font-size: 0.72rem;
      color: var(--ong-slate);
    }

    /* Debossed Concave Well */
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
      height: 48px;
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

    /* 1-Click Demo Fill Chip */
    .demo-credential-chip {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 14px;
      background: linear-gradient(135deg, rgba(214, 178, 90, 0.08) 0%, rgba(22, 82, 141, 0.12) 100%);
      border: 1px solid rgba(214, 178, 90, 0.25);
      border-radius: var(--radius-sm);
      cursor: pointer;
      transition: all var(--spring-fast);
      user-select: none;
    }

    .demo-credential-chip:hover {
      background: linear-gradient(135deg, rgba(214, 178, 90, 0.16) 0%, rgba(22, 82, 141, 0.22) 100%);
      border-color: var(--ong-guardrail-gold);
      transform: translateY(-1px);
      box-shadow: 0 4px 14px rgba(214, 178, 90, 0.15);
    }

    .demo-credential-chip:active {
      transform: translateY(1px);
    }

    .demo-chip-left {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .demo-sparkle {
      color: var(--ong-guardrail-gold);
      font-size: 1.1rem;
    }

    .demo-info {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .demo-title {
      font-size: 0.78rem;
      font-weight: 600;
      color: var(--ong-guardrail-gold);
    }

    .demo-email {
      font-size: 0.72rem;
      color: var(--ong-slate);
      font-family: var(--font-mono);
    }

    .demo-action-badge {
      font-size: 0.68rem;
      font-weight: 600;
      padding: 4px 8px;
      border-radius: 6px;
      background: rgba(214, 178, 90, 0.18);
      color: var(--ong-guardrail-gold);
      border: 1px solid rgba(214, 178, 90, 0.3);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    /* Tactile Extruded Gold CTA Button */
    .gold-cta-button {
      position: relative;
      height: 50px;
      margin-top: 6px;
      border: 1px solid rgba(255, 255, 255, 0.3);
      border-radius: var(--radius-sm);
      background: linear-gradient(135deg, #E2C374 0%, #D6B25A 40%, #B8933D 100%);
      color: #071426;
      font-size: 0.94rem;
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
      margin-top: 24px;
      text-align: center;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      padding-top: 18px;
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

    /* Bottom Seal */
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
  `]
})
export class LoginComponent {
  email = '';
  password = '';
  showPassword = false;
  isLoading = signal(false);
  errorMessage = signal<string | null>(null);

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  fillDemoCredentials(): void {
    this.email = 'admin@oandg.ai';
    this.password = 'AdminPass123!';
    this.errorMessage.set(null);
  }

  onSubmit(): void {
    if (!this.email || !this.password) return;

    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.authService.login({
      email: this.email.trim(),
      password: this.password
    }).subscribe({
      next: () => {
        this.isLoading.set(false);
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.isLoading.set(false);
        const detail = err?.error?.detail || 'Authentication failed. Please check your credentials.';
        this.errorMessage.set(detail);
      }
    });
  }
}

import { Component, signal, HostListener, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterOutlet, RouterLink, RouterLinkActive, Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs';
import { AuthService, UserRole } from './services/auth.service';
import { ApiService, HealthStatus } from './api.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <!-- Clean Full-Screen Auth Layout for /login and /signup -->
    <ng-container *ngIf="isAuthPage(); else fullAppLayout">
      <router-outlet></router-outlet>
    </ng-container>

    <!-- Main Enterprise Layout with Glass Sidebar & Header -->
    <ng-template #fullAppLayout>
      <div class="app-layout">
        <!-- Apple Glass Sidebar -->
        <aside class="app-sidebar" [class.open]="sidebarOpen">
          <div class="sidebar-brand">
            <img src="assets/logo-icon.png" alt="Agentic Canvas Logo" />
            <div class="sidebar-brand-text">
              <span class="sidebar-brand-name">Agentic Canvas</span>
              <span class="sidebar-brand-desc">Enterprise Platform</span>
            </div>
          </div>

          <nav class="sidebar-nav">
            <a class="sidebar-nav-item" routerLink="/dashboard" routerLinkActive="active" (click)="sidebarOpen = false">
              <span class="nav-icon">◈</span>
              <span>Command Center</span>
            </a>
            <a class="sidebar-nav-item" routerLink="/campaigns/new" routerLinkActive="active" (click)="sidebarOpen = false">
              <span class="nav-icon">✦</span>
              <span>New Campaign</span>
            </a>
            <a class="sidebar-nav-item" routerLink="/brand-rules" routerLinkActive="active" (click)="sidebarOpen = false">
              <span class="nav-icon">⬡</span>
              <span>Brand Guardrails</span>
            </a>
          </nav>

          <div class="sidebar-footer">
            <div class="system-status-pill" (click)="openEngineModal($event)" style="cursor: pointer;" title="Click to view Engine Details">
              <span class="status-indicator"></span>
              <span>Autonomous Engine 1.0</span>
            </div>
          </div>
        </aside>

        <!-- Main Content Area -->
        <main class="app-main">
          <header class="app-header">
            <button class="mobile-menu" (click)="sidebarOpen = !sidebarOpen" aria-label="Toggle navigation">☰</button>
            
            <div class="header-left">
              <div class="header-breadcrumbs">
                <span class="breadcrumb-item">Platform</span>
                <span class="breadcrumb-separator">/</span>
                <span class="breadcrumb-active">Agentic Canvas</span>
              </div>

              <!-- Interactive Engine Status Pill on Left Side -->
              <button
                type="button"
                id="engine-live-btn"
                class="engine-badge-btn"
                (click)="openEngineModal($event)"
                title="Click to view Engine Details and Architecture"
              >
                <span class="engine-pulsing-dot"></span>
                <span class="engine-badge-text">ENGINE LIVE</span>
                <span class="engine-badge-tag">v1.0</span>
              </button>
            </div>

            <div class="header-actions">
              <!-- User Profile Chip & Dropdown on Right Side -->
              <div *ngIf="authService.isAuthenticated()" class="user-profile-wrapper">
                <button
                  type="button"
                  id="user-profile-btn"
                  class="user-profile-chip"
                  (click)="toggleProfileDropdown($event)"
                  [class.active]="profileDropdownOpen"
                  aria-label="User Profile Menu"
                >
                  <div class="user-avatar-initials">
                    {{ authService.userInitials() }}
                  </div>
                  <div class="user-meta-col">
                    <span class="user-name-text">{{ authService.userName() }}</span>
                    <span class="user-role-badge" [attr.data-role]="authService.userRole()">
                      {{ authService.userRoleLabel() }}
                    </span>
                  </div>
                  <span class="dropdown-chevron" [class.rotated]="profileDropdownOpen">▾</span>
                </button>

                <!-- Glassmorphic Dropdown Panel -->
                <div *ngIf="profileDropdownOpen" class="profile-dropdown-glass">
                  <div class="dropdown-user-info">
                    <div class="dropdown-avatar">{{ authService.userInitials() }}</div>
                    <div class="dropdown-text">
                      <span class="dropdown-name">{{ authService.userName() }}</span>
                      <span class="dropdown-email">{{ authService.userEmail() }}</span>
                    </div>
                  </div>

                  <div class="dropdown-role-tag">
                    <span class="role-dot"></span>
                    <span>{{ authService.userRoleLabel() }}</span>
                  </div>

                  <!-- Quick Account Summary -->
                  <div class="dropdown-meta-card">
                    <div class="meta-card-row">
                      <span class="meta-card-label">User ID</span>
                      <span class="meta-card-val font-mono">{{ (authService.currentUser()?.id || 'AC-SYS') | slice:0:8 }}...</span>
                    </div>
                    <div class="meta-card-row">
                      <span class="meta-card-label">Tier</span>
                      <span class="meta-card-val text-gold">Enterprise Autonomous</span>
                    </div>
                  </div>

                  <!-- Edit Account Details Action -->
                  <button
                    type="button"
                    id="edit-account-btn"
                    class="account-action-btn"
                    (click)="openAccountModal($event)"
                  >
                    <span class="action-icon">⚙</span>
                    <span>Edit Account Details</span>
                  </button>

                  <div class="dropdown-divider"></div>

                  <button type="button" class="sign-out-btn" (click)="onSignOut()">
                    <span class="sign-out-icon">⎋</span>
                    <span>Sign Out</span>
                  </button>
                </div>
              </div>
            </div>
          </header>

          <div class="app-content">
            <router-outlet></router-outlet>
          </div>
        </main>
      </div>

      <!-- ═══════════════════════════════════════════════════════════════════
           ENGINE DETAILS MODAL
           ═══════════════════════════════════════════════════════════════════ -->
      <div *ngIf="engineModalOpen" class="modal-backdrop-glass" (click)="closeEngineModal()">
        <div class="modal-dialog-glass engine-modal-dialog" (click)="$event.stopPropagation()">
          <div class="modal-glass-header">
            <div class="modal-title-wrap">
              <div class="engine-live-header-pill">
                <span class="engine-pulsing-dot"></span>
                <span>SYSTEM ONLINE & HEALTHY</span>
              </div>
              <h2 class="modal-glass-title">Agentic Canvas Autonomous Engine 1.0</h2>
              <p class="modal-glass-desc">Multi-Agent Orchestration & Compliance Runtime Architecture</p>
            </div>
            <button type="button" class="modal-close-btn" (click)="closeEngineModal()" aria-label="Close Engine Details">✕</button>
          </div>

          <div class="modal-glass-body">
            <!-- Grid: Health + LLM Architecture -->
            <div class="engine-grid">
              <!-- Card 1: Live Runtime -->
              <div class="engine-detail-card">
                <div class="detail-card-header">
                  <span class="detail-card-icon">⚡</span>
                  <span class="detail-card-title">Live Backend & Services</span>
                  <span class="badge badge-approved" style="margin-left: auto;">
                    {{ engineHealth()?.status === 'healthy' ? 'HEALTHY' : 'CONNECTED' }}
                  </span>
                </div>
                <div class="detail-card-rows">
                  <div class="detail-row">
                    <span class="detail-label">API Gateway:</span>
                    <span class="detail-val font-mono">http://localhost:8000/api</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Database:</span>
                    <span class="detail-val text-success font-mono">
                      PostgreSQL {{ engineHealth()?.database === 'connected' ? '(Active)' : '' }}
                    </span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Environment:</span>
                    <span class="detail-val text-cyan font-mono">{{ engineHealth()?.environment || 'development' | uppercase }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Round-Trip Latency:</span>
                    <span class="detail-val font-mono">
                      <span *ngIf="engineHealthLoading()" class="spinner-tiny"></span>
                      <span *ngIf="!engineHealthLoading() && engineLatencyMs() !== null" class="text-gold font-bold">
                        {{ engineLatencyMs() }} ms
                      </span>
                      <span *ngIf="!engineHealthLoading() && engineLatencyMs() === null">Measured on ping</span>
                    </span>
                  </div>
                </div>
                <button
                  type="button"
                  class="btn btn-secondary btn-sm"
                  style="margin-top: 10px; width: 100%; justify-content: center;"
                  (click)="pingEngine()"
                  [disabled]="engineHealthLoading()"
                >
                  <span *ngIf="!engineHealthLoading()">⚡ Test Live Latency Ping</span>
                  <span *ngIf="engineHealthLoading()">Measuring ping...</span>
                </button>
              </div>

              <!-- Card 2: Resilient LLM Engine -->
              <div class="engine-detail-card">
                <div class="detail-card-header">
                  <span class="detail-card-icon">🧠</span>
                  <span class="detail-card-title">LLM Fabric & Failover</span>
                  <span class="badge badge-approved" style="margin-left: auto;">FAILOVER ACTIVE</span>
                </div>
                <div class="detail-card-rows">
                  <div class="detail-row">
                    <span class="detail-label">Primary LLM:</span>
                    <span class="detail-val font-mono text-gold font-bold">gemini-2.5-flash</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Auto-Failover:</span>
                    <span class="detail-val font-mono text-cyan">gemini-flash-latest, 2.5-lite</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">503 Recovery:</span>
                    <span class="detail-val text-success">Exponential Backoff + Jitter</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Outage Protection:</span>
                    <span class="detail-val text-gold">Continuity Fallback Generator</span>
                  </div>
                </div>
                <div class="detail-tag-note">
                  Protected against transient spikes in demand & model capacity errors.
                </div>
              </div>
            </div>

            <!-- Agent Fleet Section -->
            <div class="agent-fleet-container">
              <h3 class="fleet-section-title">Active Multi-Agent Pipeline</h3>
              <div class="fleet-pills-wrap">
                <div class="fleet-agent-item">
                  <div class="fleet-agent-dot ready"></div>
                  <div class="fleet-agent-meta">
                    <span class="fleet-agent-name">1. Copywriter Agent</span>
                    <span class="fleet-agent-desc">Brief analysis & tone compliance</span>
                  </div>
                  <span class="fleet-agent-version">v1.0</span>
                </div>
                <div class="fleet-agent-item">
                  <div class="fleet-agent-dot ready"></div>
                  <div class="fleet-agent-meta">
                    <span class="fleet-agent-name">2. Layout Structurer</span>
                    <span class="fleet-agent-desc">Semantic hierarchy & color palettes</span>
                  </div>
                  <span class="fleet-agent-version">v1.0</span>
                </div>
                <div class="fleet-agent-item">
                  <div class="fleet-agent-dot ready"></div>
                  <div class="fleet-agent-meta">
                    <span class="fleet-agent-name">3. Asset Recommender</span>
                    <span class="fleet-agent-desc">Visual directives & aspect ratios</span>
                  </div>
                  <span class="fleet-agent-version">v1.0</span>
                </div>
                <div class="fleet-agent-item">
                  <div class="fleet-agent-dot gold"></div>
                  <div class="fleet-agent-meta">
                    <span class="fleet-agent-name">4. Guardrail Evaluator</span>
                    <span class="fleet-agent-desc">Deterministic & semantic scoring</span>
                  </div>
                  <span class="fleet-agent-version">v1.0</span>
                </div>
                <div class="fleet-agent-item">
                  <div class="fleet-agent-dot gold"></div>
                  <div class="fleet-agent-meta">
                    <span class="fleet-agent-name">5. Repair Agent</span>
                    <span class="fleet-agent-desc">Autonomous violation remediation</span>
                  </div>
                  <span class="fleet-agent-version">v1.0</span>
                </div>
              </div>
            </div>

            <!-- Parameters Grid -->
            <div class="engine-params-row">
              <div class="param-box">
                <span class="param-title">Pass Threshold</span>
                <span class="param-stat text-gold">75.0%</span>
              </div>
              <div class="param-box">
                <span class="param-title">Max Repair Loops</span>
                <span class="param-stat">3 Iterations</span>
              </div>
              <div class="param-box">
                <span class="param-title">Agent Retry Policy</span>
                <span class="param-stat">3 Retries (Backoff)</span>
              </div>
              <div class="param-box">
                <span class="param-title">Vector Collection</span>
                <span class="param-stat text-cyan">ong_brand_rules</span>
              </div>
            </div>
          </div>

          <div class="modal-glass-footer">
            <span class="footer-hint">Operating within enterprise brand-safety boundaries</span>
            <button type="button" class="btn btn-secondary" (click)="closeEngineModal()">Close</button>
          </div>
        </div>
      </div>

      <!-- ═══════════════════════════════════════════════════════════════════
           EDIT ACCOUNT DETAILS MODAL
           ═══════════════════════════════════════════════════════════════════ -->
      <div *ngIf="accountModalOpen" class="modal-backdrop-glass" (click)="closeAccountModal()">
        <div class="modal-dialog-glass account-modal-dialog" (click)="$event.stopPropagation()">
          <div class="modal-glass-header">
            <div class="modal-title-wrap">
              <h2 class="modal-glass-title">Edit Account Details</h2>
              <p class="modal-glass-desc">Update your enterprise profile credentials and permissions</p>
            </div>
            <button type="button" class="modal-close-btn" (click)="closeAccountModal()" aria-label="Close Account Modal">✕</button>
          </div>

          <form (ngSubmit)="saveAccountDetails()" class="modal-glass-form">
            <div *ngIf="accountError()" class="alert-box error">
              <span>⚠ {{ accountError() }}</span>
            </div>

            <div *ngIf="accountSuccess()" class="alert-box success">
              <span>✓ Account details saved successfully!</span>
            </div>

            <div class="form-field">
              <label class="field-label" for="edit-full-name">Full Name</label>
              <input
                id="edit-full-name"
                name="full_name"
                type="text"
                class="field-input"
                [(ngModel)]="editForm.full_name"
                required
                placeholder="e.g. Agentic Canvas Enterprise Admin"
              />
            </div>

            <div class="form-field">
              <label class="field-label" for="edit-email">Enterprise Email Address</label>
              <input
                id="edit-email"
                name="email"
                type="email"
                class="field-input"
                [(ngModel)]="editForm.email"
                required
                placeholder="e.g. admin@oandg.ai"
              />
            </div>

            <div class="form-field">
              <label class="field-label" for="edit-role">Enterprise Role</label>
              <select
                id="edit-role"
                name="role"
                class="field-input field-select"
                [(ngModel)]="editForm.role"
              >
                <option value="admin">System Administrator (Full Control)</option>
                <option value="brand_guardian">Brand Guardian (Brand Rules & Governance)</option>
                <option value="campaign_architect">Campaign Architect (Campaign Pipelines)</option>
                <option value="compliance_officer">Compliance Officer (Audit & Safety)</option>
              </select>
            </div>

            <div class="form-field">
              <label class="field-label" for="edit-password">
                New Password <span class="field-sub">(leave blank to keep current)</span>
              </label>
              <input
                id="edit-password"
                name="password"
                type="password"
                class="field-input"
                [(ngModel)]="editForm.password"
                placeholder="Min 6 characters"
              />
            </div>

            <div class="modal-glass-footer" style="margin-top: 1.25rem; padding-top: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.08);">
              <button type="button" class="btn btn-secondary" (click)="closeAccountModal()" [disabled]="savingAccount()">Cancel</button>
              <button type="submit" id="save-account-btn" class="btn btn-primary" [disabled]="savingAccount()">
                <span *ngIf="!savingAccount()">Save Changes</span>
                <span *ngIf="savingAccount()" style="display: flex; align-items: center; gap: 8px;">
                  <span class="spinner-tiny"></span> Saving...
                </span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </ng-template>
  `,
  styles: [`
    .sidebar-footer {
      margin-top: auto;
      padding: 16px 18px 22px 18px;
      border-top: 1px solid var(--glass-border);
    }
    .system-status-pill {
      display: flex;
      align-items: center;
      gap: 9px;
      padding: 9px 14px;
      border-radius: var(--radius-pill);
      background: var(--glass-neu-well);
      box-shadow: var(--neu-concave-shadow);
      border: 1px solid rgba(255, 255, 255, 0.06);
      font-size: 0.74rem;
      color: var(--ong-slate);
      font-weight: 500;
      transition: all var(--spring-fast);
    }
    .system-status-pill:hover {
      border-color: rgba(48, 209, 88, 0.4);
      box-shadow: 0 0 12px rgba(48, 209, 88, 0.2);
    }
    .status-indicator {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #30D158;
      box-shadow: 0 0 8px #30D158, inset 0 1px 1px #FFF;
    }
    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;
      flex-wrap: nowrap;
    }
    .header-breadcrumbs {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.85rem;
    }
    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-left: auto;
      flex-wrap: nowrap;
    }
    .breadcrumb-item {
      color: var(--ong-slate);
      font-weight: 500;
    }
    .breadcrumb-separator {
      color: rgba(138, 153, 173, 0.4);
      font-size: 0.75rem;
    }
    .breadcrumb-active {
      color: var(--ong-cloud-white);
      font-weight: 600;
    }
    .mobile-menu {
      display: none;
      background: var(--glass-neu-surface);
      border: 1px solid var(--glass-border);
      box-shadow: var(--neu-convex-shadow);
      color: var(--ong-cloud-white);
      font-size: 1.25rem;
      cursor: pointer;
      padding: 6px 12px;
      border-radius: var(--radius-sm);
      transition: all var(--spring-fast);
    }
    .mobile-menu:hover {
      background: var(--glass-neu-surface-hover);
      box-shadow: var(--neu-convex-shadow-hover);
    }
    .mobile-menu:active {
      box-shadow: var(--neu-concave-shadow);
      transform: translateY(1px);
    }

    /* Interactive Engine Badge Button */
    .engine-badge-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      border-radius: var(--radius-pill);
      background: linear-gradient(145deg, rgba(48, 209, 88, 0.12) 0%, rgba(12, 33, 64, 0.7) 100%);
      border: 1px solid rgba(48, 209, 88, 0.38);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.15);
      cursor: pointer;
      color: #30D158;
      font-family: var(--font-family);
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.05em;
      transition: all var(--spring-fast);
      outline: none;
    }
    .engine-badge-btn:hover {
      background: linear-gradient(145deg, rgba(48, 209, 88, 0.22) 0%, rgba(16, 44, 82, 0.85) 100%);
      border-color: #30D158;
      box-shadow: 0 0 18px rgba(48, 209, 88, 0.35), inset 0 1px 1px rgba(255, 255, 255, 0.3);
      transform: translateY(-1px);
    }
    .engine-badge-btn:active {
      transform: translateY(1px);
    }
    .engine-pulsing-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #30D158;
      box-shadow: 0 0 8px #30D158;
      animation: pulseGreen 2s infinite cubic-bezier(0.4, 0, 0.6, 1);
    }
    @keyframes pulseGreen {
      0%, 100% { opacity: 1; transform: scale(1); box-shadow: 0 0 8px #30D158; }
      50% { opacity: 0.5; transform: scale(0.85); box-shadow: 0 0 3px #30D158; }
    }
    .engine-badge-text {
      color: #30D158;
    }
    .engine-badge-tag {
      font-size: 0.62rem;
      padding: 2px 6px;
      border-radius: 4px;
      background: rgba(48, 209, 88, 0.2);
      color: #7BF299;
      font-weight: 600;
    }

    /* User Profile Chip & Dropdown */
    .user-profile-wrapper {
      position: relative;
    }

    .user-profile-chip {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 5px 12px 5px 6px;
      border-radius: var(--radius-pill);
      background: var(--glass-neu-surface);
      border: 1px solid rgba(255, 255, 255, 0.12);
      box-shadow: var(--neu-convex-sm);
      cursor: pointer;
      transition: all var(--spring-fast);
      color: var(--ong-cloud-white);
      outline: none;
    }

    .user-profile-chip:hover,
    .user-profile-chip.active {
      background: var(--glass-neu-surface-hover);
      border-color: rgba(214, 178, 90, 0.4);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
    }

    .user-avatar-initials {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: linear-gradient(135deg, #16528D 0%, #D6B25A 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.74rem;
      font-weight: 700;
      color: #FFF;
      box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.4);
    }

    .user-meta-col {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      text-align: left;
      gap: 1px;
    }

    .user-name-text {
      font-size: 0.78rem;
      font-weight: 600;
      color: var(--ong-cloud-white);
      white-space: nowrap;
      max-width: 140px;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .user-role-badge {
      font-size: 0.65rem;
      font-weight: 500;
      color: var(--ong-guardrail-gold);
      line-height: 1;
    }

    .dropdown-chevron {
      font-size: 0.8rem;
      color: var(--ong-slate);
      transition: transform var(--spring-fast);
    }

    .dropdown-chevron.rotated {
      transform: rotate(180deg);
    }

    /* Glass Dropdown Panel */
    .profile-dropdown-glass {
      position: absolute;
      top: calc(100% + 8px);
      right: 0;
      width: 260px;
      background: linear-gradient(155deg, rgba(16, 44, 82, 0.94) 0%, rgba(7, 20, 38, 0.98) 100%);
      backdrop-filter: blur(28px) saturate(200%);
      -webkit-backdrop-filter: blur(28px) saturate(200%);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: var(--radius-md);
      box-shadow:
        0 14px 34px rgba(0, 0, 0, 0.75),
        inset 1px 1px 1.5px rgba(255, 255, 255, 0.2);
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      z-index: 100;
      animation: fadeInDropdown 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes fadeInDropdown {
      from { opacity: 0; transform: translateY(-6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .dropdown-user-info {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .dropdown-avatar {
      width: 38px;
      height: 38px;
      border-radius: 50%;
      background: linear-gradient(135deg, #16528D 0%, #D6B25A 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.84rem;
      font-weight: 700;
      color: #FFF;
      flex-shrink: 0;
    }

    .dropdown-text {
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .dropdown-name {
      font-size: 0.84rem;
      font-weight: 600;
      color: var(--ong-cloud-white);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .dropdown-email {
      font-size: 0.7rem;
      color: var(--ong-slate);
      font-family: var(--font-mono);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .dropdown-role-tag {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 4px 8px;
      border-radius: 6px;
      background: rgba(4, 12, 24, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.06);
      font-size: 0.68rem;
      color: var(--ong-guardrail-gold);
      font-weight: 500;
    }

    .role-dot {
      width: 5px;
      height: 5px;
      border-radius: 50%;
      background: var(--ong-guardrail-gold);
      box-shadow: 0 0 6px var(--ong-guardrail-gold);
    }

    .dropdown-meta-card {
      background: var(--glass-neu-well);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: var(--radius-sm);
      padding: 8px 10px;
      display: flex;
      flex-direction: column;
      gap: 5px;
      font-size: 0.72rem;
    }
    .meta-card-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .meta-card-label {
      color: var(--ong-slate);
    }
    .meta-card-val {
      color: var(--ong-cloud-white);
      font-weight: 500;
    }

    .account-action-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: var(--radius-sm);
      background: linear-gradient(135deg, rgba(22, 82, 141, 0.25) 0%, rgba(38, 116, 184, 0.15) 100%);
      border: 1px solid rgba(38, 116, 184, 0.35);
      color: #92C5F2;
      font-size: 0.78rem;
      font-weight: 600;
      cursor: pointer;
      transition: all var(--spring-fast);
      width: 100%;
      outline: none;
    }
    .account-action-btn:hover {
      background: linear-gradient(135deg, rgba(22, 82, 141, 0.45) 0%, rgba(38, 116, 184, 0.3) 100%);
      border-color: var(--ong-secure-azure);
      color: #FFF;
      transform: translateY(-1px);
    }
    .action-icon {
      font-size: 0.9rem;
    }

    .dropdown-divider {
      height: 1px;
      background: rgba(255, 255, 255, 0.08);
      margin: 2px 0;
    }

    .sign-out-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: var(--radius-sm);
      background: rgba(255, 69, 58, 0.12);
      border: 1px solid rgba(255, 69, 58, 0.25);
      color: #FF8077;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      transition: all var(--spring-fast);
      width: 100%;
    }

    .sign-out-btn:hover {
      background: rgba(255, 69, 58, 0.22);
      border-color: #FF453A;
      color: #FFF;
      transform: translateY(-1px);
    }

    .sign-out-icon {
      font-size: 0.95rem;
    }

    /* ═══════════════════════════════════════════════════════════════════
       MODALS SHARED GLASS ARCHITECTURE
       ═══════════════════════════════════════════════════════════════════ */
    .modal-backdrop-glass {
      position: fixed;
      inset: 0;
      background: rgba(2, 6, 14, 0.75);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      z-index: 999;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
      animation: fadeInBackdrop 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes fadeInBackdrop {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    .modal-dialog-glass {
      background: linear-gradient(155deg, rgba(16, 44, 82, 0.94) 0%, rgba(7, 20, 38, 0.98) 100%);
      backdrop-filter: blur(36px) saturate(210%);
      -webkit-backdrop-filter: blur(36px) saturate(210%);
      border: 1px solid rgba(255, 255, 255, 0.16);
      border-radius: var(--radius-lg);
      box-shadow:
        0 24px 60px rgba(0, 0, 0, 0.85),
        0 0 1px rgba(255, 255, 255, 0.3),
        inset 1px 1px 2px rgba(255, 255, 255, 0.2);
      width: 100%;
      max-height: 90vh;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      animation: scaleUpModal 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes scaleUpModal {
      from { opacity: 0; transform: scale(0.95) translateY(10px); }
      to { opacity: 1; transform: scale(1) translateY(0); }
    }

    .engine-modal-dialog {
      max-width: 680px;
    }
    .account-modal-dialog {
      max-width: 480px;
    }

    .modal-glass-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      padding: 20px 24px 16px 24px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .modal-title-wrap {
      display: flex;
      flex-direction: column;
      gap: 3px;
    }
    .modal-glass-title {
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--ong-cloud-white);
      margin: 0;
      letter-spacing: -0.02em;
    }
    .modal-glass-desc {
      font-size: 0.78rem;
      color: var(--ong-slate);
      margin: 0;
    }

    .modal-close-btn {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: var(--ong-slate);
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.85rem;
      cursor: pointer;
      transition: all var(--spring-fast);
    }
    .modal-close-btn:hover {
      background: rgba(255, 255, 255, 0.14);
      color: #FFF;
      border-color: rgba(255, 255, 255, 0.25);
    }

    .modal-glass-body {
      padding: 20px 24px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }

    .modal-glass-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 24px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      background: rgba(4, 12, 24, 0.4);
    }

    /* Engine Details Elements */
    .engine-live-header-pill {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      padding: 3px 10px;
      border-radius: var(--radius-pill);
      background: rgba(48, 209, 88, 0.12);
      border: 1px solid rgba(48, 209, 88, 0.3);
      color: #30D158;
      font-size: 0.65rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      margin-bottom: 4px;
      width: fit-content;
    }

    .engine-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }

    .engine-detail-card {
      background: var(--glass-neu-well);
      box-shadow: var(--neu-concave-shadow);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: var(--radius-md);
      padding: 14px 16px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .detail-card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      padding-bottom: 6px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }
    .detail-card-icon {
      font-size: 1rem;
    }
    .detail-card-title {
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--ong-cloud-white);
    }
    .detail-card-rows {
      display: flex;
      flex-direction: column;
      gap: 6px;
      font-size: 0.74rem;
    }
    .detail-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .detail-label {
      color: var(--ong-slate);
    }
    .detail-val {
      color: var(--ong-cloud-white);
    }
    .detail-tag-note {
      margin-top: 6px;
      font-size: 0.68rem;
      color: var(--ong-slate);
      font-style: italic;
      line-height: 1.4;
    }

    .agent-fleet-container {
      background: rgba(12, 33, 64, 0.35);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: var(--radius-md);
      padding: 14px 16px;
    }
    .fleet-section-title {
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--ong-cloud-white);
      margin: 0 0 10px 0;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .fleet-pills-wrap {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
      gap: 8px;
    }
    .fleet-agent-item {
      display: flex;
      align-items: center;
      gap: 9px;
      padding: 7px 10px;
      border-radius: var(--radius-sm);
      background: var(--glass-neu-well);
      border: 1px solid rgba(255, 255, 255, 0.06);
    }
    .fleet-agent-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      flex-shrink: 0;
    }
    .fleet-agent-dot.ready {
      background: #30D158;
      box-shadow: 0 0 6px #30D158;
    }
    .fleet-agent-dot.gold {
      background: var(--ong-guardrail-gold);
      box-shadow: 0 0 6px var(--ong-guardrail-gold);
    }
    .fleet-agent-meta {
      display: flex;
      flex-direction: column;
      overflow: hidden;
      flex: 1;
    }
    .fleet-agent-name {
      font-size: 0.74rem;
      font-weight: 600;
      color: var(--ong-cloud-white);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .fleet-agent-desc {
      font-size: 0.64rem;
      color: var(--ong-slate);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .fleet-agent-version {
      font-size: 0.62rem;
      font-family: var(--font-mono);
      color: var(--ong-slate);
      padding: 1px 4px;
      background: rgba(255, 255, 255, 0.06);
      border-radius: 4px;
    }

    .engine-params-row {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
    }
    .param-box {
      background: var(--glass-neu-well);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: var(--radius-sm);
      padding: 8px 12px;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }
    .param-title {
      font-size: 0.65rem;
      color: var(--ong-slate);
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }
    .param-stat {
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--ong-cloud-white);
    }

    .footer-hint {
      font-size: 0.72rem;
      color: var(--ong-slate);
    }

    /* Form in Edit Account Modal */
    .modal-glass-form {
      padding: 18px 24px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .form-field {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .field-label {
      font-size: 0.78rem;
      font-weight: 600;
      color: var(--ong-cloud-white);
    }
    .field-sub {
      font-size: 0.7rem;
      font-weight: 400;
      color: var(--ong-slate);
    }
    .field-input {
      padding: 10px 14px;
      border-radius: var(--radius-sm);
      background: var(--glass-neu-well);
      box-shadow: var(--neu-concave-shadow);
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: var(--ong-cloud-white);
      font-size: 0.85rem;
      font-family: inherit;
      outline: none;
      transition: all var(--spring-fast);
    }
    .field-input:focus {
      border-color: var(--ong-guardrail-gold);
      box-shadow: var(--neu-concave-focus);
    }
    .field-select {
      cursor: pointer;
    }
    .field-select option {
      background: #0C2140;
      color: #FFF;
    }

    .alert-box {
      padding: 9px 12px;
      border-radius: var(--radius-sm);
      font-size: 0.76rem;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .alert-box.error {
      background: rgba(255, 69, 58, 0.15);
      border: 1px solid rgba(255, 69, 58, 0.35);
      color: #FF8077;
    }
    .alert-box.success {
      background: rgba(48, 209, 88, 0.15);
      border: 1px solid rgba(48, 209, 88, 0.35);
      color: #7BF299;
    }

    .spinner-tiny {
      display: inline-block;
      width: 12px;
      height: 12px;
      border: 2px solid rgba(255, 255, 255, 0.2);
      border-top-color: #FFF;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    /* Helper text colors */
    .text-success { color: #30D158; }
    .text-gold { color: var(--ong-guardrail-gold); }
    .text-cyan { color: #64D2FF; }
    .font-mono { font-family: var(--font-mono); }
    .font-bold { font-weight: 700; }

    @media (max-width: 1024px) {
      .mobile-menu { display: block; }
      .engine-grid { grid-template-columns: 1fr; }
      .engine-params-row { grid-template-columns: 1fr 1fr; }
    }
  `]
})
export class AppComponent {
  sidebarOpen = false;
  profileDropdownOpen = false;
  isAuthPage = signal(false);

  // Engine Modal State
  engineModalOpen = false;
  engineHealth = signal<HealthStatus | null>(null);
  engineHealthLoading = signal<boolean>(false);
  engineLatencyMs = signal<number | null>(null);

  // Account Modal State
  accountModalOpen = false;
  savingAccount = signal<boolean>(false);
  accountError = signal<string | null>(null);
  accountSuccess = signal<boolean>(false);
  editForm = {
    full_name: '',
    email: '',
    role: 'campaign_architect' as UserRole,
    password: ''
  };

  constructor(
    public authService: AuthService,
    private apiService: ApiService,
    private router: Router,
    private elementRef: ElementRef
  ) {
    // Determine if initial route is auth page
    const initialUrl = window.location.pathname;
    this.isAuthPage.set(initialUrl.startsWith('/login') || initialUrl.startsWith('/signup'));

    // Subscribe to navigation events
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      const url = event.urlAfterRedirects || event.url;
      this.isAuthPage.set(url.startsWith('/login') || url.startsWith('/signup'));
      this.profileDropdownOpen = false;
      this.sidebarOpen = false;
    });
  }

  toggleProfileDropdown(event: Event): void {
    event.stopPropagation();
    this.profileDropdownOpen = !this.profileDropdownOpen;
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    if (!this.elementRef.nativeElement.contains(event.target)) {
      this.profileDropdownOpen = false;
    }
  }

  onSignOut(): void {
    this.profileDropdownOpen = false;
    this.authService.logout(true);
  }

  // ─── Engine Details Methods ──────────────────────────────────────────
  openEngineModal(event: Event): void {
    event.stopPropagation();
    this.engineModalOpen = true;
    this.profileDropdownOpen = false;
    this.pingEngine();
  }

  closeEngineModal(): void {
    this.engineModalOpen = false;
  }

  pingEngine(): void {
    this.engineHealthLoading.set(true);
    const start = performance.now();
    this.apiService.getHealth().subscribe({
      next: (status) => {
        const latency = Math.round(performance.now() - start);
        this.engineHealth.set(status);
        this.engineLatencyMs.set(latency);
        this.engineHealthLoading.set(false);
      },
      error: () => {
        this.engineHealthLoading.set(false);
        this.engineLatencyMs.set(null);
      }
    });
  }

  // ─── Account Edit Methods ──────────────────────────────────────────
  openAccountModal(event: Event): void {
    event.stopPropagation();
    this.profileDropdownOpen = false;
    const user = this.authService.currentUser();
    this.editForm = {
      full_name: user?.full_name || '',
      email: user?.email || '',
      role: user?.role || 'campaign_architect',
      password: ''
    };
    this.accountError.set(null);
    this.accountSuccess.set(false);
    this.accountModalOpen = true;
  }

  closeAccountModal(): void {
    this.accountModalOpen = false;
    this.accountError.set(null);
    this.accountSuccess.set(false);
  }

  saveAccountDetails(): void {
    if (!this.editForm.full_name.trim()) {
      this.accountError.set('Full name is required');
      return;
    }
    if (!this.editForm.email.trim()) {
      this.accountError.set('Email is required');
      return;
    }

    this.savingAccount.set(true);
    this.accountError.set(null);
    this.accountSuccess.set(false);

    const payload: { full_name: string; email: string; role: UserRole; password?: string } = {
      full_name: this.editForm.full_name.trim(),
      email: this.editForm.email.trim(),
      role: this.editForm.role
    };

    if (this.editForm.password && this.editForm.password.trim().length >= 6) {
      payload.password = this.editForm.password.trim();
    } else if (this.editForm.password && this.editForm.password.trim().length < 6) {
      this.savingAccount.set(false);
      this.accountError.set('Password must be at least 6 characters');
      return;
    }

    this.authService.updateProfile(payload).subscribe({
      next: () => {
        this.savingAccount.set(false);
        this.accountSuccess.set(true);
        setTimeout(() => {
          this.closeAccountModal();
        }, 1200);
      },
      error: (err) => {
        this.savingAccount.set(false);
        const msg = err.error?.detail || 'Failed to update account details. Please try again.';
        this.accountError.set(msg);
      }
    });
  }
}

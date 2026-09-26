import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService, DashboardSummary, Execution } from '../../api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <!-- Top Hero Banner: Neumorphic Glass Surface -->
    <div class="hero-banner">
      <div class="hero-content">
        <div class="hero-badge">
          <span class="hero-pulse"></span>
          <span>AUTONOMOUS MULTI-AGENT ENGINE</span>
        </div>
        <h1 class="hero-heading">Command Center</h1>
        <p class="hero-subtext">
          Orchestrate Intelligence. Protect Everything. Real-time brand guardrail telemetry & multi-agent execution pipeline.
        </p>
      </div>
      <div class="hero-cta">
        <a routerLink="/campaigns/new" class="btn btn-primary" style="font-size: 0.95rem; padding: 12px 26px;">
          ✦ Create Campaign
        </a>
      </div>
    </div>

    <!-- Loading State -->
    <div *ngIf="loading" class="loading-container">
      <div class="spinner"></div>
    </div>

    <!-- Error State -->
    <div *ngIf="error && !loading" class="error-state">
      <p class="error-state-title">Unable to load telemetry data</p>
      <p style="color: var(--ong-slate); font-size: 0.875rem; margin-top: 4px;">{{ error }}</p>
      <button class="btn btn-secondary" style="margin-top: 1rem;" (click)="loadDashboard()">Retry Connection</button>
    </div>

    <!-- Dashboard Content -->
    <div *ngIf="!loading && !error && summary">
      <!-- Neumorphic Metrics Grid -->
      <div class="metrics-grid">
        <div class="metric-card metric-blue">
          <div class="metric-label">Total Campaigns</div>
          <div class="metric-value">{{ summary.total_campaigns }}</div>
          <div class="metric-subtitle">Across all categories</div>
        </div>

        <div class="metric-card metric-azure">
          <div class="metric-label">Active Running</div>
          <div class="metric-value" style="color: #64B5F6;">{{ summary.running_executions }}</div>
          <div class="metric-subtitle">Live pipeline jobs</div>
        </div>

        <div class="metric-card metric-success">
          <div class="metric-label">Approved</div>
          <div class="metric-value" style="color: #30D158;">{{ summary.approved_campaigns }}</div>
          <div class="metric-subtitle">100% Brand Compliant</div>
        </div>

        <div class="metric-card metric-error">
          <div class="metric-label">Failed</div>
          <div class="metric-value" style="color: #FF453A;">{{ summary.failed_campaigns }}</div>
          <div class="metric-subtitle">Unrecoverable states</div>
        </div>

        <div class="metric-card metric-gold">
          <div class="metric-label">Review Required</div>
          <div class="metric-value" style="color: var(--ong-guardrail-gold);">{{ summary.review_required_campaigns }}</div>
          <div class="metric-subtitle">Human audit queue</div>
        </div>

        <div class="metric-card metric-blue">
          <div class="metric-label">Avg. Compliance</div>
          <div class="metric-value">
            {{ summary.average_compliance_score !== null ? (summary.average_compliance_score | number:'1.0-1') + '%' : '—' }}
          </div>
          <div class="metric-subtitle">Weighted guardrail index</div>
        </div>
      </div>

      <!-- Recent Executions -->
      <div class="card">
        <div class="card-header">
          <div>
            <h2 class="card-title">Recent Autonomous Executions</h2>
            <p style="font-size: 0.78rem; color: var(--ong-slate); margin-top: 2px;">
              Live audit ledger of agent runs, compliance validations, and repair cycles
            </p>
          </div>
          <span class="badge badge-running" style="font-size: 0.7rem;">LIVE AUDIT TRAIL</span>
        </div>

        <div *ngIf="summary.recent_executions.length === 0" class="empty-state">
          <div class="empty-state-icon">◈</div>
          <p class="empty-state-title">No executions recorded yet</p>
          <p class="empty-state-message" style="color: var(--ong-slate); font-size: 0.88rem; margin-top: 4px;">
            Create a campaign brief to let Agentic Canvas specialized agents orchestrate and validate brand assets.
          </p>
          <a routerLink="/campaigns/new" class="btn btn-primary" style="margin-top: 1.25rem;">+ Launch First Campaign</a>
        </div>

        <div class="table-container" *ngIf="summary.recent_executions.length > 0">
          <table>
            <thead>
              <tr>
                <th>Execution ID</th>
                <th>Status</th>
                <th>Compliance</th>
                <th>Started</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let exec of summary.recent_executions">
                <td style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--ong-secure-azure);">
                  {{ exec.id | slice:0:8 }}...
                </td>
                <td>
                  <span class="badge" [ngClass]="getStatusBadge(exec.status)">{{ exec.status }}</span>
                </td>
                <td>
                  <span *ngIf="exec.final_score !== null" style="font-weight: 700; font-size: 0.9rem;" [style.color]="getScoreColor(exec.final_score)">
                    {{ exec.final_score | number:'1.0-1' }}%
                  </span>
                  <span *ngIf="exec.final_score === null" style="color: var(--ong-slate);">—</span>
                </td>
                <td style="font-size: 0.8rem; color: var(--ong-slate);">{{ exec.started_at | date:'medium' }}</td>
                <td>
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <a [routerLink]="['/campaigns', exec.campaign_id]" class="btn btn-secondary" style="font-size: 0.74rem; padding: 6px 12px;">
                      Inspect Audit →
                    </a>
                    <button
                      type="button"
                      class="btn-row-delete"
                      (click)="deleteExecution(exec, $event)"
                      title="Delete this execution and clear all its data"
                    >
                      🗑
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .hero-banner {
      background: var(--glass-neu-surface);
      backdrop-filter: var(--glass-blur-md);
      -webkit-backdrop-filter: var(--glass-blur-md);
      border: 1px solid var(--glass-border);
      box-shadow: var(--neu-convex-shadow);
      border-radius: var(--radius-xl);
      padding: 1.6rem 2.2rem;
      margin-bottom: 1.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 2rem;
      position: relative;
      overflow: hidden;
    }

    .hero-banner::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 2px;
      background: linear-gradient(90deg, var(--ong-orchestration-blue) 0%, var(--ong-guardrail-gold) 50%, var(--ong-secure-azure) 100%);
    }

    .hero-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 5px 12px;
      border-radius: var(--radius-pill);
      background: var(--glass-neu-well);
      box-shadow: var(--neu-concave-shadow);
      border: 1px solid rgba(255, 255, 255, 0.08);
      font-size: 0.68rem;
      font-weight: 700;
      color: var(--ong-guardrail-gold);
      letter-spacing: 1.2px;
      margin-bottom: 12px;
    }

    .hero-pulse {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--ong-guardrail-gold);
      box-shadow: 0 0 8px var(--ong-guardrail-gold);
    }

    .hero-heading {
      font-size: 2.2rem;
      font-weight: 800;
      color: var(--ong-cloud-white);
      letter-spacing: -0.03em;
      line-height: 1.15;
    }

    .hero-subtext {
      font-size: 0.95rem;
      color: var(--ong-slate);
      margin-top: 8px;
      max-width: 620px;
      line-height: 1.6;
    }

    .hero-cta {
      flex-shrink: 0;
    }

    @media (max-width: 860px) {
      .hero-banner {
        flex-direction: column;
        align-items: flex-start;
        padding: 1.75rem;
      }
    }
  `]
})
export class DashboardComponent implements OnInit, OnDestroy {
  summary: DashboardSummary | null = null;
  loading = true;
  error: string | null = null;
  private refreshInterval: any;

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.loadDashboard();
    this.refreshInterval = setInterval(() => this.loadDashboard(), 10000);
  }

  ngOnDestroy() {
    if (this.refreshInterval) clearInterval(this.refreshInterval);
  }

  loadDashboard() {
    this.loading = !this.summary;
    this.error = null;

    this.api.getDashboardSummary().subscribe({
      next: (data) => {
        this.summary = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Could not connect to the Agentic Canvas backend API. Ensure the service is operational.';
        this.loading = false;
      }
    });
  }

  getStatusBadge(status: string): string {
    const map: { [key: string]: string } = {
      'approved': 'badge-approved',
      'completed': 'badge-completed',
      'running': 'badge-running',
      'generating_copy': 'badge-running',
      'structuring_layout': 'badge-running',
      'recommending_assets': 'badge-running',
      'validating_brand': 'badge-running',
      'repairing': 'badge-review',
      'failed': 'badge-failed',
      'review_required': 'badge-review',
      'created': 'badge-draft',
      'queued': 'badge-draft',
    };
    return map[status] || 'badge-draft';
  }

  getScoreColor(score: number): string {
    if (score >= 80) return '#30D158';
    if (score >= 60) return '#D6B25A';
    return '#FF453A';
  }

  deleteExecution(exec: Execution, event: MouseEvent) {
    event.stopPropagation();
    if (!confirm(`Are you sure you want to delete execution ${exec.id.slice(0, 8)}...? All associated runs, logs, and deliverables will be cleared.`)) {
      return;
    }
    this.api.deleteExecution(exec.id).subscribe({
      next: () => {
        this.loadDashboard();
      },
      error: (err) => {
        alert('Failed to delete execution: ' + (err?.error?.detail || err.message));
      }
    });
  }
}

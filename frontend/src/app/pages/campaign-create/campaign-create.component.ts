import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService, CampaignCreate } from '../../api.service';

@Component({
  selector: 'app-campaign-create',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page-header">
      <div>
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
          <span class="badge badge-running">PIPELINE INTAKE</span>
        </div>
        <h1 class="page-title">Initiate Campaign</h1>
        <p class="page-subtitle">
          Define strategic goals. Autonomous agents will synthesize copy, layout, and assets governed by brand guardrails.
        </p>
      </div>
    </div>

    <!-- Quick Sample Presets (Tactile Neumorphic Buttons) -->
    <div class="card" style="margin-bottom: 1.5rem; padding: 1.25rem 1.75rem;">
      <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
        <div>
          <span style="font-size: 0.82rem; font-weight: 700; color: var(--ong-secure-azure); text-transform: uppercase; letter-spacing: 1.1px;">
            ✦ Quick Presets
          </span>
          <p style="font-size: 0.78rem; color: var(--ong-slate); margin-top: 2px;">
            Load enterprise campaign briefs tested against strict brand guidelines
          </p>
        </div>
        <div style="display: flex; gap: 0.6rem; flex-wrap: wrap;">
          <button type="button" class="btn btn-secondary" style="font-size: 0.75rem; padding: 7px 14px;" (click)="loadPreset('security')">
            Zero-Trust Launch
          </button>
          <button type="button" class="btn btn-secondary" style="font-size: 0.75rem; padding: 7px 14px;" (click)="loadPreset('guardrails')">
            AI Guardrail Engine
          </button>
          <button type="button" class="btn btn-secondary" style="font-size: 0.75rem; padding: 7px 14px;" (click)="loadPreset('report')">
            Enterprise Report
          </button>
        </div>
      </div>
    </div>

    <!-- Main Form Card (Convex Neumorphic Glass) -->
    <div class="card">
      <form (ngSubmit)="onSubmit()" #campaignForm="ngForm">
        <div class="form-group">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <label class="form-label" for="name" style="margin-bottom: 0;">Campaign Title</label>
            <span style="font-size: 0.72rem; color: var(--ong-slate);">{{ campaign.name.length }}/255</span>
          </div>
          <input
            class="form-input"
            id="name"
            name="name"
            type="text"
            [(ngModel)]="campaign.name"
            required
            minlength="3"
            maxlength="255"
            placeholder="e.g., Agentic Canvas Zero-Trust Autonomous Agent Launch"
          />
        </div>

        <div class="form-group">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <label class="form-label" for="campaign_type" style="margin-bottom: 0;">Deliverable Category</label>
            <span style="font-size: 0.72rem; color: var(--ong-slate);">Layout & Tone Rule Target</span>
          </div>
          <select
            class="form-select"
            id="campaign_type"
            name="campaign_type"
            [(ngModel)]="campaign.campaign_type"
            required
          >
            <option value="" disabled>Select a campaign deliverable type</option>
            <option value="website">Website / Landing Page</option>
            <option value="landing_page">Landing Page</option>
            <option value="pitch_deck">Pitch Deck / Executive Deck</option>
            <option value="product_dashboard">Product Dashboard</option>
            <option value="developer_assets">Developer Assets</option>
            <option value="social_media">Social Media Campaign</option>
            <option value="report">Enterprise Security Report</option>
          </select>
        </div>

        <div class="form-group">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <label class="form-label" for="brief" style="margin-bottom: 0;">Campaign Brief & Value Proposition</label>
            <span style="font-size: 0.72rem; color: var(--ong-slate);">{{ campaign.brief.length }}/5000</span>
          </div>
          <textarea
            class="form-textarea"
            id="brief"
            name="brief"
            [(ngModel)]="campaign.brief"
            required
            minlength="10"
            maxlength="5000"
            rows="6"
            placeholder="Specify product capabilities, core security boundaries, compliance requirements, and audience drivers..."
          ></textarea>
        </div>

        <div class="form-group">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <label class="form-label" for="target_audience" style="margin-bottom: 0;">Target Stakeholders & Audience</label>
            <span style="font-size: 0.72rem; color: var(--ong-slate);">{{ campaign.target_audience.length }}/2000</span>
          </div>
          <textarea
            class="form-textarea"
            id="target_audience"
            name="target_audience"
            [(ngModel)]="campaign.target_audience"
            required
            minlength="5"
            maxlength="2000"
            rows="3"
            placeholder="e.g., Enterprise CISOs, Head of Security Architecture, VP of AI Infrastructure"
          ></textarea>
        </div>

        <div *ngIf="error" class="error-state" style="margin-bottom: 1.25rem; padding: 1rem;">
          <p class="error-state-title" style="font-size: 0.875rem;">{{ error }}</p>
        </div>

        <div style="display: flex; gap: 1.25rem; align-items: center; padding-top: 0.5rem;">
          <button
            type="submit"
            class="btn btn-primary"
            style="padding: 12px 28px; font-size: 0.95rem;"
            [disabled]="submitting || !campaignForm.valid"
          >
            <span *ngIf="!submitting">✦ Launch Autonomous Pipeline</span>
            <span *ngIf="submitting" style="display: flex; align-items: center; gap: 8px;">
              <span class="spinner" style="width: 16px; height: 16px; border-width: 2px;"></span> Initializing Agents...
            </span>
          </button>
        </div>
      </form>
    </div>
  `
})
export class CampaignCreateComponent {
  campaign: CampaignCreate = {
    name: '',
    brief: '',
    campaign_type: '',
    target_audience: ''
  };

  submitting = false;
  error: string | null = null;

  constructor(private api: ApiService, private router: Router) {}

  loadPreset(type: 'security' | 'guardrails' | 'report') {
    if (type === 'security') {
      this.campaign = {
        name: 'Agentic Canvas Zero-Trust Autonomous AI Security Launch',
        campaign_type: 'website',
        brief: 'Comprehensive launch campaign introducing Agentic Canvas autonomous agent orchestration with enterprise-grade guardrails. Focus on zero-trust protection, deterministic brand verification, and continuous compliance audit trails.',
        target_audience: 'Chief Information Security Officers (CISOs), Enterprise IT Architects, and AI Engineering Directors'
      };
    } else if (type === 'guardrails') {
      this.campaign = {
        name: 'Agentic Canvas Guardrail Engine Telemetry Platform',
        campaign_type: 'product_dashboard',
        brief: 'Product campaign launching the real-time Guardrail Evaluation Dashboard. Highlights include sub-second deterministic rule validation, semantic LLM evaluation, and automated repair loops for multi-agent workflows.',
        target_audience: 'Enterprise Security Operations (SecOps), Compliance Officers, and Lead AI Architects'
      };
    } else if (type === 'report') {
      this.campaign = {
        name: '2026 Enterprise AI Orchestration & Guardrail Report',
        campaign_type: 'report',
        brief: 'Authoritative research report on the state of enterprise multi-agent systems, vulnerabilities in unchecked LLM outputs, and mathematical guardrail enforcement methodologies.',
        target_audience: 'Chief Technology Officers (CTOs), Board Risk Committees, and Enterprise Architects'
      };
    }
  }

  onSubmit() {
    if (this.submitting) return;
    this.submitting = true;
    this.error = null;

    this.api.createCampaign(this.campaign).subscribe({
      next: (campaign) => {
        // Automatically start execution pipeline
        this.api.startExecution(campaign.id).subscribe({
          next: () => {
            this.router.navigate(['/campaigns', campaign.id]);
          },
          error: () => {
            this.router.navigate(['/campaigns', campaign.id]);
          }
        });
      },
      error: (err) => {
        console.error('Campaign creation error:', err);
        if (err.status === 0) {
          this.error = 'Unable to reach backend API at http://localhost:8000. Please verify the backend server is running.';
        } else if (err.error?.detail) {
          if (Array.isArray(err.error.detail)) {
            this.error = err.error.detail
              .map((d: any) => {
                const field = d.loc ? d.loc.slice(-1)[0] : '';
                const msg = d.msg || JSON.stringify(d);
                return field ? `${field}: ${msg}` : msg;
              })
              .join(' | ');
          } else if (typeof err.error.detail === 'string') {
            this.error = err.error.detail;
          } else {
            this.error = JSON.stringify(err.error.detail);
          }
        } else if (err.message) {
          this.error = err.message;
        } else {
          this.error = 'Failed to initiate campaign. Please verify all inputs.';
        }
        this.submitting = false;
      }
    });
  }
}

import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ApiService, Campaign, Execution, ExecutionEvent, ComplianceResult, GeneratedAsset } from '../../api.service';

@Component({
  selector: 'app-campaign-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  template: `
    <!-- Loading -->
    <div *ngIf="loading" class="loading-container"><div class="spinner"></div></div>

    <!-- Error -->
    <div *ngIf="error && !loading" class="error-state">
      <p class="error-state-title">{{ error }}</p>
      <button class="btn btn-secondary" style="margin-top: 1rem;" (click)="loadData()">Retry</button>
    </div>

    <!-- Notification Banner -->
    <div *ngIf="notificationMessage" class="notification-banner">
      <span>{{ notificationMessage }}</span>
      <button type="button" class="banner-close" (click)="notificationMessage = null">✕</button>
    </div>

    <!-- Content -->
    <div *ngIf="campaign && !loading">
      <div class="page-header">
        <div>
          <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
            <span class="badge" [ngClass]="getStatusBadge(latestExecution?.status || campaign.status)">
              {{ latestExecution?.status || campaign.status }}
            </span>
            <span style="font-size: 0.78rem; color: var(--ong-slate); font-family: var(--font-mono);">
              ID: {{ campaign.id | slice:0:8 }}
            </span>
          </div>
          <h1 class="page-title">{{ campaign.name }}</h1>
          <p class="page-subtitle">{{ campaign.campaign_type | uppercase }} — Created {{ campaign.created_at | date:'medium' }}</p>
        </div>
        <div style="display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap;">
          <!-- Execute Button -->
          <button *ngIf="!latestExecution || isTerminal(latestExecution.status)" class="btn btn-primary" (click)="executeAgain()" [disabled]="executing">
            <span *ngIf="!executing">▶ Execute Pipeline</span>
            <span *ngIf="executing" style="display: flex; align-items: center; gap: 8px;">
              <span class="spinner" style="width: 14px; height: 14px; border-width: 2px;"></span> Starting...
            </span>
          </button>

          <!-- Delete Execution Run Button -->
          <button
            *ngIf="latestExecution"
            type="button"
            class="btn btn-3d-danger"
            (click)="deleteCurrentExecution()"
            title="Delete this execution run, audit logs, compliance checks, and generated deliverables"
          >
            🗑 Delete Execution
          </button>

          <!-- Reset Campaign All Executions Button -->
          <button
            *ngIf="latestExecution || assets.length > 0 || events.length > 0"
            type="button"
            class="btn btn-secondary"
            (click)="resetCampaignAll()"
            title="Wipe all executions, logs, and assets to reset campaign to draft"
          >
            ↺ Reset Campaign
          </button>
        </div>
      </div>

      <!-- Two Column Layout (Campaign Brief + Neumorphic Compliance Dial) -->
      <div class="detail-grid">
        <!-- Campaign Brief Card -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">Campaign Brief & Strategic Context</h3>
            <span class="badge badge-running" style="font-size: 0.68rem;">{{ campaign.campaign_type }}</span>
          </div>
          <div class="recessed-well" style="padding: 16px; margin-bottom: 14px;">
            <p style="font-size: 0.9rem; color: var(--ong-cloud-white); line-height: 1.7;">{{ campaign.brief }}</p>
          </div>
          <div style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; color: var(--ong-slate);">
            <strong style="color: var(--ong-secure-azure);">Target Audience:</strong>
            <span>{{ campaign.target_audience }}</span>
          </div>
        </div>

        <!-- Compliance Dial Card -->
        <div class="card" *ngIf="latestCompliance">
          <div class="card-header">
            <div>
              <h3 class="card-title">Deterministic Brand Compliance</h3>
              <p class="card-subtitle" style="font-size: 0.76rem; color: var(--ong-slate); margin-top: 2px;">
                Evaluated by Semantic Engine {{ latestCompliance.evaluator_version }}
              </p>
            </div>
            <span class="badge" [ngClass]="latestCompliance.status === 'passed' ? 'badge-approved' : (latestCompliance.status === 'fail' ? 'badge-failed' : 'badge-review')" style="font-size: 0.7rem;">
              {{ latestCompliance.status | uppercase }}
            </span>
          </div>

          <div style="display: flex; gap: 2rem; align-items: center; flex-wrap: wrap;">
            <!-- 3-D Animated Radial Dial Orb -->
            <div class="orb-3d-container">
              <div class="orb-3d-outer" [style.--orb-color]="getScoreColor(latestCompliance.overall_score)">
                <div class="orb-halo-ring"></div>
                <div class="orb-radar-wave"></div>
                <div class="orb-3d-inner">
                  <span class="orb-3d-score" [style.color]="getScoreColor(latestCompliance.overall_score)">
                    {{ latestCompliance.overall_score | number:'1.0-0' }}%
                  </span>
                  <span class="orb-3d-label">GUARDRAIL</span>
                </div>
              </div>
            </div>

            <!-- Breakdown Bars -->
            <div style="flex: 1; min-width: 200px;">
              <div *ngIf="latestCompliance?.critical_violation" style="padding: 0.6rem 1rem; background: rgba(255,69,58,0.15); border: 1px solid rgba(255,69,58,0.35); border-radius: var(--radius-sm); margin-bottom: 0.85rem; box-shadow: var(--neu-convex-sm);">
                <span style="color: #FF453A; font-size: 0.78rem; font-weight: 700; display: flex; align-items: center; gap: 6px;">
                  ⚠ CRITICAL OVERRIDE ACTIVE — Automatic Approval Blocked
                </span>
              </div>
              <div *ngFor="let cat of getCategoryScores()" style="margin-bottom: 0.65rem;">
                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--ong-slate); margin-bottom: 4px;">
                  <span style="text-transform: capitalize; font-weight: 500;">{{ cat.name }}</span>
                  <span style="font-weight: 700; color: var(--ong-cloud-white);">{{ cat.score | number:'1.0-0' }}%</span>
                </div>
                <div class="compliance-bar">
                  <div class="compliance-bar-fill" [class.high]="cat.score >= 80" [class.medium]="cat.score >= 50 && cat.score < 80" [class.low]="cat.score < 50" [style.width.%]="cat.score"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Execution Trace (Neumorphic Stepper) -->
      <div class="card" style="margin-bottom: 1.5rem;">
        <div class="card-header">
          <div>
            <h3 class="card-title">Autonomous Orchestration Audit Trail</h3>
            <p class="card-subtitle" style="font-size: 0.76rem; color: var(--ong-slate); margin-top: 2px;">
              Multi-agent event stream recorded with sequence integrity
            </p>
          </div>
          <div style="display: flex; align-items: center; gap: 10px;">
            <span *ngIf="events.length > 0" class="badge badge-running" style="font-size: 0.7rem;">
              {{ events.length }} TRANSITIONS
            </span>
            <!-- Delete previous logs option -->
            <button
              *ngIf="events.length > 0"
              type="button"
              class="btn-sm-danger"
              (click)="clearExecutionLogs()"
              title="Delete previous execution trace logs"
            >
              🗑 Clear Trace Logs
            </button>
          </div>
        </div>

        <div class="execution-trace" *ngIf="events.length > 0">
          <div class="trace-step" *ngFor="let event of events">
            <div class="trace-icon" [ngClass]="getTraceIconClass(event)">
              {{ getTraceIcon(event) }}
            </div>
            <div class="trace-content">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <div class="trace-title">{{ formatState(event.to_state) }}</div>
                <span style="font-family: var(--font-mono); font-size: 0.7rem; color: var(--ong-slate);">SEQ #{{ event.sequence }}</span>
              </div>
              <div class="trace-detail" style="margin-top: 2px;">{{ event.reason || 'State transition' }}</div>
              <div class="trace-detail" style="font-size: 0.7rem; color: rgba(138, 153, 173, 0.7); margin-top: 4px;">
                {{ event.timestamp | date:'medium' }}
              </div>
            </div>
          </div>
        </div>

        <div *ngIf="events.length === 0" class="empty-trace-placeholder">
          <span>No execution trace logs found. Execute the pipeline to stream live orchestration steps.</span>
        </div>
      </div>

      <!-- Violations List -->
      <div class="card" style="margin-bottom: 1.5rem;" *ngIf="latestCompliance && latestCompliance.violations.length > 0">
        <div class="card-header">
          <h3 class="card-title">Brand Rule Violations ({{ latestCompliance.violations.length }})</h3>
          <span class="badge badge-review" style="font-size: 0.7rem;">ACTION REQUIRED</span>
        </div>

        <div *ngFor="let v of latestCompliance.violations" class="violation-item">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="badge" [ngClass]="v.severity === 'critical' ? 'badge-failed' : 'badge-review'" style="font-size: 0.65rem;">
                {{ v.severity | uppercase }}
              </span>
              <span class="violation-rule">{{ v.rule_id }}</span>
            </div>
            <span *ngIf="v.field" style="font-family: var(--font-mono); font-size: 0.72rem; color: var(--ong-slate);">{{ v.field }}</span>
          </div>
          <div class="violation-message">{{ v.message }}</div>
          <div class="violation-details" *ngIf="v.expected || v.actual">
            <div *ngIf="v.expected"><strong style="color: #30D158;">Expected:</strong> {{ v.expected }}</div>
            <div *ngIf="v.actual"><strong style="color: #FF453A;">Actual:</strong> {{ v.actual }}</div>
          </div>
          <div class="violation-details" *ngIf="v.suggested_fix" style="color: var(--ong-guardrail-gold); margin-top: 8px; font-weight: 500;">
            💡 <strong>Recommended Remediation:</strong> {{ v.suggested_fix }}
          </div>
        </div>
      </div>

      <!-- Generated Assets (Formatted in .README Format with Download & Edit Options) -->
      <div class="card" *ngIf="assets.length > 0">
        <div class="card-header" style="flex-wrap: wrap; gap: 14px;">
          <div>
            <h3 class="card-title">Generated Campaign Assets (.README Format)</h3>
            <p class="card-subtitle" style="font-size: 0.76rem; color: var(--ong-slate); margin-top: 2px;">
              Multi-agent structured deliverables formatted in interactive .README markdown specs
            </p>
          </div>
          
          <div class="artifacts-top-controls">
            <!-- Global Format Toggle -->
            <div class="segmented-control">
              <button
                type="button"
                [class.active]="globalViewMode === 'readme'"
                (click)="setGlobalViewMode('readme')"
                title="View artifacts as formatted .README markdown documents"
              >
                📖 .README View
              </button>
              <button
                type="button"
                [class.active]="globalViewMode === 'json'"
                (click)="setGlobalViewMode('json')"
                title="View raw JSON payload"
              >
                {{ '{ }' }} Raw JSON
              </button>
            </div>

            <!-- Download All Bundle README.md -->
            <button
              type="button"
              class="btn-sm-gold"
              (click)="downloadAllAsReadme()"
              title="Download entire campaign bundle as a README.md markdown document"
            >
              ⬇ Download All (README.md)
            </button>

            <!-- Clear All Assets Option -->
            <button
              type="button"
              class="btn-sm-danger"
              (click)="deleteAllAssets()"
              title="Clear all generated artifacts for this campaign"
            >
              🗑 Clear All
            </button>
          </div>
        </div>

        <!-- List of Generated Assets -->
        <div *ngFor="let asset of assets" class="asset-card">
          <div class="asset-card-header">
            <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
              <span class="asset-badge">{{ formatAssetType(asset.asset_type) }}</span>
              <span class="asset-timestamp">{{ asset.created_at | date:'shortTime' }}</span>
              <span class="badge badge-approved" style="font-size: 0.65rem;">{{ asset.status | uppercase }}</span>
            </div>

            <!-- Asset Actions Bar: Mode toggle, Copy Markdown, Download README, Edit, Delete -->
            <div class="asset-actions-bar">
              <div class="mini-segmented-control">
                <button
                  type="button"
                  [class.active]="getAssetViewMode(asset.id) === 'readme'"
                  (click)="setAssetViewMode(asset.id, 'readme')"
                  title="View in README format"
                >
                  📖 README
                </button>
                <button
                  type="button"
                  [class.active]="getAssetViewMode(asset.id) === 'json'"
                  (click)="setAssetViewMode(asset.id, 'json')"
                  title="View JSON format"
                >
                  JSON
                </button>
              </div>

              <button
                type="button"
                class="btn-action-ghost"
                (click)="copyAssetMarkdown(asset)"
                [title]="copiedAssetId === asset.id ? 'Copied to clipboard!' : 'Copy formatted .README markdown'"
              >
                {{ copiedAssetId === asset.id ? '✓ Copied' : '📋 Copy .md' }}
              </button>

              <button
                type="button"
                class="btn-action-ghost"
                (click)="downloadAssetReadme(asset)"
                title="Download this artifact as .README.md file"
              >
                ⬇ Download .md
              </button>

              <!-- Edit / Modify Option -->
              <button
                type="button"
                class="btn-action-accent"
                (click)="openEditModal(asset)"
                title="Modify or edit this generated artifact"
              >
                ✏ Edit Artifact
              </button>

              <!-- Delete Single Asset Option -->
              <button
                type="button"
                class="btn-action-danger"
                (click)="deleteAsset(asset)"
                title="Delete this artifact"
              >
                🗑
              </button>
            </div>
          </div>

          <!-- FORMAT 1: Formatted .README Document View -->
          <div *ngIf="getAssetViewMode(asset.id) === 'readme'" class="readme-document">
            
            <!-- COPYWRITER ASSET README -->
            <div *ngIf="isCopywriterAsset(asset)" class="readme-content-box">
              <div class="readme-file-indicator">
                <span class="file-icon">📄</span>
                <span class="file-name">README-copywriter.md</span>
                <span class="file-badge">BRAND APPROVED</span>
              </div>

              <div class="readme-section-block">
                <h1 class="readme-h1">{{ asset.content?.headline || 'Enterprise Campaign Headline' }}</h1>
                <p class="readme-lead" *ngIf="asset.content?.subheadline">{{ asset.content.subheadline }}</p>
              </div>

              <div class="readme-section-block" *ngIf="asset.content?.value_proposition">
                <h3 class="readme-h3">💡 Value Proposition</h3>
                <div class="readme-quote-box">
                  {{ asset.content.value_proposition }}
                </div>
              </div>

              <div class="readme-section-block" *ngIf="asset.content?.cta">
                <h3 class="readme-h3">🎯 Call to Action (CTA)</h3>
                <div class="readme-cta-pill">
                  <span class="cta-arrow">➜</span>
                  <span class="cta-string">{{ asset.content.cta }}</span>
                </div>
              </div>

              <div class="readme-section-block" *ngIf="asset.content?.supporting_copy">
                <h3 class="readme-h3">📝 Supporting Body Copy</h3>
                <div class="readme-text-prose">{{ asset.content.supporting_copy }}</div>
              </div>

              <div class="readme-section-block" *ngIf="asset.content?.social_posts?.length">
                <h3 class="readme-h3">📱 Social Media Posts ({{ asset.content.social_posts.length }})</h3>
                <div class="social-posts-stack">
                  <div *ngFor="let post of asset.content.social_posts; let pIdx = index" class="social-post-item">
                    <div class="social-post-header">
                      <span class="social-post-tag">Post #{{ pIdx + 1 }}</span>
                      <button type="button" class="btn-micro-copy" (click)="copyText(post)">Copy</button>
                    </div>
                    <div class="social-post-text">{{ post }}</div>
                  </div>
                </div>
              </div>

              <div class="readme-section-block" *ngIf="asset.content?.brand_context_used?.length">
                <h3 class="readme-h3">🛡 Brand Guardrails Referenced</h3>
                <div class="brand-rules-chips">
                  <span *ngFor="let rule of asset.content.brand_context_used" class="brand-chip">
                    {{ rule.rule_id }} (v{{ rule.version }})
                  </span>
                </div>
              </div>
            </div>

            <!-- LAYOUT SPEC ASSET README -->
            <div *ngIf="isLayoutAsset(asset)" class="readme-content-box">
              <div class="readme-file-indicator">
                <span class="file-icon">📐</span>
                <span class="file-name">README-layout-spec.md</span>
                <span class="file-badge">SEMANTIC GRID</span>
              </div>

              <div class="readme-section-block">
                <h1 class="readme-h1">Campaign Layout Specification</h1>
                <div class="layout-props-grid">
                  <div class="prop-card">
                    <span class="prop-label">Layout Type</span>
                    <span class="prop-value">{{ asset.content?.layout_type || 'Responsive Grid' }}</span>
                  </div>
                  <div class="prop-card">
                    <span class="prop-label">Campaign Type</span>
                    <span class="prop-value">{{ asset.content?.campaign_type || 'Website' }}</span>
                  </div>
                  <div class="prop-card">
                    <span class="prop-label">Logo Placement</span>
                    <span class="prop-value">{{ asset.content?.logo_placement || 'Header Left' }}</span>
                  </div>
                  <div class="prop-card">
                    <span class="prop-label">Logo Required</span>
                    <span class="prop-value text-gold">{{ asset.content?.logo_required !== false ? 'Required' : 'Optional' }}</span>
                  </div>
                </div>
              </div>

              <div class="readme-section-block" *ngIf="asset.content?.visual_hierarchy">
                <h3 class="readme-h3">👁 Visual Hierarchy Architecture</h3>
                <div class="readme-quote-box">{{ asset.content.visual_hierarchy }}</div>
              </div>

              <div class="readme-section-block" *ngIf="asset.content?.sections?.length">
                <h3 class="readme-h3">🧩 Layout Sections Spec Table</h3>
                <div class="table-responsive">
                  <table class="layout-spec-table">
                    <thead>
                      <tr>
                        <th>Section ID</th>
                        <th>Type</th>
                        <th>Hierarchy</th>
                        <th>Styling (Background / Text)</th>
                        <th>Components</th>
                        <th>Placement</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr *ngFor="let sec of asset.content.sections">
                        <td><span class="font-mono text-bold">{{ sec.section_id }}</span></td>
                        <td><span class="pill-blue">{{ sec.section_type }}</span></td>
                        <td><span class="pill-hierarchy">Level {{ sec.hierarchy_level || 1 }}</span></td>
                        <td>
                          <div class="color-palette-cell">
                            <span class="swatch-circle" [style.background-color]="sec.background_color" [title]="'BG: ' + sec.background_color"></span>
                            <span class="swatch-circle" [style.background-color]="sec.text_color" [title]="'Text: ' + sec.text_color"></span>
                            <span class="font-mono text-xs">{{ sec.background_color }} / {{ sec.text_color }}</span>
                          </div>
                        </td>
                        <td>
                          <div class="components-cell">
                            <span *ngFor="let c of sec.components" class="comp-tag">{{ c }}</span>
                          </div>
                        </td>
                        <td><span class="text-xs font-mono text-slate">{{ sec.placement || 'standard' }}</span></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <!-- VISUAL ASSET RECOMMENDATIONS README -->
            <div *ngIf="isVisualAssets(asset)" class="readme-content-box">
              <div class="readme-file-indicator">
                <span class="file-icon">🎨</span>
                <span class="file-name">README-visual-assets.md</span>
                <span class="file-badge">ASSET BRIEF</span>
              </div>

              <div class="readme-section-block">
                <h1 class="readme-h1">Visual Asset Recommendations</h1>
                <p class="readme-lead" *ngIf="asset.content?.campaign_type">
                  Specification for <strong>{{ asset.content.campaign_type | uppercase }}</strong> campaign visual elements.
                </p>
              </div>

              <div class="visual-recommendations-grid" *ngIf="asset.content?.recommendations?.length">
                <div *ngFor="let rec of asset.content.recommendations; let rIdx = index" class="rec-card">
                  <div class="rec-header">
                    <span class="rec-type-badge">{{ rec.asset_type || ('Asset #' + (rIdx + 1)) }}</span>
                    <span class="rec-aspect-badge">{{ rec.aspect_ratio || '16:9' }}</span>
                  </div>
                  <div class="rec-subject">{{ rec.subject }}</div>

                  <div class="rec-color-row">
                    <div class="color-item">
                      <span class="color-item-lbl">Background</span>
                      <div class="swatch-wrapper">
                        <span class="swatch-circle" [style.background-color]="rec.background_color"></span>
                        <span class="font-mono text-xs">{{ rec.background_color }}</span>
                      </div>
                    </div>
                    <div class="color-item" *ngIf="rec.gradient">
                      <span class="color-item-lbl">Gradient</span>
                      <span class="font-mono text-xs text-gold">{{ rec.gradient }}</span>
                    </div>
                  </div>

                  <div class="rec-alt-box" *ngIf="rec.alt_text">
                    <span class="alt-lbl">ALT-TEXT:</span>
                    <span class="alt-text-content">"{{ rec.alt_text }}"</span>
                  </div>

                  <div class="rec-restrictions" *ngIf="rec.brand_restrictions?.length">
                    <span *ngFor="let res of rec.brand_restrictions" class="restriction-chip">
                      🛡 {{ res }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Expandable Raw .md Source Code -->
            <details class="raw-markdown-details">
              <summary>View Raw .README.md Markdown Source</summary>
              <div class="recessed-well" style="margin-top: 8px;">
                <pre class="asset-code">{{ getAssetMarkdown(asset) }}</pre>
              </div>
            </details>
          </div>

          <!-- FORMAT 2: Raw JSON View -->
          <div *ngIf="getAssetViewMode(asset.id) === 'json'" class="recessed-well" style="margin-top: 12px;">
            <pre class="asset-code">{{ asset.content | json }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit / Modify Artifact Modal -->
    <div *ngIf="editModalOpen" class="modal-backdrop" (click)="closeEditModal()">
      <div class="modal-surface" (click)="$event.stopPropagation()">
        <div class="modal-header">
          <div>
            <h2 class="modal-title">✏ Modify Generated Artifact</h2>
            <p class="modal-subtitle">{{ formatAssetType(editingAsset?.asset_type || '') }} — ID: {{ editingAsset?.id | slice:0:8 }}</p>
          </div>
          <button type="button" class="btn-modal-close" (click)="closeEditModal()">✕</button>
        </div>

        <div *ngIf="editError" class="modal-error-banner">
          {{ editError }}
        </div>

        <!-- Mode selector in modal -->
        <div class="modal-mode-tabs">
          <button
            type="button"
            class="tab-btn"
            [class.active]="!editJsonMode"
            (click)="editJsonMode = false"
          >
            Structured Editor
          </button>
          <button
            type="button"
            class="tab-btn"
            [class.active]="editJsonMode"
            (click)="editJsonMode = true"
          >
            Raw JSON Editor
          </button>
        </div>

        <div class="modal-body">
          <!-- Structured Form View -->
          <div *ngIf="!editJsonMode" class="edit-form-stack">
            <!-- Copywriter fields -->
            <ng-container *ngIf="editingAsset && isCopywriterAsset(editingAsset)">
              <div class="form-group">
                <label class="form-label">Headline</label>
                <input
                  type="text"
                  class="form-input"
                  [(ngModel)]="editFormContent.headline"
                  placeholder="Campaign Headline"
                />
              </div>

              <div class="form-group">
                <label class="form-label">Subheadline</label>
                <input
                  type="text"
                  class="form-input"
                  [(ngModel)]="editFormContent.subheadline"
                  placeholder="Campaign Subheadline"
                />
              </div>

              <div class="form-group">
                <label class="form-label">Value Proposition</label>
                <textarea
                  class="form-textarea"
                  rows="3"
                  [(ngModel)]="editFormContent.value_proposition"
                  placeholder="Value proposition text"
                ></textarea>
              </div>

              <div class="form-group">
                <label class="form-label">Call To Action (CTA)</label>
                <input
                  type="text"
                  class="form-input"
                  [(ngModel)]="editFormContent.cta"
                  placeholder="e.g. Schedule Enterprise Assessment"
                />
              </div>

              <div class="form-group">
                <label class="form-label">Supporting Body Copy</label>
                <textarea
                  class="form-textarea"
                  rows="4"
                  [(ngModel)]="editFormContent.supporting_copy"
                  placeholder="Detailed narrative copy..."
                ></textarea>
              </div>

              <div class="form-group">
                <label class="form-label">Social Media Posts (Separate each post with a blank line)</label>
                <textarea
                  class="form-textarea font-mono"
                  rows="4"
                  [(ngModel)]="editFormContent._social_posts_text"
                  placeholder="Post 1...&#10;&#10;Post 2..."
                ></textarea>
              </div>
            </ng-container>

            <!-- Layout fields -->
            <ng-container *ngIf="editingAsset && isLayoutAsset(editingAsset)">
              <div class="form-row-2">
                <div class="form-group">
                  <label class="form-label">Layout Type</label>
                  <input
                    type="text"
                    class="form-input"
                    [(ngModel)]="editFormContent.layout_type"
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">Logo Placement</label>
                  <input
                    type="text"
                    class="form-input"
                    [(ngModel)]="editFormContent.logo_placement"
                  />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Visual Hierarchy Guidance</label>
                <textarea
                  class="form-textarea"
                  rows="3"
                  [(ngModel)]="editFormContent.visual_hierarchy"
                ></textarea>
              </div>

              <div class="form-group">
                <label class="form-label">Sections JSON Spec</label>
                <textarea
                  class="form-textarea font-mono"
                  rows="6"
                  [(ngModel)]="editFormContent._sections_raw"
                  placeholder="JSON array of sections"
                ></textarea>
              </div>
            </ng-container>

            <!-- Visual Asset or Other fields -->
            <ng-container *ngIf="editingAsset && !isCopywriterAsset(editingAsset) && !isLayoutAsset(editingAsset)">
              <div class="form-group">
                <label class="form-label">Campaign Type</label>
                <input
                  type="text"
                  class="form-input"
                  [(ngModel)]="editFormContent.campaign_type"
                />
              </div>
              <div class="form-group">
                <label class="form-label">Recommendations / Content (JSON)</label>
                <textarea
                  class="form-textarea font-mono"
                  rows="8"
                  [(ngModel)]="editRawJson"
                ></textarea>
              </div>
            </ng-container>
          </div>

          <!-- Raw JSON Editor View -->
          <div *ngIf="editJsonMode" class="edit-json-box">
            <label class="form-label">Edit Raw JSON Payload</label>
            <textarea
              class="form-textarea font-mono"
              rows="14"
              [(ngModel)]="editRawJson"
              placeholder="Paste or edit valid JSON..."
            ></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" (click)="closeEditModal()">Cancel</button>
          <button
            type="button"
            class="btn btn-primary"
            (click)="saveAssetEdit()"
            [disabled]="editSaving"
          >
            <span *ngIf="!editSaving">💾 Save Modifications</span>
            <span *ngIf="editSaving">Saving...</span>
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .detail-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.5rem;
      margin-bottom: 1.5rem;
    }

    .notification-banner {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 18px;
      margin-bottom: 1.25rem;
      border-radius: var(--radius-md);
      background: linear-gradient(135deg, rgba(48, 209, 88, 0.18) 0%, rgba(12, 33, 64, 0.8) 100%);
      border: 1px solid rgba(48, 209, 88, 0.4);
      color: #7BF299;
      font-size: 0.86rem;
      font-weight: 600;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
    }
    .banner-close {
      background: transparent;
      border: none;
      color: #7BF299;
      font-size: 1rem;
      cursor: pointer;
      padding: 2px 6px;
    }

    .recessed-well {
      background: var(--glass-neu-well);
      box-shadow: var(--neu-concave-shadow);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: var(--radius-md);
      overflow: hidden;
    }

    /* ─── 3-D Animated Radial Gauge Orb ────────────────────────────── */
    .orb-3d-container {
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 16px;
      perspective: 1000px;
    }

    .orb-3d-outer {
      width: 136px;
      height: 136px;
      border-radius: 50%;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      background: radial-gradient(circle at 35% 30%, rgba(38, 116, 184, 0.35) 0%, rgba(7, 20, 38, 0.95) 75%);
      box-shadow: 
        0 14px 34px -4px rgba(0, 0, 0, 0.9),
        0 0 26px var(--orb-color, rgba(48, 209, 88, 0.35)),
        inset 0 2px 3px rgba(255, 255, 255, 0.4),
        inset 0 -3px 6px rgba(0, 0, 0, 0.85);
      border: 1.5px solid rgba(255, 255, 255, 0.18);
      animation: orbBreathe 4s ease-in-out infinite alternate;
      transform-style: preserve-3d;
    }

    .orb-halo-ring {
      position: absolute;
      inset: -6px;
      border-radius: 50%;
      border: 2px dashed var(--orb-color, #30D158);
      opacity: 0.55;
      animation: haloSpin 20s linear infinite;
      pointer-events: none;
    }

    .orb-radar-wave {
      position: absolute;
      inset: 0;
      border-radius: 50%;
      border: 1.5px solid var(--orb-color, #30D158);
      animation: radarPulse 3.5s cubic-bezier(0.1, 0.8, 0.3, 1) infinite;
      pointer-events: none;
    }

    .orb-3d-inner {
      width: 96px;
      height: 96px;
      border-radius: 50%;
      background: linear-gradient(145deg, rgba(16, 44, 82, 0.92) 0%, rgba(4, 12, 24, 0.98) 100%);
      box-shadow: 
        inset 5px 5px 12px rgba(0, 0, 0, 0.95),
        inset -2px -2px 6px rgba(255, 255, 255, 0.15),
        0 4px 12px rgba(0, 0, 0, 0.6);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      border: 1px solid rgba(255, 255, 255, 0.12);
      z-index: 2;
    }

    .orb-3d-score {
      font-size: 1.85rem;
      font-weight: 800;
      line-height: 1;
      letter-spacing: -0.03em;
      text-shadow: 0 0 16px var(--orb-color, #30D158), 0 4px 8px rgba(0, 0, 0, 0.8);
    }

    .orb-3d-label {
      font-size: 0.62rem;
      font-weight: 800;
      color: var(--ong-slate);
      letter-spacing: 1.5px;
      margin-top: 4px;
    }

    @keyframes orbBreathe {
      0% { transform: scale(0.97) translateZ(0); }
      100% { transform: scale(1.03) translateZ(12px); }
    }
    @keyframes haloSpin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    @keyframes radarPulse {
      0% { transform: scale(0.95); opacity: 0.8; }
      100% { transform: scale(1.4); opacity: 0; }
    }

    .empty-trace-placeholder {
      padding: 24px;
      text-align: center;
      color: var(--ong-slate);
      font-size: 0.84rem;
      font-style: italic;
    }

    /* Artifacts Top Controls */
    .artifacts-top-controls {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .segmented-control {
      display: inline-flex;
      background: var(--glass-neu-well);
      padding: 3px;
      border-radius: var(--radius-pill);
      border: 1px solid rgba(255, 255, 255, 0.1);
      box-shadow: var(--neu-concave-shadow);
    }
    .segmented-control button {
      background: transparent;
      border: none;
      color: var(--ong-slate);
      padding: 5px 14px;
      font-size: 0.74rem;
      font-weight: 600;
      border-radius: var(--radius-pill);
      cursor: pointer;
      transition: all var(--spring-fast);
    }
    .segmented-control button.active {
      background: linear-gradient(135deg, #16528D 0%, #2674B8 100%);
      color: #FFF;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
    }

    .mini-segmented-control {
      display: inline-flex;
      background: var(--glass-neu-well);
      padding: 2px;
      border-radius: var(--radius-pill);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .mini-segmented-control button {
      background: transparent;
      border: none;
      color: var(--ong-slate);
      padding: 3px 10px;
      font-size: 0.68rem;
      font-weight: 600;
      border-radius: var(--radius-pill);
      cursor: pointer;
      transition: all var(--spring-fast);
    }
    .mini-segmented-control button.active {
      background: rgba(38, 116, 184, 0.6);
      color: #FFF;
    }

    .btn-sm-gold {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      border-radius: var(--radius-pill);
      background: linear-gradient(135deg, rgba(214, 178, 90, 0.25) 0%, rgba(12, 33, 64, 0.8) 100%);
      border: 1px solid rgba(214, 178, 90, 0.45);
      color: var(--ong-guardrail-gold);
      font-size: 0.75rem;
      font-weight: 700;
      cursor: pointer;
      box-shadow: var(--neu-convex-sm);
      transition: all var(--spring-fast);
    }
    .btn-sm-gold:hover {
      background: linear-gradient(135deg, rgba(214, 178, 90, 0.38) 0%, rgba(16, 44, 82, 0.9) 100%);
      border-color: var(--ong-guardrail-gold);
      transform: translateY(-1px);
    }

    .btn-sm-danger {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 12px;
      border-radius: var(--radius-pill);
      background: rgba(255, 69, 58, 0.12);
      border: 1px solid rgba(255, 69, 58, 0.35);
      color: #FF7B72;
      font-size: 0.72rem;
      font-weight: 600;
      cursor: pointer;
      transition: all var(--spring-fast);
    }
    .btn-sm-danger:hover {
      background: rgba(255, 69, 58, 0.25);
      border-color: #FF453A;
      color: #FFF;
    }

    /* Asset Card */
    .asset-card {
      margin-bottom: 1.5rem;
      padding: 1.35rem;
      background: var(--glass-neu-surface-subtle);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-lg);
      box-shadow: var(--neu-convex-sm);
      transition: all var(--spring-fast);
    }
    .asset-card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
      flex-wrap: wrap;
      gap: 12px;
    }
    .asset-badge {
      font-weight: 700;
      text-transform: uppercase;
      font-size: 0.76rem;
      color: var(--ong-secure-azure);
      letter-spacing: 1px;
    }
    .asset-timestamp {
      font-size: 0.74rem;
      color: var(--ong-slate);
      font-family: var(--font-mono);
    }

    .asset-actions-bar {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    .btn-action-ghost {
      background: var(--glass-neu-surface);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: var(--ong-cloud-white);
      font-size: 0.72rem;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      transition: all var(--spring-fast);
    }
    .btn-action-ghost:hover {
      background: var(--glass-neu-surface-hover);
      border-color: rgba(255, 255, 255, 0.25);
    }

    .btn-action-accent {
      background: linear-gradient(135deg, rgba(22, 82, 141, 0.4) 0%, rgba(38, 116, 184, 0.3) 100%);
      border: 1px solid rgba(38, 116, 184, 0.5);
      color: #92C5FD;
      font-size: 0.72rem;
      font-weight: 600;
      padding: 4px 11px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      transition: all var(--spring-fast);
    }
    .btn-action-accent:hover {
      background: linear-gradient(135deg, rgba(22, 82, 141, 0.7) 0%, rgba(38, 116, 184, 0.6) 100%);
      color: #FFF;
      border-color: #60A5FA;
    }

    .btn-action-danger {
      background: rgba(255, 69, 58, 0.1);
      border: 1px solid rgba(255, 69, 58, 0.3);
      color: #FF7B72;
      font-size: 0.75rem;
      padding: 4px 8px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      transition: all var(--spring-fast);
    }
    .btn-action-danger:hover {
      background: rgba(255, 69, 58, 0.3);
      color: #FFF;
    }

    /* README Rendered Container */
    .readme-document {
      background: linear-gradient(165deg, rgba(9, 23, 44, 0.95) 0%, rgba(6, 16, 32, 0.98) 100%);
      border: 1px solid rgba(255, 255, 255, 0.1);
      box-shadow: var(--neu-concave-shadow);
      border-radius: var(--radius-md);
      padding: 1.5rem;
    }

    .readme-file-indicator {
      display: flex;
      align-items: center;
      gap: 8px;
      padding-bottom: 12px;
      margin-bottom: 16px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      font-family: var(--font-mono);
      font-size: 0.78rem;
    }
    .file-icon { font-size: 0.95rem; }
    .file-name { color: #92C5FD; font-weight: 600; }
    .file-badge {
      margin-left: auto;
      font-size: 0.62rem;
      background: rgba(48, 209, 88, 0.15);
      border: 1px solid rgba(48, 209, 88, 0.3);
      color: #30D158;
      padding: 2px 8px;
      border-radius: var(--radius-pill);
      font-weight: 700;
    }

    .readme-section-block {
      margin-bottom: 1.25rem;
    }

    .readme-h1 {
      font-size: 1.35rem;
      font-weight: 700;
      color: var(--ong-cloud-white);
      margin: 0 0 6px 0;
      line-height: 1.3;
      letter-spacing: -0.02em;
    }
    .readme-lead {
      font-size: 0.92rem;
      color: rgba(245, 248, 252, 0.85);
      line-height: 1.5;
      margin: 0;
    }
    .readme-h3 {
      font-size: 0.88rem;
      font-weight: 700;
      color: var(--ong-guardrail-gold);
      margin: 0 0 8px 0;
      letter-spacing: -0.01em;
    }
    .readme-quote-box {
      background: rgba(22, 82, 141, 0.15);
      border-left: 3px solid var(--ong-secure-azure);
      padding: 10px 14px;
      border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
      color: var(--ong-cloud-white);
      font-size: 0.86rem;
      line-height: 1.6;
    }
    .readme-cta-pill {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 10px 18px;
      border-radius: var(--radius-pill);
      background: linear-gradient(135deg, #16528D 0%, #D6B25A 100%);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
    }
    .cta-arrow { font-weight: 800; color: #FFF; }
    .cta-string { font-size: 0.92rem; font-weight: 700; color: #FFF; letter-spacing: 0.02em; }

    .readme-text-prose {
      font-size: 0.86rem;
      line-height: 1.65;
      color: rgba(245, 248, 252, 0.88);
      white-space: pre-wrap;
    }

    .social-posts-stack {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .social-post-item {
      background: var(--glass-neu-surface);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: var(--radius-md);
      padding: 12px 14px;
    }
    .social-post-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
    }
    .social-post-tag {
      font-size: 0.68rem;
      font-weight: 700;
      color: var(--ong-secure-azure);
      text-transform: uppercase;
      font-family: var(--font-mono);
    }
    .btn-micro-copy {
      background: transparent;
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: var(--ong-slate);
      font-size: 0.65rem;
      padding: 2px 7px;
      border-radius: 4px;
      cursor: pointer;
    }
    .btn-micro-copy:hover {
      color: #FFF;
      border-color: rgba(255, 255, 255, 0.4);
    }
    .social-post-text {
      font-size: 0.82rem;
      color: var(--ong-cloud-white);
      line-height: 1.5;
    }

    .brand-rules-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .brand-chip {
      font-size: 0.72rem;
      font-family: var(--font-mono);
      background: rgba(214, 178, 90, 0.12);
      border: 1px solid rgba(214, 178, 90, 0.3);
      color: var(--ong-guardrail-gold);
      padding: 3px 9px;
      border-radius: var(--radius-sm);
    }

    /* Layout specific */
    .layout-props-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 10px;
      margin-top: 10px;
    }
    .prop-card {
      background: var(--glass-neu-surface);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: var(--radius-sm);
      padding: 10px 12px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .prop-label { font-size: 0.65rem; color: var(--ong-slate); text-transform: uppercase; letter-spacing: 1px; }
    .prop-value { font-size: 0.85rem; font-weight: 700; color: var(--ong-cloud-white); }

    .table-responsive {
      overflow-x: auto;
    }
    .layout-spec-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.78rem;
      margin-top: 6px;
    }
    .layout-spec-table th {
      text-align: left;
      padding: 8px 10px;
      background: rgba(12, 33, 64, 0.6);
      border-bottom: 1px solid rgba(255, 255, 255, 0.12);
      color: var(--ong-slate);
      font-weight: 600;
      font-size: 0.72rem;
      text-transform: uppercase;
    }
    .layout-spec-table td {
      padding: 10px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      color: var(--ong-cloud-white);
    }
    .pill-blue {
      background: rgba(38, 116, 184, 0.2);
      border: 1px solid rgba(38, 116, 184, 0.4);
      color: #92C5FD;
      padding: 2px 7px;
      border-radius: 4px;
      font-family: var(--font-mono);
      font-size: 0.7rem;
    }
    .pill-hierarchy {
      background: rgba(214, 178, 90, 0.15);
      color: var(--ong-guardrail-gold);
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 600;
      font-size: 0.7rem;
    }
    .color-palette-cell {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .swatch-circle {
      width: 13px;
      height: 13px;
      border-radius: 50%;
      border: 1px solid rgba(255, 255, 255, 0.3);
      display: inline-block;
    }
    .components-cell {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
    }
    .comp-tag {
      background: rgba(255, 255, 255, 0.06);
      padding: 2px 6px;
      border-radius: 3px;
      font-size: 0.7rem;
    }

    /* Visual recommendations */
    .visual-recommendations-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 14px;
      margin-top: 12px;
    }
    .rec-card {
      background: var(--glass-neu-surface);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: var(--radius-md);
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .rec-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .rec-type-badge {
      font-weight: 700;
      color: #92C5FD;
      font-size: 0.76rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .rec-aspect-badge {
      font-family: var(--font-mono);
      font-size: 0.68rem;
      background: rgba(255, 255, 255, 0.08);
      padding: 2px 6px;
      border-radius: 4px;
      color: var(--ong-slate);
    }
    .rec-subject {
      font-size: 0.84rem;
      line-height: 1.5;
      color: var(--ong-cloud-white);
    }
    .rec-color-row {
      display: flex;
      gap: 16px;
      align-items: center;
      font-size: 0.72rem;
    }
    .color-item-lbl {
      color: var(--ong-slate);
      margin-right: 6px;
    }
    .swatch-wrapper {
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .rec-alt-box {
      background: var(--glass-neu-well);
      border-radius: var(--radius-sm);
      padding: 8px 10px;
      font-size: 0.74rem;
      color: var(--ong-cloud-white);
      line-height: 1.4;
    }
    .alt-lbl {
      color: var(--ong-slate);
      font-weight: 700;
      font-size: 0.65rem;
      margin-right: 4px;
    }
    .rec-restrictions {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
    .restriction-chip {
      font-size: 0.68rem;
      font-family: var(--font-mono);
      color: #FFB347;
      background: rgba(255, 179, 71, 0.1);
      border: 1px solid rgba(255, 179, 71, 0.25);
      padding: 2px 7px;
      border-radius: 4px;
    }

    .raw-markdown-details {
      margin-top: 16px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      padding-top: 12px;
      font-size: 0.78rem;
      color: var(--ong-slate);
      cursor: pointer;
    }
    .raw-markdown-details summary {
      outline: none;
      font-weight: 600;
      color: var(--ong-secure-azure);
      margin-bottom: 8px;
    }

    .asset-code {
      padding: 1rem;
      font-size: 0.76rem;
      color: var(--ong-cloud-white);
      font-family: var(--font-mono);
      overflow-x: auto;
      white-space: pre-wrap;
      max-height: 320px;
      overflow-y: auto;
      line-height: 1.5;
    }

    /* Modal Backdrop and Dialog */
    .modal-backdrop {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(3, 10, 20, 0.85);
      backdrop-filter: blur(8px);
      z-index: 1000;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
      animation: fadeIn 0.15s ease-out;
    }
    .modal-surface {
      width: 100%;
      max-width: 680px;
      max-height: 90vh;
      display: flex;
      flex-direction: column;
      background: linear-gradient(155deg, rgba(16, 44, 82, 0.98) 0%, rgba(7, 20, 38, 0.99) 100%);
      border: 1px solid rgba(255, 255, 255, 0.18);
      border-radius: var(--radius-lg);
      box-shadow: 0 24px 64px rgba(0, 0, 0, 0.8), 0 0 1px rgba(255, 255, 255, 0.4);
      overflow: hidden;
      animation: scaleUp 0.18s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px 24px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    .modal-title {
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--ong-cloud-white);
      margin: 0;
    }
    .modal-subtitle {
      font-size: 0.75rem;
      color: var(--ong-slate);
      margin: 2px 0 0 0;
    }
    .btn-modal-close {
      background: transparent;
      border: none;
      color: var(--ong-slate);
      font-size: 1.25rem;
      cursor: pointer;
      padding: 4px 8px;
      border-radius: var(--radius-sm);
    }
    .btn-modal-close:hover {
      color: #FFF;
      background: rgba(255, 255, 255, 0.1);
    }

    .modal-error-banner {
      background: rgba(255, 69, 58, 0.18);
      border-left: 4px solid #FF453A;
      color: #FF7B72;
      padding: 10px 18px;
      font-size: 0.82rem;
      font-weight: 600;
    }

    .modal-mode-tabs {
      display: flex;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      background: rgba(0, 0, 0, 0.2);
    }
    .tab-btn {
      flex: 1;
      background: transparent;
      border: none;
      border-bottom: 2px solid transparent;
      color: var(--ong-slate);
      font-size: 0.8rem;
      font-weight: 600;
      padding: 11px 16px;
      cursor: pointer;
      transition: all var(--spring-fast);
    }
    .tab-btn.active {
      color: var(--ong-cloud-white);
      border-bottom-color: var(--ong-secure-azure);
      background: rgba(22, 82, 141, 0.15);
    }

    .modal-body {
      padding: 20px 24px;
      overflow-y: auto;
      flex: 1;
    }

    .edit-form-stack {
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .form-row-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }
    .form-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .form-label {
      font-size: 0.76rem;
      font-weight: 600;
      color: var(--ong-slate);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .form-input {
      background: var(--glass-neu-well);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: var(--radius-sm);
      padding: 9px 13px;
      color: var(--ong-cloud-white);
      font-size: 0.88rem;
      font-family: inherit;
      outline: none;
      box-shadow: var(--neu-concave-shadow);
      transition: all var(--spring-fast);
    }
    .form-input:focus {
      border-color: var(--ong-secure-azure);
      box-shadow: 0 0 10px rgba(38, 116, 184, 0.4);
    }
    .form-textarea {
      background: var(--glass-neu-well);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: var(--radius-sm);
      padding: 9px 13px;
      color: var(--ong-cloud-white);
      font-size: 0.84rem;
      font-family: inherit;
      outline: none;
      box-shadow: var(--neu-concave-shadow);
      resize: vertical;
      line-height: 1.5;
    }
    .form-textarea:focus {
      border-color: var(--ong-secure-azure);
      box-shadow: 0 0 10px rgba(38, 116, 184, 0.4);
    }

    .modal-footer {
      padding: 16px 24px;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      background: rgba(0, 0, 0, 0.25);
    }

    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    @keyframes scaleUp {
      from { transform: scale(0.96); opacity: 0; }
      to { transform: scale(1); opacity: 1; }
    }

    @media (max-width: 860px) {
      .detail-grid {
        grid-template-columns: 1fr;
      }
      .form-row-2 {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class CampaignDetailComponent implements OnInit, OnDestroy {
  campaignId = '';
  campaign: Campaign | null = null;
  latestExecution: Execution | null = null;
  events: ExecutionEvent[] = [];
  compliance: ComplianceResult[] = [];
  assets: GeneratedAsset[] = [];
  loading = true;
  error: string | null = null;
  executing = false;
  private refreshInterval: any;

  // View Mode: 'readme' vs 'json'
  globalViewMode: 'readme' | 'json' = 'readme';
  assetViewModes: { [assetId: string]: 'readme' | 'json' } = {};
  copiedAssetId: string | null = null;
  notificationMessage: string | null = null;

  // Edit Modal State
  editModalOpen = false;
  editingAsset: GeneratedAsset | null = null;
  editJsonMode = false;
  editFormContent: any = {};
  editRawJson = '';
  editSaving = false;
  editError: string | null = null;

  private pollInterval: any = null;

  get latestCompliance(): ComplianceResult | null {
    return this.compliance.length > 0 ? this.compliance[this.compliance.length - 1] : null;
  }

  constructor(private api: ApiService, private route: ActivatedRoute) {}

  ngOnInit() {
    this.campaignId = this.route.snapshot.paramMap.get('id') || '';
    this.loadData();
    this.refreshInterval = setInterval(() => {
      if (this.latestExecution && !this.isTerminal(this.latestExecution.status)) {
        this.loadData();
      }
    }, 3000);
  }

  ngOnDestroy() {
    if (this.refreshInterval) clearInterval(this.refreshInterval);
    if (this.pollInterval) clearInterval(this.pollInterval);
  }

  loadData() {
    this.error = null;
    this.api.getCampaign(this.campaignId).subscribe({
      next: (campaign) => {
        this.campaign = campaign;
        this.loading = false;
        this.loadAssets();

        // Load latest executions for this campaign
        this.api.getCampaignExecutions(this.campaignId).subscribe({
          next: (executions) => {
            if (executions && executions.length > 0) {
              this.latestExecution = executions[0];
              this.loadExecutionDetails(this.latestExecution.id);
            }
          }
        });
      },
      error: () => {
        this.error = 'Campaign not found or API unavailable.';
        this.loading = false;
      }
    });
  }

  loadExecutionDetails(executionId: string) {
    this.api.getExecutionEvents(executionId).subscribe({
      next: (events) => this.events = events
    });
    this.api.getCompliance(executionId).subscribe({
      next: (comp) => this.compliance = comp
    });
  }

  loadAssets() {
    this.api.getCampaignAssets(this.campaignId).subscribe({
      next: (assets) => {
        this.assets = assets;
        // Initialize view mode map
        assets.forEach(a => {
          if (!this.assetViewModes[a.id]) {
            this.assetViewModes[a.id] = this.globalViewMode;
          }
        });
      }
    });
  }

  executeAgain() {
    this.executing = true;
    const key = `exec-${this.campaignId}-${Date.now()}`;
    this.api.startExecution(this.campaignId, key).subscribe({
      next: (execution) => {
        this.latestExecution = execution;
        this.executing = false;
        this.pollExecution(execution.id);
      },
      error: () => {
        this.executing = false;
      }
    });
  }

  pollExecution(executionId: string) {
    if (this.pollInterval) clearInterval(this.pollInterval);
    this.pollInterval = setInterval(() => {
      this.api.getExecution(executionId).subscribe({
        next: (exec) => {
          this.latestExecution = exec;
          this.loadExecutionDetails(executionId);
          if (this.isTerminal(exec.status)) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
            this.loadAssets();
          }
        }
      });
    }, 2000);
  }

  isTerminal(status: string): boolean {
    return ['approved', 'completed', 'failed', 'review_required'].includes(status);
  }

  getStatusBadge(status: string): string {
    const map: { [key: string]: string } = {
      'approved': 'badge-approved', 'completed': 'badge-completed',
      'running': 'badge-running', 'generating_copy': 'badge-running',
      'structuring_layout': 'badge-running', 'recommending_assets': 'badge-running',
      'validating_brand': 'badge-running', 'repairing': 'badge-review',
      'failed': 'badge-failed', 'review_required': 'badge-review',
      'draft': 'badge-draft', 'created': 'badge-draft', 'active': 'badge-running',
    };
    return map[status] || 'badge-draft';
  }

  getScoreColor(score: number): string {
    if (score >= 80) return '#30D158';
    if (score >= 60) return '#D6B25A';
    return '#FF453A';
  }

  getCategoryScores(): { name: string; score: number }[] {
    if (!this.latestCompliance?.category_scores) return [];
    return Object.entries(this.latestCompliance.category_scores).map(([name, score]) => ({ name, score }));
  }

  getTraceIcon(event: ExecutionEvent): string {
    const state = event.to_state;
    if (['approved', 'completed'].includes(state)) return '✓';
    if (state === 'failed') return '✗';
    if (state === 'repairing') return '↻';
    if (state === 'review_required') return '⚠';
    if (['running', 'generating_copy', 'structuring_layout', 'recommending_assets', 'validating_brand'].includes(state)) return '▶';
    return '●';
  }

  getTraceIconClass(event: ExecutionEvent): string {
    const state = event.to_state;
    if (['approved', 'completed'].includes(state)) return 'completed';
    if (state === 'failed') return 'failed';
    if (state === 'repairing' || state === 'review_required') return 'repair';
    if (['running', 'generating_copy', 'structuring_layout', 'recommending_assets', 'validating_brand'].includes(state)) return 'completed';
    return 'pending';
  }

  formatState(state: string): string {
    return state.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  }

  // ─── Format & Asset Type Utilities ──────────────────────────────────────
  formatAssetType(type: string): string {
    const map: Record<string, string> = {
      'copy': 'Copywriting Deliverable',
      'copywriter': 'Copywriting Deliverable',
      'layout': 'Layout Specification',
      'layout_structurer': 'Layout Specification',
      'assets': 'Visual Asset Recommendations',
      'asset_recommender': 'Visual Asset Recommendations',
    };
    return map[type.toLowerCase()] || type.toUpperCase();
  }

  isCopywriterAsset(asset: GeneratedAsset): boolean {
    const t = (asset.asset_type || '').toLowerCase();
    return t.includes('copy') || !!(asset.content && (asset.content.headline || asset.content.cta));
  }

  isLayoutAsset(asset: GeneratedAsset): boolean {
    const t = (asset.asset_type || '').toLowerCase();
    return t.includes('layout') || !!(asset.content && (asset.content.sections || asset.content.layout_type));
  }

  isVisualAssets(asset: GeneratedAsset): boolean {
    const t = (asset.asset_type || '').toLowerCase();
    return t.includes('asset') || !!(asset.content && asset.content.recommendations);
  }

  // ─── View Mode Controls ────────────────────────────────────────────────
  setGlobalViewMode(mode: 'readme' | 'json') {
    this.globalViewMode = mode;
    this.assets.forEach(a => {
      this.assetViewModes[a.id] = mode;
    });
  }

  getAssetViewMode(assetId: string): 'readme' | 'json' {
    return this.assetViewModes[assetId] || this.globalViewMode;
  }

  setAssetViewMode(assetId: string, mode: 'readme' | 'json') {
    this.assetViewModes[assetId] = mode;
  }

  // ─── Markdown / README Generation ──────────────────────────────────────
  getAssetMarkdown(asset: GeneratedAsset): string {
    const c = asset.content || {};
    const lines: string[] = [];

    if (this.isCopywriterAsset(asset)) {
      lines.push(`# ${c.headline || 'Enterprise Campaign Copy'}\n`);
      if (c.subheadline) {
        lines.push(`> ${c.subheadline}\n`);
      }
      if (c.value_proposition) {
        lines.push(`### Value Proposition\n${c.value_proposition}\n`);
      }
      if (c.cta) {
        lines.push(`### Call to Action (CTA)\n**${c.cta}**\n`);
      }
      if (c.supporting_copy) {
        lines.push(`### Supporting Copy\n${c.supporting_copy}\n`);
      }
      if (Array.isArray(c.social_posts) && c.social_posts.length > 0) {
        lines.push(`### Social Media Deliverables\n`);
        c.social_posts.forEach((post: string, i: number) => {
          lines.push(`${i + 1}. ${post}`);
        });
        lines.push('');
      }
      if (Array.isArray(c.brand_context_used) && c.brand_context_used.length > 0) {
        lines.push(`### Brand Guardrails Applied\n`);
        lines.push(`| Rule ID | Version |`);
        lines.push(`| :--- | :--- |`);
        c.brand_context_used.forEach((rule: any) => {
          lines.push(`| \`${rule.rule_id}\` | \`${rule.version}\` |`);
        });
        lines.push('');
      }
    } else if (this.isLayoutAsset(asset)) {
      lines.push(`# Campaign Layout Specification\n`);
      lines.push(`- **Layout Type**: ${c.layout_type || 'Standard'}`);
      lines.push(`- **Campaign Profile**: ${c.campaign_type || 'General'}`);
      lines.push(`- **Visual Hierarchy**: ${c.visual_hierarchy || 'Standard'}`);
      lines.push(`- **Logo Placement**: ${c.logo_placement || 'Header Left'} (Required: ${c.logo_required !== false ? 'Yes' : 'No'})\n`);

      if (Array.isArray(c.sections) && c.sections.length > 0) {
        lines.push(`## Layout Structural Sections\n`);
        lines.push(`| Section ID | Type | Hierarchy | Background | Text Color | Components | Placement |`);
        lines.push(`| :--- | :--- | :--- | :--- | :--- | :--- | :--- |`);
        c.sections.forEach((sec: any) => {
          const comps = Array.isArray(sec.components) ? sec.components.join(', ') : (sec.components || '-');
          lines.push(`| **${sec.section_id}** | \`${sec.section_type}\` | Level ${sec.hierarchy_level || 1} | \`${sec.background_color}\` | \`${sec.text_color}\` | ${comps} | \`${sec.placement || 'standard'}\` |`);
        });
        lines.push('');
      }
      if (Array.isArray(c.brand_context_used) && c.brand_context_used.length > 0) {
        lines.push(`### Brand Guardrails Applied\n`);
        lines.push(`| Rule ID | Version |`);
        lines.push(`| :--- | :--- |`);
        c.brand_context_used.forEach((rule: any) => {
          lines.push(`| \`${rule.rule_id}\` | \`${rule.version}\` |`);
        });
        lines.push('');
      }
    } else if (this.isVisualAssets(asset)) {
      lines.push(`# Visual Asset Recommendations\n`);
      if (c.campaign_type) {
        lines.push(`- **Campaign Profile**: ${c.campaign_type}\n`);
      }
      if (Array.isArray(c.recommendations) && c.recommendations.length > 0) {
        lines.push(`## Recommended Visual Assets\n`);
        c.recommendations.forEach((rec: any, i: number) => {
          lines.push(`### ${i + 1}. ${rec.asset_type || 'Asset'} (${rec.aspect_ratio || '16:9'})\n`);
          lines.push(`- **Subject**: ${rec.subject}`);
          lines.push(`- **Colors**: Background \`${rec.background_color || '#0C2140'}\`${rec.gradient ? ` | Gradient: \`${rec.gradient}\`` : ''}`);
          if (rec.alt_text) lines.push(`- **Accessibility Alt Text**: "${rec.alt_text}"`);
          if (Array.isArray(rec.brand_restrictions) && rec.brand_restrictions.length > 0) {
            lines.push(`- **Brand Restrictions**: ${rec.brand_restrictions.map((r: string) => `\`${r}\``).join(', ')}`);
          }
          lines.push('');
        });
      }
      if (Array.isArray(c.brand_context_used) && c.brand_context_used.length > 0) {
        lines.push(`### Brand Guardrails Applied\n`);
        lines.push(`| Rule ID | Version |`);
        lines.push(`| :--- | :--- |`);
        c.brand_context_used.forEach((rule: any) => {
          lines.push(`| \`${rule.rule_id}\` | \`${rule.version}\` |`);
        });
        lines.push('');
      }
    } else {
      lines.push(`# ${asset.asset_type.toUpperCase()} Deliverable\n`);
      lines.push(`Status: \`${asset.status}\` | Generated: \`${asset.created_at}\`\n`);
      lines.push('```json');
      lines.push(JSON.stringify(c, null, 2));
      lines.push('```');
    }

    return lines.join('\n');
  }

  generateCampaignBundleReadme(): string {
    const lines: string[] = [];
    const name = this.campaign?.name || 'Enterprise Campaign';
    lines.push(`# ${name} — Deliverable Artifacts & Specifications\n`);
    lines.push(`> **Generated by Agentic Canvas Autonomous Orchestration Engine**`);
    lines.push(`> Multi-agent Pipeline Verified with Deterministic Brand Guardrails\n`);

    lines.push(`## Campaign Overview`);
    lines.push(`- **Campaign ID**: \`${this.campaign?.id}\``);
    lines.push(`- **Type**: \`${this.campaign?.campaign_type}\``);
    lines.push(`- **Target Audience**: ${this.campaign?.target_audience || 'N/A'}`);
    lines.push(`- **Status**: \`${this.latestExecution?.status || this.campaign?.status}\``);
    if (this.latestCompliance) {
      lines.push(`- **Brand Compliance Score**: **${this.latestCompliance.overall_score}%**`);
      lines.push(`- **Critical Override**: ${this.latestCompliance.critical_violation ? '⚠️ BLOCKED' : '✓ Clean'}`);
    }
    lines.push('');

    if (this.campaign?.brief) {
      lines.push(`## Strategic Campaign Brief\n${this.campaign.brief}\n`);
    }

    lines.push(`---\n`);

    this.assets.forEach((asset, idx) => {
      lines.push(`## Artifact #${idx + 1}: ${this.formatAssetType(asset.asset_type)}\n`);
      lines.push(this.getAssetMarkdown(asset));
      lines.push(`\n---\n`);
    });

    lines.push(`*Generated via Agentic Canvas Platform on ${new Date().toISOString()}.*`);
    return lines.join('\n');
  }

  // ─── Download and Copy Actions ──────────────────────────────────────────
  downloadAssetReadme(asset: GeneratedAsset) {
    const slug = (this.campaign?.name || 'campaign')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-');
    const filename = `${slug}-${asset.asset_type.toLowerCase()}-README.md`;
    const content = this.getAssetMarkdown(asset);
    this.downloadFile(filename, content);
  }

  downloadAllAsReadme() {
    const slug = (this.campaign?.name || 'campaign')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-');
    const filename = `${slug}-CAMPAIGN-README.md`;
    const content = this.generateCampaignBundleReadme();
    this.downloadFile(filename, content);
  }

  downloadFile(filename: string, content: string) {
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    this.showNotification(`Downloaded ${filename}`);
  }

  copyAssetMarkdown(asset: GeneratedAsset) {
    const md = this.getAssetMarkdown(asset);
    this.copyText(md);
    this.copiedAssetId = asset.id;
    setTimeout(() => {
      if (this.copiedAssetId === asset.id) this.copiedAssetId = null;
    }, 2500);
  }

  copyText(text: string) {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text);
      this.showNotification('Copied markdown to clipboard!');
    }
  }

  // ─── Modify / Edit Artifact Actions ─────────────────────────────────────
  openEditModal(asset: GeneratedAsset) {
    this.editingAsset = asset;
    this.editError = null;
    this.editFormContent = JSON.parse(JSON.stringify(asset.content || {}));
    
    // Prepare social posts text helper
    if (Array.isArray(this.editFormContent.social_posts)) {
      this.editFormContent._social_posts_text = this.editFormContent.social_posts.join('\n\n');
    }
    // Prepare sections raw helper
    if (Array.isArray(this.editFormContent.sections)) {
      this.editFormContent._sections_raw = JSON.stringify(this.editFormContent.sections, null, 2);
    }

    this.editRawJson = JSON.stringify(asset.content || {}, null, 2);
    this.editJsonMode = false;
    this.editModalOpen = true;
  }

  closeEditModal() {
    this.editModalOpen = false;
    this.editingAsset = null;
    this.editError = null;
  }

  saveAssetEdit() {
    if (!this.editingAsset) return;
    this.editSaving = true;
    this.editError = null;

    let payloadContent: any;
    if (this.editJsonMode) {
      try {
        payloadContent = JSON.parse(this.editRawJson);
      } catch (err: any) {
        this.editError = 'Invalid JSON syntax: ' + err.message;
        this.editSaving = false;
        return;
      }
    } else {
      payloadContent = { ...this.editFormContent };
      // Parse social posts text
      if (payloadContent._social_posts_text !== undefined) {
        payloadContent.social_posts = payloadContent._social_posts_text
          .split('\n')
          .map((s: string) => s.trim())
          .filter((s: string) => s.length > 0);
        delete payloadContent._social_posts_text;
      }
      // Parse sections raw
      if (payloadContent._sections_raw !== undefined) {
        try {
          payloadContent.sections = JSON.parse(payloadContent._sections_raw);
        } catch (e: any) {
          this.editError = 'Invalid sections JSON: ' + e.message;
          this.editSaving = false;
          return;
        }
        delete payloadContent._sections_raw;
      }
    }

    this.api.updateCampaignAsset(this.campaignId, this.editingAsset.id, {
      content: payloadContent
    }).subscribe({
      next: (updated) => {
        const idx = this.assets.findIndex(a => a.id === updated.id);
        if (idx !== -1) {
          this.assets[idx] = updated;
        }
        this.editSaving = false;
        this.closeEditModal();
        this.showNotification('Artifact modified and saved successfully!');
      },
      error: (err) => {
        this.editSaving = false;
        this.editError = err?.error?.detail || 'Failed to save modifications. Please try again.';
      }
    });
  }

  deleteAsset(asset: GeneratedAsset) {
    if (!confirm(`Are you sure you want to delete this ${this.formatAssetType(asset.asset_type)} artifact?`)) {
      return;
    }
    this.api.deleteCampaignAsset(this.campaignId, asset.id).subscribe({
      next: () => {
        this.assets = this.assets.filter(a => a.id !== asset.id);
        this.showNotification('Artifact deleted successfully.');
      },
      error: (err) => {
        alert('Failed to delete artifact: ' + (err?.error?.detail || err.message));
      }
    });
  }

  deleteAllAssets() {
    if (!confirm('Are you sure you want to delete ALL generated artifacts for this campaign?')) {
      return;
    }
    this.api.clearCampaignAssets(this.campaignId).subscribe({
      next: (res) => {
        this.assets = [];
        this.showNotification(`Cleared ${res.deleted_count || 0} artifacts.`);
      },
      error: (err) => {
        alert('Failed to clear artifacts: ' + (err?.error?.detail || err.message));
      }
    });
  }

  clearExecutionLogs() {
    if (!confirm('Are you sure you want to delete previous execution trace logs?')) {
      return;
    }
    if (this.latestExecution) {
      this.api.clearExecutionEvents(this.latestExecution.id).subscribe({
        next: (res) => {
          this.events = [];
          this.showNotification(`Execution trace logs deleted (${res.deleted_count || 0} records).`);
        },
        error: (err) => {
          alert('Failed to clear execution logs: ' + (err?.error?.detail || err.message));
        }
      });
    } else {
      this.api.clearCampaignLogs(this.campaignId).subscribe({
        next: (res) => {
          this.events = [];
          this.showNotification(`Campaign trace logs deleted (${res.deleted_count || 0} records).`);
        },
        error: (err) => {
          alert('Failed to clear campaign logs: ' + (err?.error?.detail || err.message));
        }
      });
    }
  }

  deleteCurrentExecution() {
    if (!this.latestExecution) return;
    if (!confirm('Are you sure you want to delete this execution run? All associated trace logs, compliance results, and generated deliverables will be cleared completely.')) {
      return;
    }
    const execId = this.latestExecution.id;
    this.api.deleteExecution(execId).subscribe({
      next: () => {
        this.latestExecution = null;
        this.events = [];
        this.compliance = [];
        this.assets = [];
        this.loadData();
        this.showNotification('Execution run and all associated data cleared.');
      },
      error: (err) => {
        alert('Failed to delete execution: ' + (err?.error?.detail || err.message));
      }
    });
  }

  resetCampaignAll() {
    if (!confirm('Are you sure you want to completely reset this campaign? All executions, trace logs, compliance checks, and generated deliverables will be wiped clean.')) {
      return;
    }
    this.api.deleteCampaignExecutions(this.campaignId).subscribe({
      next: (res) => {
        this.latestExecution = null;
        this.events = [];
        this.compliance = [];
        this.assets = [];
        if (this.campaign) this.campaign.status = 'draft';
        this.loadData();
        this.showNotification(`Campaign reset. Cleared ${res.deleted_count || 0} executions and all deliverables.`);
      },
      error: (err) => {
        alert('Failed to reset campaign: ' + (err?.error?.detail || err.message));
      }
    });
  }

  showNotification(msg: string) {
    this.notificationMessage = msg;
    setTimeout(() => {
      if (this.notificationMessage === msg) {
        this.notificationMessage = null;
      }
    }, 4500);
  }
}

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, BrandRule } from '../../api.service';

@Component({
  selector: 'app-brand-rules',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="page-header">
      <div>
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
          <span class="badge badge-approved">RAG VECTOR KNOWLEDGE BASE</span>
        </div>
        <h1 class="page-title">Brand Guardrail Specifications</h1>
        <p class="page-subtitle">
          Official Agentic Canvas brand constraints, color kits, and deterministic validation rules ingested into ChromaDB.
        </p>
      </div>
    </div>

    <!-- Loading -->
    <div *ngIf="loading" class="loading-container"><div class="spinner"></div></div>

    <!-- Error -->
    <div *ngIf="error && !loading" class="error-state">
      <p class="error-state-title">{{ error }}</p>
      <button class="btn btn-secondary" style="margin-top: 1rem;" (click)="loadRules()">Retry</button>
    </div>

    <!-- Main Content -->
    <div *ngIf="!loading && !error">
      <!-- Agentic Canvas Approved Brand Palette (Neumorphic Glass Tiles) -->
      <div class="card" style="margin-bottom: 2rem;">
        <div class="card-header">
          <div>
            <h3 class="card-title">Agentic Canvas Official Brand Palette</h3>
            <p style="font-size: 0.78rem; color: var(--ong-slate); margin-top: 2px;">
              Core color hierarchy: 60% Deep Navy, 20% Blue Family, 10% Cloud White, 10% Guardrail Gold
            </p>
          </div>
          <span class="badge badge-running" style="font-size: 0.7rem;">7 APPROVED TOKENS</span>
        </div>

        <div class="swatch-grid">
          <div *ngFor="let color of colorPalette" class="swatch-card">
            <div class="swatch-block" [style.background]="color.hex">
              <span class="swatch-role-tag">{{ color.role }}</span>
            </div>
            <div class="swatch-info">
              <div class="swatch-name">{{ color.name }}</div>
              <div class="swatch-hex">{{ color.hex }}</div>
              <div class="swatch-desc">{{ color.meaning }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Approved Gradient Pairings (Neumorphic Glass Tiles) -->
      <div class="card" style="margin-bottom: 2rem;">
        <div class="card-header">
          <div>
            <h3 class="card-title">Approved Gradient Pairings</h3>
            <p style="font-size: 0.78rem; color: var(--ong-slate); margin-top: 2px;">
              Strict deterministic guardrails reject any gradient outside these 4 approved pairings
            </p>
          </div>
          <span class="badge badge-approved" style="font-size: 0.7rem;">4 PAIRINGS</span>
        </div>

        <div class="gradient-grid">
          <div *ngFor="let grad of gradientPairings" class="gradient-card">
            <div class="gradient-preview" [style.background]="grad.css"></div>
            <div class="gradient-details">
              <div class="gradient-title">{{ grad.name }}</div>
              <div class="gradient-hexes">{{ grad.from }} → {{ grad.to }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Category Filter Tabs (Tactile Neumorphic Buttons) -->
      <div style="display: flex; gap: 0.6rem; flex-wrap: wrap; margin-bottom: 1.25rem;">
        <button
          class="btn"
          [ngClass]="selectedCategory === null ? 'btn-primary' : 'btn-secondary'"
          style="font-size: 0.74rem; padding: 6px 14px;"
          (click)="filterCategory(null)"
        >
          ALL RULES ({{ rules.length }})
        </button>
        <button
          *ngFor="let cat of categories"
          class="btn"
          [ngClass]="selectedCategory === cat ? 'btn-primary' : 'btn-secondary'"
          style="font-size: 0.74rem; padding: 6px 14px;"
          (click)="filterCategory(cat)"
        >
          {{ cat | uppercase }}
        </button>
      </div>

      <!-- Rules Table -->
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Rule ID</th>
              <th>Category</th>
              <th>Priority</th>
              <th>Rule Specification</th>
              <th>Version</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let rule of filteredRules">
              <td style="font-family: var(--font-mono); color: var(--ong-secure-azure); font-size: 0.8rem; font-weight: 600; white-space: nowrap;">
                {{ rule.rule_id }}
              </td>
              <td>
                <span class="badge" [ngClass]="getCategoryClass(rule.category)">{{ rule.category }}</span>
              </td>
              <td>
                <span class="badge" [ngClass]="getPriorityClass(rule.priority)">{{ rule.priority | uppercase }}</span>
              </td>
              <td style="font-size: 0.85rem; max-width: 520px; line-height: 1.55;">
                {{ rule.content }}
              </td>
              <td style="font-size: 0.78rem; color: var(--ong-slate); font-family: var(--font-mono);">
                v{{ rule.version }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  styles: [`
    .swatch-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 1.25rem;
    }

    .swatch-card {
      background: var(--glass-neu-surface-subtle);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-md);
      padding: 12px;
      box-shadow: var(--neu-convex-sm);
      transition: all var(--spring-base);
    }

    .swatch-card:hover {
      transform: translateY(-3px);
      box-shadow: var(--neu-convex-shadow-hover);
      border-color: var(--glass-border-light);
    }

    .swatch-block {
      width: 100%;
      height: 64px;
      border-radius: var(--radius-sm);
      border: 1px solid rgba(255, 255, 255, 0.2);
      box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.4), 0 4px 12px rgba(0, 0, 0, 0.4);
      position: relative;
      overflow: hidden;
    }

    .swatch-role-tag {
      position: absolute;
      bottom: 4px;
      right: 6px;
      font-size: 0.6rem;
      font-weight: 700;
      background: rgba(7, 20, 38, 0.7);
      padding: 2px 5px;
      border-radius: 4px;
      color: var(--ong-cloud-white);
      backdrop-filter: blur(4px);
    }

    .swatch-info {
      margin-top: 10px;
    }

    .swatch-name {
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--ong-cloud-white);
    }

    .swatch-hex {
      font-size: 0.75rem;
      font-family: var(--font-mono);
      color: var(--ong-guardrail-gold);
      margin-top: 2px;
    }

    .swatch-desc {
      font-size: 0.68rem;
      color: var(--ong-slate);
      margin-top: 4px;
      line-height: 1.4;
    }

    .gradient-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1.25rem;
    }

    .gradient-card {
      background: var(--glass-neu-surface-subtle);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-md);
      padding: 14px;
      box-shadow: var(--neu-convex-sm);
      transition: all var(--spring-base);
    }

    .gradient-card:hover {
      transform: translateY(-2px);
      border-color: var(--glass-border-light);
    }

    .gradient-preview {
      width: 100%;
      height: 52px;
      border-radius: var(--radius-sm);
      border: 1px solid rgba(255, 255, 255, 0.2);
      box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.35), 0 4px 12px rgba(0, 0, 0, 0.4);
    }

    .gradient-details {
      margin-top: 10px;
    }

    .gradient-title {
      font-size: 0.84rem;
      font-weight: 700;
      color: var(--ong-cloud-white);
    }

    .gradient-hexes {
      font-size: 0.72rem;
      font-family: var(--font-mono);
      color: var(--ong-slate);
      margin-top: 2px;
    }
  `]
})
export class BrandRulesComponent implements OnInit {
  rules: BrandRule[] = [];
  filteredRules: BrandRule[] = [];
  categories: string[] = [];
  selectedCategory: string | null = null;
  loading = true;
  error: string | null = null;

  colorPalette = [
    { name: 'Deep Navy', hex: '#0C2140', role: '60%', meaning: 'Trust, security, authority, primary foundation' },
    { name: 'Orchestration Blue', hex: '#16528D', role: '20%', meaning: 'Technology, intelligence, connectivity' },
    { name: 'Secure Azure', hex: '#2674B8', role: 'Accent', meaning: 'Innovation, clarity, forward movement' },
    { name: 'Guardrail Gold', hex: '#D6B25A', role: '10%', meaning: 'Protection, assurance, premium quality, CTAs' },
    { name: 'Cloud White', hex: '#F5F8FC', role: '10%', meaning: 'Clarity, transparency, primary readable text' },
    { name: 'Slate', hex: '#5F7188', role: 'Secondary', meaning: 'Balance, professionalism, secondary text' },
    { name: 'Midnight', hex: '#071426', role: 'Zero-Trust', meaning: 'Zero-trust depth, resilience, root background' },
  ];

  gradientPairings = [
    { name: 'Navy → Blue', from: '#0C2140', to: '#16528D', css: 'linear-gradient(135deg, #0C2140 0%, #16528D 100%)' },
    { name: 'Blue → Azure', from: '#16528D', to: '#2674B8', css: 'linear-gradient(135deg, #16528D 0%, #2674B8 100%)' },
    { name: 'Navy → Gold', from: '#0C2140', to: '#D6B25A', css: 'linear-gradient(135deg, #0C2140 0%, #D6B25A 100%)' },
    { name: 'Midnight → Blue', from: '#071426', to: '#16528D', css: 'linear-gradient(135deg, #071426 0%, #16528D 100%)' },
  ];

  constructor(private api: ApiService) {}

  ngOnInit() { this.loadRules(); }

  loadRules() {
    this.loading = true;
    this.error = null;
    this.api.getBrandRules().subscribe({
      next: (rules) => {
        this.rules = rules;
        this.filteredRules = rules;
        this.categories = [...new Set(rules.map(r => r.category))];
        this.loading = false;
      },
      error: () => {
        this.error = 'Could not load brand rules from the knowledge base.';
        this.loading = false;
      }
    });
  }

  filterCategory(category: string | null) {
    this.selectedCategory = category;
    this.filteredRules = category ? this.rules.filter(r => r.category === category) : this.rules;
  }

  getCategoryClass(category: string): string {
    const map: { [key: string]: string } = {
      'color': 'badge-running', 'gradient': 'badge-running', 'tone': 'badge-review',
      'logo': 'badge-review', 'typography': 'badge-draft', 'visual': 'badge-running',
      'accessibility': 'badge-approved', 'tagline': 'badge-review',
      'application': 'badge-draft', 'color_hierarchy': 'badge-running',
    };
    return map[category] || 'badge-draft';
  }

  getPriorityClass(priority: string): string {
    return priority === 'critical' ? 'badge-failed' : priority === 'high' ? 'badge-review' : 'badge-draft';
  }
}

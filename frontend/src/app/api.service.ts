import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Campaign {
  id: string;
  name: string;
  brief: string;
  campaign_type: string;
  target_audience: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CampaignCreate {
  name: string;
  brief: string;
  campaign_type: string;
  target_audience: string;
}

export interface Execution {
  id: string;
  campaign_id: string;
  status: string;
  current_state: string;
  started_at: string | null;
  completed_at: string | null;
  retry_count: number;
  final_score: number | null;
  failure_reason: string | null;
}

export interface ExecutionEvent {
  id: string;
  execution_id: string;
  from_state: string | null;
  to_state: string;
  reason: string | null;
  timestamp: string;
  sequence: number;
}

export interface Violation {
  id: string;
  rule_id: string;
  severity: string;
  field: string | null;
  expected: string | null;
  actual: string | null;
  message: string;
  suggested_fix: string | null;
}

export interface ComplianceResult {
  id: string;
  execution_id: string;
  overall_score: number;
  category_scores: { [key: string]: number } | null;
  status: string;
  critical_violation: boolean;
  evaluator_version: string;
  attempt_number: number;
  violations: Violation[];
  created_at: string;
}

export interface BrandRule {
  id: string;
  rule_id: string;
  category: string;
  version: string;
  priority: string;
  source: string;
  content: string;
  active: boolean;
}

export interface GeneratedAsset {
  id: string;
  campaign_id: string;
  execution_id: string | null;
  asset_type: string;
  content: any;
  status: string;
  created_at: string;
}

export interface DashboardSummary {
  total_campaigns: number;
  running_executions: number;
  approved_campaigns: number;
  failed_campaigns: number;
  review_required_campaigns: number;
  average_compliance_score: number | null;
  recent_executions: Execution[];
}

export interface HealthStatus {
  status: string;
  version: string;
  environment: string;
  database: string;
  timestamp: string;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  // Health
  getHealth(): Observable<HealthStatus> {
    return this.http.get<HealthStatus>(`${this.baseUrl}/health`);
  }

  // Dashboard
  getDashboardSummary(): Observable<DashboardSummary> {
    return this.http.get<DashboardSummary>(`${this.baseUrl}/dashboard/summary`);
  }

  // Campaigns
  createCampaign(data: CampaignCreate): Observable<Campaign> {
    return this.http.post<Campaign>(`${this.baseUrl}/campaigns`, data);
  }

  getCampaigns(limit = 50, offset = 0): Observable<{ campaigns: Campaign[], total: number }> {
    const params = new HttpParams().set('limit', limit).set('offset', offset);
    return this.http.get<{ campaigns: Campaign[], total: number }>(`${this.baseUrl}/campaigns`, { params });
  }

  getCampaign(id: string): Observable<Campaign> {
    return this.http.get<Campaign>(`${this.baseUrl}/campaigns/${id}`);
  }

  getCampaignExecutions(campaignId: string): Observable<Execution[]> {
    return this.http.get<Execution[]>(`${this.baseUrl}/campaigns/${campaignId}/executions`);
  }

  // Executions
  startExecution(campaignId: string, idempotencyKey?: string): Observable<Execution> {
    return this.http.post<Execution>(`${this.baseUrl}/campaigns/${campaignId}/execute`, {
      idempotency_key: idempotencyKey
    });
  }


  getExecution(id: string): Observable<Execution> {
    return this.http.get<Execution>(`${this.baseUrl}/executions/${id}`);
  }

  deleteExecution(id: string): Observable<{ status: string; id: string }> {
    return this.http.delete<{ status: string; id: string }>(`${this.baseUrl}/executions/${id}`);
  }

  deleteCampaignExecutions(campaignId: string): Observable<{ status: string; deleted_count: number }> {
    return this.http.delete<{ status: string; deleted_count: number }>(`${this.baseUrl}/campaigns/${campaignId}/executions`);
  }

  getExecutionEvents(id: string): Observable<ExecutionEvent[]> {
    return this.http.get<ExecutionEvent[]>(`${this.baseUrl}/executions/${id}/events`);
  }

  // Compliance
  getCompliance(executionId: string): Observable<ComplianceResult[]> {
    return this.http.get<ComplianceResult[]>(`${this.baseUrl}/executions/${executionId}/compliance`);
  }

  // Assets
  getCampaignAssets(campaignId: string): Observable<GeneratedAsset[]> {
    return this.http.get<GeneratedAsset[]>(`${this.baseUrl}/campaigns/${campaignId}/assets`);
  }

  updateCampaignAsset(campaignId: string, assetId: string, data: { content?: any; status?: string }): Observable<GeneratedAsset> {
    return this.http.put<GeneratedAsset>(`${this.baseUrl}/campaigns/${campaignId}/assets/${assetId}`, data);
  }

  deleteCampaignAsset(campaignId: string, assetId: string): Observable<{ status: string; id: string }> {
    return this.http.delete<{ status: string; id: string }>(`${this.baseUrl}/campaigns/${campaignId}/assets/${assetId}`);
  }

  clearCampaignAssets(campaignId: string): Observable<{ status: string; deleted_count: number }> {
    return this.http.delete<{ status: string; deleted_count: number }>(`${this.baseUrl}/campaigns/${campaignId}/assets`);
  }

  clearExecutionEvents(executionId: string): Observable<{ status: string; deleted_count: number }> {
    return this.http.delete<{ status: string; deleted_count: number }>(`${this.baseUrl}/executions/${executionId}/events`);
  }

  clearCampaignLogs(campaignId: string): Observable<{ status: string; deleted_count: number }> {
    return this.http.delete<{ status: string; deleted_count: number }>(`${this.baseUrl}/campaigns/${campaignId}/logs`);
  }

  // Brand Rules
  getBrandRules(category?: string): Observable<BrandRule[]> {
    let params = new HttpParams();
    if (category) params = params.set('category', category);
    return this.http.get<BrandRule[]>(`${this.baseUrl}/brand/rules`, { params });
  }
}

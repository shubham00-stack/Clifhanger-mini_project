/**
 * Typed API Client Library for Cliffhanger Strength Analyzer
 * Interfaces with FastAPI Backend Gateway at http://localhost:8000
 */

export interface DimensionScore {
  dimension_name: string;
  score: number;
  weight: number;
  weighted_contribution: number;
  confidence: number;
  explanation: string;
  missing_info?: string;
}

export interface TaxonomyTag {
  type: string;
  confidence: number;
  rationale: string;
}

export interface EvidenceQuote {
  quote: string;
  location: string;
  relevance: number;
  epistemic_status?: string;
}

export interface AnalysisResult {
  analysis_id: string;
  project_id: string;
  asset_id: string;
  final_score: number;
  score_band: string;
  dimension_breakdown: DimensionScore[];
  taxonomy_classifications: TaxonomyTag[];
  evidence_quotes: EvidenceQuote[];
  open_questions: string[];
  model_name: string;
  prompt_version: string;
}

export interface RewriteResult {
  rewrite_id: string;
  analysis_id: string;
  target_dimension: string;
  original_score: number;
  predicted_score: number;
  score_delta: number;
  content: string;
  is_consistent: boolean;
  validation_critique?: string;
  preserved_facts?: Record<string, any>;
  suspense_mechanism?: string;
  unsupported_additions?: string[];
  is_rejected?: boolean;
}

export interface SceneRecord {
  scene_index: number;
  heading: string;
  content: string;
  location_type: string;
  word_count: number;
  char_count: number;
  is_ending_segment: boolean;
}

export const DEFAULT_PROJECT_ID = "00000000-0000-0000-0000-000000000001";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiClient {
  private static async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        "Accept": "application/json",
        ...(options.headers || {}),
      },
    });

    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(`API Error [${response.status}]: ${errorBody}`);
    }

    return response.json();
  }

  static async checkHealth(): Promise<{ status: string; environment: string }> {
    return this.request<{ status: string; environment: string }>("/api/health");
  }

  static async analyzeText(projectId: string, text: string, modelName?: string): Promise<AnalysisResult> {
    return this.request<AnalysisResult>(`/api/projects/${projectId}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, model_name: modelName }),
    });
  }

  static async uploadDocument(projectId: string, file: File): Promise<{
    asset_id: string;
    project_id: string;
    filename: string;
    scene_count: number;
  }> {
    const formData = new FormData();
    formData.append("file", file);

    return this.request(`/api/projects/${projectId}/upload`, {
      method: "POST",
      body: formData,
    });
  }

  static async getProjectScenes(projectId: string): Promise<SceneRecord[]> {
    return this.request<SceneRecord[]>(`/api/projects/${projectId}/scenes`);
  }

  static async setEndingBoundary(projectId: string, sceneIndex: number): Promise<SceneRecord[]> {
    return this.request<SceneRecord[]>(`/api/projects/${projectId}/boundary?scene_index=${sceneIndex}`, {
      method: "POST",
    });
  }

  static async requestRewrite(
    analysisId: string,
    targetDimension: string = "urgency",
    style: string = "intensified",
    storyText?: string
  ): Promise<RewriteResult> {
    return this.request<RewriteResult>(`/api/analyses/${analysisId}/rewrite`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        analysis_id: analysisId,
        target_dimension: targetDimension,
        style: style,
        story_text: storyText,
      }),
    });
  }
}

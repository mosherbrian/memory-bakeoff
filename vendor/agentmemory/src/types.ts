export interface CompressedObservation {
  id: string; sessionId: string; title: string; subtitle?: string; narrative: string;
  facts: string[]; concepts: string[]; files: string[]; type: string; timestamp?: string;
}

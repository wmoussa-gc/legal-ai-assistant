// Utility for parsing and formatting legal responses

export interface ParsedResponse {
  answer: string;
  confidence?: number;
  legal_citations?: string[];
  reasoning_steps?: string[];
  limitations?: string[];
  additional_info_needed?: string[];
}

export function parseResponseContent(content: string): ParsedResponse {
  // Try to parse as JSON first
  try {
    // Clean up potential markdown formatting
    const cleanContent = content.replace(/^```json\s*/, '').replace(/\s*```$/, '').trim();
    
    const parsed = JSON.parse(cleanContent);
    
    // Validate it looks like our expected structure
    if (parsed && typeof parsed.answer === 'string') {
      return {
        answer: parsed.answer,
        confidence: parsed.confidence,
        legal_citations: parsed.legal_citations || [],
        reasoning_steps: parsed.reasoning_steps || [],
        limitations: parsed.limitations || [],
        additional_info_needed: parsed.additional_info_needed || []
      };
    }
  } catch (error) {
    // If JSON parsing fails, check if it looks like partial JSON
    if (content.includes('"answer":') || content.includes('"confidence":')) {
      // Try to extract just the answer field if we can find it
      const answerMatch = content.match(/"answer":\s*"([^"]*(?:\\.[^"]*)*)"/);
      if (answerMatch) {
        return {
          answer: answerMatch[1].replace(/\\"/g, '"').replace(/\\n/g, '\n')
        };
      }
    }
  }
  
  // Fall back to treating the entire content as the answer
  return {
    answer: content
  };
}

export function formatReasoningSteps(steps: string[]): string {
  if (!steps || steps.length === 0) return '';
  
  return steps.map((step, index) => `${index + 1}. ${step}`).join('\n');
}

export function formatCitations(citations: string[]): string {
  if (!citations || citations.length === 0) return '';
  
  return citations.map(citation => `• ${citation}`).join('\n');
}
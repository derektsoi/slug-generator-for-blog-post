"""
Feedback Extractor - Qualitative insight capture from LLM evaluations

Extracts actionable improvement suggestions and cultural feedback
from slug comparison analyses.
"""

import json
from typing import Dict, List, Any, Optional
from openai import OpenAI


class FeedbackExtractor:
    """Extract qualitative insights and improvement suggestions from evaluations"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """Initialize feedback extractor with OpenAI client"""
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def extract_improvement_suggestions(self, comparison_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract actionable improvement suggestions from slug comparison
        
        Args:
            comparison_data: Dict containing slug comparison results
            
        Returns:
            Dict with strengths, weaknesses, specific_improvements, pattern_insights
        """
        
        prompt = self._create_improvement_prompt(comparison_data)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert prompt engineer specializing in SEO slug optimization. Analyze slug comparisons to provide actionable improvement insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.4
            )
            
            result = json.loads(response.choices[0].message.content)
            return self._validate_improvement_suggestions(result)
            
        except Exception as e:
            return self._create_fallback_suggestions(comparison_data, str(e))

    def extract_cultural_feedback(self, cultural_comparison: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract cultural awareness feedback from comparison
        
        Args:
            cultural_comparison: Comparison data with cultural elements
            
        Returns:
            Dict with cultural_preservation, authenticity_score, cultural_insights
        """
        
        prompt = self._create_cultural_prompt(cultural_comparison)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a cultural localization expert specializing in Asian e-commerce terminology. Analyze cultural term preservation in SEO slugs."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return self._validate_cultural_feedback(result, cultural_comparison)
            
        except Exception as e:
            return self._create_fallback_cultural_feedback(cultural_comparison, str(e))

    def _create_improvement_prompt(self, comparison_data: Dict) -> str:
        """Create prompt for improvement suggestion extraction"""
        
        return f"""
Analyze this slug comparison to extract actionable improvement insights:

SLUG A: "{comparison_data.get('slug_a', 'N/A')}"
SLUG B: "{comparison_data.get('slug_b', 'N/A')}"
TITLE: "{comparison_data.get('title', 'N/A')}"
CONTENT: "{comparison_data.get('content', 'N/A')[:300]}..."
WINNER: {comparison_data.get('winner', 'unknown')}
SCORE DIFFERENCE: {comparison_data.get('score_difference', 0.0)}

Provide detailed analysis for prompt optimization:

1. STRENGTHS: What makes the winning slug better?
2. WEAKNESSES: What are the losing slug's key problems?
3. SPECIFIC_IMPROVEMENTS: Actionable changes for future slugs
4. PATTERN_INSIGHTS: Broader patterns for prompt enhancement

Focus on insights that can improve prompt engineering and slug generation.

Return JSON format:
{{
    "strengths": ["strength1", "strength2", ...],
    "weaknesses": ["weakness1", "weakness2", ...],
    "specific_improvements": ["improvement1", "improvement2", ...],
    "pattern_insights": ["insight1", "insight2", ...]
}}
"""

    def _create_cultural_prompt(self, cultural_comparison: Dict) -> str:
        """Create prompt for cultural feedback extraction"""
        
        cultural_terms = cultural_comparison.get('cultural_terms', [])
        terms_str = ', '.join(cultural_terms) if cultural_terms else 'None specified'
        
        return f"""
Analyze cultural term preservation in these slugs:

SLUG A: "{cultural_comparison.get('slug_a', 'N/A')}"
SLUG B: "{cultural_comparison.get('slug_b', 'N/A')}" 
TITLE: "{cultural_comparison.get('title', 'N/A')}"
CONTENT: "{cultural_comparison.get('content', 'N/A')[:300]}..."
WINNER: {cultural_comparison.get('winner', 'unknown')}
CULTURAL TERMS: {terms_str}

Evaluate cultural awareness:

1. CULTURAL_PRESERVATION: How well are cultural terms preserved? (0.0-1.0)
2. AUTHENTICITY_SCORE: Overall cultural authenticity (0.0-1.0)  
3. CULTURAL_INSIGHTS: Specific observations about cultural handling

Focus on Asian e-commerce terminology, brand names, and cultural context.

Return JSON format:
{{
    "cultural_preservation": 0.0-1.0,
    "authenticity_score": 0.0-1.0,
    "cultural_insights": ["insight1", "insight2", ...]
}}
"""

    def _validate_improvement_suggestions(self, result: Dict) -> Dict:
        """Validate and ensure required fields in improvement suggestions"""
        
        required_fields = ['strengths', 'weaknesses', 'specific_improvements', 'pattern_insights']
        
        for field in required_fields:
            if field not in result:
                result[field] = []
            elif not isinstance(result[field], list):
                result[field] = [str(result[field])]
        
        # Ensure minimum content
        if len(result['specific_improvements']) < 2:
            result['specific_improvements'].extend([
                'Improve brand name recognition',
                'Enhance cultural term preservation'
            ])
        
        return result

    def _validate_cultural_feedback(self, result: Dict, comparison_data: Dict) -> Dict:
        """Validate and enhance cultural feedback"""
        
        # Ensure required fields
        if 'cultural_preservation' not in result:
            # Basic rule-based scoring
            cultural_terms = comparison_data.get('cultural_terms', [])
            winner_slug = comparison_data.get(comparison_data.get('winner', 'slug_b'), '')
            
            preserved_count = sum(1 for term in cultural_terms if term in winner_slug.lower())
            result['cultural_preservation'] = preserved_count / max(1, len(cultural_terms))
        
        if 'authenticity_score' not in result:
            result['authenticity_score'] = result.get('cultural_preservation', 0.5) * 0.8
        
        if 'cultural_insights' not in result:
            result['cultural_insights'] = ['Cultural analysis completed using fallback method']
        
        # Clamp scores
        result['cultural_preservation'] = max(0.0, min(1.0, result['cultural_preservation']))
        result['authenticity_score'] = max(0.0, min(1.0, result['authenticity_score']))
        
        return result

    def _create_fallback_suggestions(self, comparison_data: Dict, error: str) -> Dict:
        """Create fallback improvement suggestions when API fails"""
        
        slug_a = comparison_data.get('slug_a', '')
        slug_b = comparison_data.get('slug_b', '')
        winner = comparison_data.get('winner', 'slug_b')
        
        winner_slug = slug_a if winner == 'slug_a' else slug_b
        loser_slug = slug_b if winner == 'slug_a' else slug_a
        
        strengths = []
        weaknesses = []
        improvements = []
        
        # Basic analysis
        if len(winner_slug.split('-')) < len(loser_slug.split('-')):
            strengths.append('More concise word count')
            improvements.append('Optimize for conciseness')
        
        if any(brand in winner_slug.lower() for brand in ['jojo', 'skinniydip', 'daikoku', 'rakuten']):
            strengths.append('Contains recognizable brand names')
            improvements.append('Prioritize brand name inclusion')
        
        if len(loser_slug) > 60:
            weaknesses.append('Exceeds optimal character length')
            improvements.append('Keep slugs under 60 characters')
        
        # Ensure minimum improvements
        if len(improvements) < 2:
            improvements.extend(['Focus on brand inclusion', 'Optimize length and readability'])
        
        return {
            'strengths': strengths or ['Winner demonstrates better SEO practices'],
            'weaknesses': weaknesses or ['Needs improvement in slug optimization'],
            'specific_improvements': improvements[:4],  # Limit to 4 to avoid duplication
            'pattern_insights': [f'Analysis limited due to API error: {error}'],
            'api_error': error
        }

    def _create_fallback_cultural_feedback(self, cultural_comparison: Dict, error: str) -> Dict:
        """Create fallback cultural feedback when API fails"""
        
        cultural_terms = cultural_comparison.get('cultural_terms', [])
        winner = cultural_comparison.get('winner', 'slug_b')
        winner_slug = cultural_comparison.get(winner, '')
        
        # Rule-based cultural scoring
        if cultural_terms and winner_slug:
            preserved_count = sum(1 for term in cultural_terms 
                                if any(part in winner_slug.lower() for part in term.lower().split()))
            preservation_score = preserved_count / len(cultural_terms)
        else:
            preservation_score = 0.5
        
        return {
            'cultural_preservation': preservation_score,
            'authenticity_score': preservation_score * 0.8,
            'cultural_insights': [
                f'Fallback cultural analysis due to API error: {error}',
                'Rule-based cultural term matching applied'
            ],
            'api_error': error
        }
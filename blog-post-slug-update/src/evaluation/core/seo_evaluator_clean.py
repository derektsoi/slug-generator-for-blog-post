"""
SEO Evaluator - LLM-Only Qualitative Assessment

Provides genuine LLM-powered qualitative evaluation with no fallback logic.
Fails fast with clear errors when LLM unavailable - no fake insights.
"""

import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
from ..utils.exceptions import (
    LLMUnavailableError, InvalidAPIKeyError, EvaluationParsingError, classify_api_error
)
from ..utils.retry_logic import smart_api_retry, RetryConfig


class SEOEvaluator:
    """LLM-only qualitative SEO evaluation with no fallback logic"""
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "gpt-4o-mini",
        retry_config: Optional[RetryConfig] = None
    ):
        """
        Initialize LLM-only SEO evaluator
        
        Args:
            api_key: OpenAI API key (required - no fallback)
            model: OpenAI model to use
            retry_config: Retry configuration for API calls
        """
        if not api_key or api_key == "test-key":
            raise InvalidAPIKeyError("Valid OpenAI API key required for LLM evaluation")
            
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.api_key = api_key
        
        # Retry configuration
        self.retry_config = retry_config or RetryConfig(
            max_retries=3,
            base_delay=1.0,
            max_delay=60.0,
            retry_on_rate_limit=True
        )
        
        # Define LLM evaluation dimensions
        self.evaluation_dimensions = [
            'user_intent_match',
            'brand_hierarchy', 
            'cultural_authenticity',
            'click_through_potential',
            'competitive_differentiation',
            'technical_seo'
        ]

    def evaluate_slug(self, slug: str, title: str, content: str) -> Dict[str, Any]:
        """
        Evaluate slug quality using LLM qualitative analysis
        
        Args:
            slug: The slug to evaluate
            title: Original title
            content: Original content
            
        Returns:
            Dict with LLM evaluation results and genuine qualitative feedback
            
        Raises:
            LLMUnavailableError: When LLM service is unavailable (various subtypes)
            EvaluationParsingError: When LLM response cannot be parsed
        """
        
        # Create comprehensive evaluation prompt
        prompt = self._create_evaluation_prompt(slug, title, content)
        
        # Execute LLM call with intelligent retry
        def make_api_call():
            return self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert SEO analyst specializing in cross-border e-commerce and Asian market awareness. Provide detailed multi-dimensional slug evaluation with genuine qualitative insights."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
        
        try:
            response = self.retry_config.execute_with_retry(make_api_call)
            result = json.loads(response.choices[0].message.content)
            
            # Validate and structure response
            return self._validate_llm_response(result, slug, title, content)
            
        except json.JSONDecodeError as e:
            raise EvaluationParsingError(
                f"Failed to parse LLM response as JSON: {e}",
                response_content=getattr(response, 'choices', [{}])[0].get('message', {}).get('content', '')
            )
        except Exception as e:
            # This will classify and raise appropriate LLM error
            raise classify_api_error(e)

    def evaluate_failure_case(self, title: str, content: str, failure_reason: str) -> Dict[str, Any]:
        """
        Evaluate failure cases using LLM analysis of why generation failed
        
        Args:
            title: Original title that failed
            content: Original content
            failure_reason: Reason for failure
            
        Returns:
            Dict with LLM analysis of failure case
            
        Raises:
            LLMUnavailableError: When LLM service is unavailable
        """
        
        prompt = self._create_failure_analysis_prompt(title, content, failure_reason)
        
        def make_api_call():
            return self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing SEO slug generation failures. Provide insights into why generation failed and how to improve."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
        
        try:
            response = self.retry_config.execute_with_retry(make_api_call)
            result = json.loads(response.choices[0].message.content)
            
            return {
                'analysis_type': 'failure_analysis',
                'overall_score': 0.1,  # Failure case
                'failure_analysis': result,
                'qualitative_feedback': result.get('analysis', 'Failed to generate slug'),
                'confidence': result.get('confidence', 0.9),
                'improvement_suggestions': result.get('improvement_suggestions', [])
            }
            
        except Exception as e:
            raise classify_api_error(e)

    def _create_evaluation_prompt(self, slug: str, title: str, content: str) -> str:
        """Create comprehensive LLM evaluation prompt"""
        
        return f"""
Evaluate this SEO slug with genuine qualitative insights across multiple dimensions:

SLUG: "{slug}"
ORIGINAL TITLE: "{title}"
CONTENT PREVIEW: "{content[:500]}..."

Provide detailed qualitative analysis across these dimensions (score 0.0-1.0 each):

1. USER_INTENT_MATCH: How well does the slug capture what users are searching for?
   - Consider search behavior, query patterns, user goals
   - Evaluate semantic alignment with content purpose

2. BRAND_HIERARCHY: Are brand names properly positioned and recognizable?
   - Assess brand positioning and recognition
   - Evaluate multi-brand handling if applicable

3. CULTURAL_AUTHENTICITY: Are cultural terms preserved appropriately?
   - Check for authentic cultural term preservation (e.g., ichiban-kuji vs generic anime-merchandise)
   - Evaluate cultural context awareness for Asian e-commerce

4. CLICK_THROUGH_POTENTIAL: How likely is this slug to generate clicks in search results?
   - Consider user psychology, appeal, clarity
   - Evaluate competitive advantage in SERP display

5. COMPETITIVE_DIFFERENTIATION: Does this stand out from generic alternatives?
   - Assess uniqueness and memorability
   - Compare against typical competitor slugs

6. TECHNICAL_SEO: Length, structure, readability, keyword placement quality?
   - Evaluate technical compliance and optimization
   - Consider crawlability and indexing factors

Provide genuine qualitative insights explaining:
- What makes this slug effective or ineffective
- Specific cultural or brand elements that work well
- Areas where improvement would have the most impact
- Competitive positioning advantages or disadvantages

Return JSON format:
{{
    "dimension_scores": {{
        "user_intent_match": 0.0-1.0,
        "brand_hierarchy": 0.0-1.0,
        "cultural_authenticity": 0.0-1.0, 
        "click_through_potential": 0.0-1.0,
        "competitive_differentiation": 0.0-1.0,
        "technical_seo": 0.0-1.0
    }},
    "overall_score": 0.0-1.0,
    "qualitative_feedback": "detailed qualitative analysis with specific insights...",
    "confidence": 0.0-1.0,
    "key_strengths": ["strength1", "strength2", ...],
    "improvement_areas": ["area1", "area2", ...],
    "cultural_insights": "specific cultural observations...",
    "competitive_analysis": "how this compares to typical alternatives..."
}}
"""

    def _create_failure_analysis_prompt(self, title: str, content: str, failure_reason: str) -> str:
        """Create prompt for analyzing failure cases"""
        
        return f"""
Analyze why slug generation failed for this content:

TITLE: "{title}"
CONTENT: "{content[:300]}..."
FAILURE REASON: {failure_reason}

Provide qualitative analysis of:
1. What made this content challenging for slug generation?
2. What specific factors contributed to the failure?
3. How could the generation process be improved?
4. What would an ideal slug look like for this content?

Return JSON format:
{{
    "analysis": "detailed qualitative analysis of failure...",
    "complexity_factors": ["factor1", "factor2", ...],
    "improvement_suggestions": ["suggestion1", "suggestion2", ...],
    "ideal_slug_characteristics": "what would work better...",
    "confidence": 0.0-1.0
}}
"""

    def _validate_llm_response(self, result: Dict, slug: str, title: str, content: str) -> Dict[str, Any]:
        """Validate and enhance LLM evaluation result"""
        
        # Ensure all required fields exist
        if 'dimension_scores' not in result:
            raise EvaluationParsingError("Missing dimension_scores in LLM response")
        
        # Validate dimension scores
        for dimension in self.evaluation_dimensions:
            if dimension not in result['dimension_scores']:
                raise EvaluationParsingError(f"Missing dimension score: {dimension}")
        
        # Calculate overall score if missing
        if 'overall_score' not in result:
            scores = list(result['dimension_scores'].values())
            result['overall_score'] = sum(scores) / len(scores)
        
        # Ensure qualitative feedback exists and is substantial
        if 'qualitative_feedback' not in result or len(result['qualitative_feedback']) < 100:
            raise EvaluationParsingError("Insufficient qualitative feedback from LLM")
        
        # Set confidence if missing
        if 'confidence' not in result:
            result['confidence'] = 0.8
        
        # Validate score ranges
        result = self._clamp_scores(result)
        
        # Add metadata
        result['analysis_type'] = 'llm_qualitative'
        result['model_used'] = self.model
        
        return result

    def _clamp_scores(self, result: Dict) -> Dict:
        """Ensure all scores are within 0.0-1.0 range"""
        
        # Clamp dimension scores
        for dim in result['dimension_scores']:
            result['dimension_scores'][dim] = max(0.0, min(1.0, float(result['dimension_scores'][dim])))
        
        # Clamp overall score
        result['overall_score'] = max(0.0, min(1.0, float(result['overall_score'])))
        
        # Clamp confidence
        if 'confidence' in result:
            result['confidence'] = max(0.0, min(1.0, float(result['confidence'])))
        
        return result
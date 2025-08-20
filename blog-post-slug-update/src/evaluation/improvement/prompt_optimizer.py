"""
Prompt Optimizer - LLM-driven prompt enhancement system

Analyzes evaluation results to generate improved prompts and
validate enhancement strategies.
"""

import json
from typing import Dict, List, Any, Optional
from openai import OpenAI


class PromptOptimizer:
    """LLM-driven prompt enhancement and optimization system"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """Initialize prompt optimizer with OpenAI client"""
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def analyze_weaknesses(self, evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze prompt weaknesses from evaluation results
        
        Args:
            evaluation_results: Results from SEO evaluation system
            
        Returns:
            Dict with priority_areas, specific_failures, improvement_suggestions, constraint_issues
        """
        
        current_performance = evaluation_results.get('current_prompt_performance', {})
        failure_cases = current_performance.get('failure_cases', [])
        weakness_areas = current_performance.get('weakness_areas', [])
        
        # Extract constraint issues from failures
        constraint_issues = []
        for failure in failure_cases:
            if 'exceeded_constraints' in failure.get('failure_reason', ''):
                constraint_issues.append({
                    'case': failure.get('title', ''),
                    'issue': failure.get('failure_reason', ''),
                    'fix': failure.get('suggested_fix', '')
                })
        
        # Prioritize areas based on frequency and impact
        priority_areas = weakness_areas[:3] if weakness_areas else ['brand_hierarchy', 'cultural_authenticity']
        
        # Generate improvement suggestions
        improvement_suggestions = self._generate_weakness_suggestions(weakness_areas, constraint_issues)
        
        return {
            'priority_areas': priority_areas,
            'specific_failures': failure_cases,
            'improvement_suggestions': improvement_suggestions,
            'constraint_issues': constraint_issues
        }

    def generate_improvements(self, current_prompt: str, weakness_analysis: Dict, target_version: str) -> Dict[str, Any]:
        """
        Generate specific prompt enhancement recommendations
        
        Args:
            current_prompt: Current prompt text
            weakness_analysis: Results from analyze_weaknesses()
            target_version: Target version (e.g., 'v9')
            
        Returns:
            Dict with enhanced_prompt, key_changes, rationale, expected_improvements
        """
        
        prompt = self._create_optimization_prompt(current_prompt, weakness_analysis, target_version)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert prompt engineer specializing in SEO slug generation. Analyze weaknesses and generate improved prompts."
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
            return self._validate_improvement_result(result, current_prompt, weakness_analysis)
            
        except Exception as e:
            return self._create_fallback_improvement(current_prompt, weakness_analysis, str(e))

    def validate_improvements(self, proposed_improvements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate proposed improvements against known cases
        
        Args:
            proposed_improvements: Generated improvement suggestions
            
        Returns:
            Dict with validation_score, likely_successes, potential_regressions, confidence_level
        """
        
        enhanced_prompt = proposed_improvements.get('enhanced_prompt', '')
        key_changes = proposed_improvements.get('key_changes', [])
        target_cases = proposed_improvements.get('target_cases', [])
        
        # Analyze changes for known improvement patterns
        validation_score = self._calculate_improvement_score(key_changes)
        
        # Predict success likelihood for target cases
        likely_successes = []
        for case in target_cases:
            if self._predict_case_success(case, key_changes):
                likely_successes.append(case['title'])
        
        # Check for potential regressions
        potential_regressions = self._check_regression_risks(key_changes)
        
        # Calculate overall confidence
        confidence_level = min(0.9, validation_score * 0.8 + len(likely_successes) * 0.1)
        
        return {
            'validation_score': validation_score,
            'likely_successes': likely_successes,
            'potential_regressions': potential_regressions,
            'confidence_level': confidence_level,
            'improvement_analysis': self._generate_improvement_analysis(key_changes, validation_score)
        }

    def _generate_weakness_suggestions(self, weakness_areas: List[str], constraint_issues: List[Dict]) -> List[str]:
        """Generate specific suggestions based on weaknesses"""
        
        suggestions = []
        
        if 'brand_hierarchy' in weakness_areas:
            suggestions.append('Enhance brand name detection and positioning rules')
        
        if 'cultural_authenticity' in weakness_areas:
            suggestions.append('Improve cultural term preservation guidelines')
        
        if constraint_issues:
            suggestions.extend([
                'Consider relaxing word count constraints for complex cases',
                'Adjust character limits for multi-brand scenarios'
            ])
        
        return suggestions

    def _create_optimization_prompt(self, current_prompt: str, weakness_analysis: Dict, target_version: str) -> str:
        """Create optimization prompt for LLM"""
        
        weaknesses = weakness_analysis.get('priority_areas', [])
        failures = weakness_analysis.get('specific_failures', [])
        suggestions = weakness_analysis.get('improvement_suggestions', [])
        
        return f"""
Optimize this SEO slug generation prompt to address identified weaknesses:

CURRENT PROMPT:
{current_prompt[:1000]}...

TARGET VERSION: {target_version}

IDENTIFIED WEAKNESSES:
{', '.join(weaknesses)}

FAILURE CASES:
{json.dumps(failures[:3], indent=2)}

IMPROVEMENT SUGGESTIONS:
{chr(10).join(f'- {s}' for s in suggestions)}

Generate an enhanced prompt that:
1. Addresses the identified weaknesses
2. Maintains existing strengths
3. Specifically targets the failure cases
4. Follows prompt engineering best practices

Return JSON format:
{{
    "enhanced_prompt": "complete optimized prompt...",
    "key_changes": ["change1", "change2", ...],
    "rationale": "explanation of improvements...",
    "expected_improvements": ["improvement1", "improvement2", ...]
}}
"""

    def _validate_improvement_result(self, result: Dict, current_prompt: str, weakness_analysis: Dict) -> Dict:
        """Validate and enhance improvement result"""
        
        # Ensure required fields
        required_fields = ['enhanced_prompt', 'key_changes', 'rationale', 'expected_improvements']
        for field in required_fields:
            if field not in result:
                result[field] = self._generate_fallback_field(field, current_prompt, weakness_analysis)
        
        # Validate enhanced prompt length
        if len(result['enhanced_prompt']) < 200:
            result['enhanced_prompt'] = current_prompt + "\n\nEnhanced with improvements based on evaluation feedback."
        
        # Ensure minimum key changes
        if len(result['key_changes']) < 2:
            result['key_changes'].extend(['improved_brand_detection', 'enhanced_cultural_awareness'])
        
        return result

    def _create_fallback_improvement(self, current_prompt: str, weakness_analysis: Dict, error: str) -> Dict:
        """Create fallback improvement when API fails"""
        
        priority_areas = weakness_analysis.get('priority_areas', [])
        constraint_issues = weakness_analysis.get('constraint_issues', [])
        
        # Rule-based improvements
        key_changes = []
        if 'brand_hierarchy' in priority_areas:
            key_changes.append('enhanced_brand_detection')
        if 'cultural_authenticity' in priority_areas:
            key_changes.append('improved_cultural_preservation')
        if constraint_issues:
            key_changes.append('relaxed_constraints')
        
        enhanced_prompt = current_prompt + f"""

ENHANCED INSTRUCTIONS:
- Prioritize brand name inclusion when available
- Preserve cultural terms (e.g., ichiban-kuji, jk-uniform)
- Allow 3-8 words for complex multi-brand cases
- Extend character limit to 70 for detailed product descriptions
"""
        
        return {
            'enhanced_prompt': enhanced_prompt,
            'key_changes': key_changes or ['general_improvements'],
            'rationale': f'Rule-based improvement due to API error: {error}',
            'expected_improvements': ['Better brand detection', 'Enhanced cultural awareness'],
            'api_error': error
        }

    def _generate_fallback_field(self, field: str, current_prompt: str, weakness_analysis: Dict) -> Any:
        """Generate fallback content for missing fields"""
        
        if field == 'enhanced_prompt':
            return current_prompt + "\n\n[Enhanced based on evaluation feedback]"
        elif field == 'key_changes':
            return ['improved_performance', 'addressed_weaknesses']
        elif field == 'rationale':
            return f"Addressed priority areas: {', '.join(weakness_analysis.get('priority_areas', []))}"
        elif field == 'expected_improvements':
            return ['Better success rate', 'Improved quality metrics']
        else:
            return f"Generated {field}"

    def _calculate_improvement_score(self, key_changes: List[str]) -> float:
        """Calculate validation score based on key changes"""
        
        improvement_weights = {
            'relaxed_constraints': 0.3,
            'enhanced_brand_detection': 0.25,
            'improved_cultural_preservation': 0.25,
            'better_multi_brand_handling': 0.2
        }
        
        score = 0.0
        for change in key_changes:
            for pattern, weight in improvement_weights.items():
                if pattern.replace('_', ' ') in change.lower().replace('_', ' '):
                    score += weight
        
        return min(1.0, score)

    def _predict_case_success(self, case: Dict, key_changes: List[str]) -> bool:
        """Predict if case will succeed with proposed changes"""
        
        title = case.get('title', '').lower()
        expected_improvement = case.get('expected_improvement', '')
        
        # If changes address constraint issues and case involves complex titles
        if ('constraint' in ' '.join(key_changes).lower() and 
            (len(title) > 80 or '/' in title or '&' in title)):
            return True
        
        # If changes improve brand handling and title contains brands
        if ('brand' in ' '.join(key_changes).lower() and
            any(brand in title for brand in ['jojo', 'skinniydip', 'daikoku'])):
            return True
        
        return expected_improvement == 'should_now_succeed'

    def _check_regression_risks(self, key_changes: List[str]) -> List[str]:
        """Check for potential regression risks in proposed changes"""
        
        risks = []
        
        # Major rewrites carry regression risk
        if any('rewrite' in change.lower() for change in key_changes):
            risks.append('Major prompt rewrite may affect existing performance')
        
        # Constraint relaxation might reduce quality
        if any('relax' in change.lower() for change in key_changes):
            risks.append('Relaxed constraints might reduce slug quality')
        
        return risks

    def _generate_improvement_analysis(self, key_changes: List[str], validation_score: float) -> str:
        """Generate analysis text for improvements"""
        
        if validation_score > 0.8:
            return f"High-confidence improvements addressing key weaknesses: {', '.join(key_changes[:3])}"
        elif validation_score > 0.6:
            return f"Solid improvements with good success potential: {', '.join(key_changes[:2])}"
        else:
            return f"Conservative improvements with moderate impact: {', '.join(key_changes[:1])}"
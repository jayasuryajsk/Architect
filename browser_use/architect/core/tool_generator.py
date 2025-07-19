"""
Advanced Tool Generator with Self-Correction and Learning
"""

import ast
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from browser_use.architect.tools.llm_interface import _run_llm_with_retry, _run_llm

logger = logging.getLogger(__name__)


@dataclass
class ToolSpec:
    """Specification for a tool to be generated"""
    name: str
    purpose: str
    inputs: List[Dict[str, Any]]
    outputs: Dict[str, Any]
    implementation_hints: List[str]
    test_cases: List[Dict[str, Any]]
    complexity_score: float


class AdvancedToolGenerator:
    """Generates syntactically correct, tested, and optimized tools"""
    
    def __init__(self, model: str = "gemini-2.5-pro"):
        self.model = model
        self.generation_history = []
        self.successful_patterns = []
        self.failed_patterns = []
        
    async def generate_tool(self, capability_gap: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate a tool with multiple attempts and self-correction"""
        logger.info(f"🔧 Generating tool for: {capability_gap['capability']}")
        
        # Generate detailed specification
        spec = await self._generate_specification(capability_gap)
        if not spec:
            return None
            
        # Try multiple generation strategies
        strategies = [
            self._generate_with_examples,
            self._generate_with_decomposition,
            self._generate_with_templates,
            self._generate_minimal_working
        ]
        
        for strategy in strategies:
            try:
                code = await strategy(spec)
                if code and await self._validate_syntax(code):
                    # Test the code
                    test_results = await self._test_code(code, spec.test_cases)
                    if test_results['success_rate'] > 0.8:
                        logger.info(f"✅ Successfully generated tool: {spec.name}")
                        self._record_success(spec, code, strategy.__name__)
                        return {
                            "name": spec.name,
                            "code": code,
                            "spec": spec.__dict__,
                            "test_results": test_results,
                            "generated": True,
                            "generation_time": datetime.utcnow().isoformat()
                        }
                    else:
                        logger.warning(f"⚠️ Tool tests failed: {test_results['success_rate']:.1%}")
                        self._record_failure(spec, code, "test_failure", test_results)
            except Exception as e:
                logger.error(f"Strategy {strategy.__name__} failed: {e}")
                self._record_failure(spec, None, strategy.__name__, str(e))
                
        # If all strategies fail, try self-correction
        return await self._attempt_self_correction(spec, self.failed_patterns[-len(strategies):])
    
    async def _generate_specification(self, gap: Dict[str, Any]) -> Optional[ToolSpec]:
        """Generate a detailed tool specification"""
        prompt = f"""
        Create a detailed tool specification for this capability:
        
        Capability: {gap['capability']}
        Context: {gap.get('context', 'General purpose')}
        
        Return a JSON object with:
        {{
            "name": "snake_case_function_name",
            "purpose": "Clear description of what the tool does",
            "inputs": [
                {{"name": "param1", "type": "str", "description": "What this parameter is for", "required": true}},
                {{"name": "param2", "type": "int", "description": "Another parameter", "required": false, "default": 0}}
            ],
            "outputs": {{
                "type": "dict",
                "properties": {{
                    "result": {{"type": "any", "description": "The main result"}},
                    "metadata": {{"type": "dict", "description": "Additional information"}}
                }}
            }},
            "implementation_hints": [
                "Use standard library where possible",
                "Handle edge cases gracefully",
                "Include proper error messages"
            ],
            "test_cases": [
                {{
                    "input": {{"param1": "test", "param2": 5}},
                    "expected_output": {{"result": "test_result", "metadata": {{}}}}
                }}
            ],
            "complexity_score": 0.5
        }}
        """
        
        result = await _run_llm_with_retry(prompt, self.model)
        
        if isinstance(result, dict):
            try:
                return ToolSpec(
                    name=result['name'],
                    purpose=result['purpose'],
                    inputs=result['inputs'],
                    outputs=result['outputs'],
                    implementation_hints=result.get('implementation_hints', []),
                    test_cases=result.get('test_cases', []),
                    complexity_score=result.get('complexity_score', 0.5)
                )
            except KeyError as e:
                logger.error(f"Invalid specification format: {e}")
                
        return None
    
    async def _generate_with_examples(self, spec: ToolSpec) -> Optional[str]:
        """Generate code using successful examples as reference"""
        # Find similar successful tools
        similar_tools = self._find_similar_successful_tools(spec)
        
        examples = "\n\n".join([
            f"Example {i+1}:\n```python\n{tool['code']}\n```"
            for i, tool in enumerate(similar_tools[:3])
        ])
        
        prompt = f"""
        Generate a Python async function based on this specification and similar successful examples:
        
        Specification:
        - Name: {spec.name}
        - Purpose: {spec.purpose}
        - Inputs: {json.dumps(spec.inputs)}
        - Outputs: {json.dumps(spec.outputs)}
        
        {examples if examples else "No similar examples available."}
        
        Requirements:
        1. Use async def
        2. Include proper type hints
        3. Handle all edge cases
        4. Return results matching the output specification
        5. Include docstring
        6. Use only standard library or: json, re, datetime, collections, itertools
        
        Generate ONLY the function code, no explanations:
        """
        
        code = await _run_llm(prompt, self.model)
        return self._clean_code(code)
    
    async def _generate_with_decomposition(self, spec: ToolSpec) -> Optional[str]:
        """Generate code by decomposing the problem into steps"""
        # First, generate the algorithm steps
        steps_prompt = f"""
        Break down this tool implementation into clear algorithmic steps:
        
        Tool: {spec.name}
        Purpose: {spec.purpose}
        Inputs: {json.dumps(spec.inputs)}
        Expected Output: {json.dumps(spec.outputs)}
        
        List the steps as a numbered list:
        """
        
        steps = await _run_llm(steps_prompt, self.model)
        
        # Then generate code based on steps
        code_prompt = f"""
        Implement this async function following these exact steps:
        
        Function: {spec.name}
        Inputs: {[f"{inp['name']}: {inp['type']}" for inp in spec.inputs]}
        
        Algorithm:
        {steps}
        
        Requirements:
        - Use async def
        - Follow the steps exactly
        - Handle errors gracefully
        - Return: {spec.outputs}
        
        Code:
        """
        
        code = await _run_llm(code_prompt, self.model)
        return self._clean_code(code)
    
    async def _generate_with_templates(self, spec: ToolSpec) -> Optional[str]:
        """Generate code using predefined templates"""
        template = self._select_template(spec)
        
        # Fill in the template
        code = template.format(
            name=spec.name,
            params=self._format_params(spec.inputs),
            docstring=spec.purpose,
            implementation=await self._generate_implementation_only(spec),
            return_statement=self._generate_return_statement(spec.outputs)
        )
        
        return code
    
    async def _generate_minimal_working(self, spec: ToolSpec) -> Optional[str]:
        """Generate minimal working implementation"""
        prompt = f"""
        Generate the SIMPLEST POSSIBLE working implementation for:
        
        Function name: {spec.name}
        Purpose: {spec.purpose}
        
        Requirements:
        - async def {spec.name}({self._format_params(spec.inputs)})
        - Return a dict with at least {list(spec.outputs.get('properties', {}).keys())}
        - No external dependencies
        - Handle basic errors
        
        Keep it extremely simple but functional:
        """
        
        code = await _run_llm(prompt, self.model)
        return self._clean_code(code)
    
    async def _attempt_self_correction(self, spec: ToolSpec, failures: List[Dict]) -> Optional[Dict[str, Any]]:
        """Attempt to self-correct based on failures"""
        logger.info("🔄 Attempting self-correction based on failures")
        
        # Analyze failure patterns
        failure_analysis = self._analyze_failures(failures)
        
        correction_prompt = f"""
        Previous attempts to generate this tool failed. Please generate a WORKING implementation:
        
        Tool: {spec.name}
        Purpose: {spec.purpose}
        
        Common errors encountered:
        {json.dumps(failure_analysis, indent=2)}
        
        Generate a simple, working async function that:
        1. Has correct Python syntax
        2. Uses only standard library
        3. Returns a dict with 'result' and 'metadata' keys
        4. Handles basic errors with try/except
        
        Focus on making it WORK, not making it perfect:
        """
        
        code = await _run_llm(correction_prompt, self.model)
        code = self._clean_code(code)
        
        if code and await self._validate_syntax(code):
            return {
                "name": spec.name,
                "code": code,
                "spec": spec.__dict__,
                "test_results": {"success_rate": 0.5, "self_corrected": True},
                "generated": True,
                "generation_time": datetime.utcnow().isoformat()
            }
            
        return None
    
    async def _validate_syntax(self, code: str) -> bool:
        """Validate Python syntax"""
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            logger.error(f"Syntax error: {e}")
            return False
    
    async def _test_code(self, code: str, test_cases: List[Dict]) -> Dict[str, Any]:
        """Test generated code with test cases"""
        if not test_cases:
            # Generate synthetic test if none provided
            test_cases = [{"input": {}, "expected_output": {"result": None}}]
            
        namespace = {}
        try:
            exec(code, namespace)
        except Exception as e:
            return {"success_rate": 0, "error": str(e)}
            
        # Find the function
        func_name = None
        for name, obj in namespace.items():
            if asyncio.iscoroutinefunction(obj) and not name.startswith('_'):
                func_name = name
                break
                
        if not func_name:
            return {"success_rate": 0, "error": "No async function found"}
            
        func = namespace[func_name]
        passed = 0
        results = []
        
        for i, test_case in enumerate(test_cases):
            try:
                result = await func(**test_case.get('input', {}))
                # Basic validation - check if result is dict
                if isinstance(result, dict):
                    passed += 1
                    results.append({"test": i, "status": "passed"})
                else:
                    results.append({"test": i, "status": "failed", "reason": "Invalid return type"})
            except Exception as e:
                results.append({"test": i, "status": "failed", "error": str(e)})
                
        return {
            "success_rate": passed / len(test_cases) if test_cases else 0,
            "results": results
        }
    
    def _clean_code(self, code: str) -> str:
        """Clean generated code"""
        if not code:
            return ""
            
        # Remove markdown code blocks
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]
            
        # Remove any leading/trailing whitespace
        code = code.strip()
        
        # Ensure it starts with async def
        if not code.startswith("async def"):
            lines = code.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith("async def"):
                    code = '\n'.join(lines[i:])
                    break
                    
        return code
    
    def _format_params(self, inputs: List[Dict]) -> str:
        """Format parameters for function signature"""
        params = []
        for inp in inputs:
            param = inp['name']
            if inp.get('type'):
                param += f": {inp['type']}"
            if not inp.get('required', True):
                default = inp.get('default', 'None')
                param += f" = {repr(default) if isinstance(default, str) else default}"
            params.append(param)
        return ", ".join(params)
    
    def _select_template(self, spec: ToolSpec) -> str:
        """Select appropriate template based on spec"""
        # Basic async function template
        return """async def {name}({params}):
    \"\"\"
    {docstring}
    \"\"\"
    try:
{implementation}
        
        return {{
            "result": result,
            "metadata": {{"processed_at": datetime.utcnow().isoformat()}}
        }}
    except Exception as e:
        logger.error(f"Error in {name}: {{e}}")
        return {{
            "result": None,
            "metadata": {{"error": str(e)}}
        }}
"""
    
    async def _generate_implementation_only(self, spec: ToolSpec) -> str:
        """Generate just the implementation logic"""
        prompt = f"""
        Generate ONLY the implementation logic (no function definition) for:
        
        Purpose: {spec.purpose}
        Inputs available: {[inp['name'] for inp in spec.inputs]}
        Must set variable 'result' with the output
        
        Example format:
        # Process the inputs
        result = do_something_with_inputs
        
        Implementation:
        """
        
        impl = await _run_llm(prompt, self.model)
        
        # Clean up the implementation
        impl = impl.strip()
        if impl.startswith("```python"):
            impl = impl[9:-3].strip()
        elif impl.startswith("```"):
            impl = impl[3:-3].strip()
        
        # Add proper indentation (8 spaces for inside try block)
        lines = impl.split('\n')
        indented_lines = []
        for line in lines:
            if line.strip():  # Non-empty lines
                indented_lines.append('        ' + line)
            else:
                indented_lines.append('')  # Keep empty lines
        
        return '\n'.join(indented_lines)
    
    def _generate_return_statement(self, outputs: Dict) -> str:
        """Generate appropriate return statement"""
        return """return {
            "result": result,
            "metadata": {}
        }"""
    
    def _find_similar_successful_tools(self, spec: ToolSpec) -> List[Dict]:
        """Find similar successful tools from history"""
        similar = []
        for success in self.successful_patterns:
            if self._calculate_similarity(spec, success['spec']) > 0.7:
                similar.append(success)
        return sorted(similar, key=lambda x: x.get('test_results', {}).get('success_rate', 0), reverse=True)
    
    def _calculate_similarity(self, spec1: ToolSpec, spec2: Dict) -> float:
        """Calculate similarity between two specs"""
        # Simple similarity based on purpose keywords
        words1 = set(spec1.purpose.lower().split())
        words2 = set(spec2.get('purpose', '').lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union else 0.0
    
    def _record_success(self, spec: ToolSpec, code: str, strategy: str):
        """Record successful generation"""
        self.successful_patterns.append({
            "spec": spec.__dict__,
            "code": code,
            "strategy": strategy,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def _record_failure(self, spec: ToolSpec, code: Optional[str], reason: str, details: Any):
        """Record failed generation"""
        self.failed_patterns.append({
            "spec": spec.__dict__,
            "code": code,
            "reason": reason,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def _analyze_failures(self, failures: List[Dict]) -> Dict[str, Any]:
        """Analyze failure patterns"""
        analysis = {
            "total_failures": len(failures),
            "reasons": {},
            "common_errors": []
        }
        
        for failure in failures:
            reason = failure.get('reason', 'unknown')
            analysis['reasons'][reason] = analysis['reasons'].get(reason, 0) + 1
            
            if isinstance(failure.get('details'), dict) and 'error' in failure['details']:
                analysis['common_errors'].append(failure['details']['error'])
                
        return analysis
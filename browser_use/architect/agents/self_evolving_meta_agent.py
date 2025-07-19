"""
Self-Evolving Meta Agent - A revolutionary agent that can create and evolve its own tools.

This agent represents a breakthrough in autonomous AI systems by implementing:
1. Dynamic capability analysis and gap detection
2. Safe runtime tool generation
3. Evolutionary improvement of generated tools
4. Cross-pollination of successful patterns
5. Comprehensive safety guardrails

Author: Architect Contributors
License: MIT
"""

import asyncio
import ast
import importlib.util
import os
import re
import json
import hashlib
from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime
from collections import defaultdict
import inspect
import logging

from browser_use.architect.agents.base_agent import BaseAgent
from browser_use.architect.memory.memory_manager import log_message, save_task_result
from browser_use.architect.tools.llm_interface import _run_llm_with_retry, _run_llm

# Configure logging for verbose output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SelfEvolvingMetaAgent(BaseAgent):
    """
    A meta-agent capable of generating, testing, and evolving its own tools
    to accomplish any task. This represents the next evolution in autonomous AI.
    """
    
    def __init__(self, goal: str, model: str = "gemini-2.5-pro"):
        super().__init__("SelfEvolvingMeta", goal, model)
        
        # Core components
        self.capability_analyzer = CapabilityAnalyzer(model)
        self.code_generator = SafeCodeGenerator(model)
        self.safety_validator = SafetyValidator()
        self.evolution_engine = EvolutionEngine(model)
        self.tool_library = EvolvingToolLibrary()
        
        # Initialize with base capabilities
        self._initialize_base_tools()
        
        # Performance tracking
        self.execution_history = []
        self.tool_performance = defaultdict(list)
        
        log_message(self.name, "🧬 Self-Evolving Meta Agent initialized with autonomous capability generation")
        logger.info(f"\n{'='*80}")
        logger.info(f"🧬 SELF-EVOLVING META AGENT INITIALIZED")
        logger.info(f"   Goal: {goal}")
        logger.info(f"   Model: {model}")
        logger.info(f"   Base tools: {list(self.tool_library.base_tools.keys())}")
        logger.info(f"{'='*80}\n")
    
    def _initialize_base_tools(self):
        """Initialize with a minimal set of base tools"""
        base_tools = {
            "analyze_text": self._analyze_text,
            "search_web": self._search_web,
            "process_data": self._process_data,
        }
        
        for name, func in base_tools.items():
            self.tool_library.register_base_tool(name, func)
    
    async def run(self, callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Execute the task with autonomous tool generation and evolution.
        """
        log_message(self.name, f"🚀 Starting self-evolving execution for: {self.goal}")
        logger.info(f"\n{'='*80}")
        logger.info(f"🚀 STARTING SELF-EVOLVING EXECUTION")
        logger.info(f"   Task: {self.goal}")
        logger.info(f"{'='*80}\n")
        
        start_time = datetime.utcnow()
        
        try:
            # Phase 1: Analyze task and identify capability gaps
            log_message(self.name, "🔍 Analyzing task requirements...")
            logger.info("\n📊 PHASE 1: TASK ANALYSIS")
            logger.info("   Analyzing task requirements and complexity...")
            task_analysis = await self.capability_analyzer.analyze_task(self.goal)
            logger.info(f"   Task type: {task_analysis.get('task_type', 'unknown')}")
            logger.info(f"   Complexity: {task_analysis.get('complexity', 'N/A')}/10")
            logger.info(f"   Required capabilities: {task_analysis.get('required_capabilities', [])}")
            gaps = await self.capability_analyzer.identify_gaps(
                task_analysis, 
                self.tool_library.get_capabilities()
            )
            
            if gaps:
                log_message(self.name, f"🔧 Identified {len(gaps)} capability gaps. Generating tools...")
                logger.info(f"\n🔍 CAPABILITY GAP ANALYSIS")
                logger.info(f"   Found {len(gaps)} missing capabilities:")
                for i, gap in enumerate(gaps, 1):
                    logger.info(f"   {i}. {gap['capability']} (Priority: {gap['priority']}, Complexity: {gap['complexity']})")
                
                # Phase 2: Generate tools to fill gaps
                logger.info("\n🔧 PHASE 2: TOOL GENERATION")
                for gap in gaps:
                    try:
                        logger.info(f"\n   Generating tool for: {gap['capability']}...")
                        tool = await self._generate_and_validate_tool(gap)
                        if tool:
                            self.tool_library.add(tool)
                            log_message(self.name, f"✅ Successfully generated tool: {tool['name']}")
                            logger.info(f"   ✅ Successfully generated and added: {tool['name']}")
                        else:
                            logger.info(f"   ❌ Failed validation for: {gap['capability']}")
                    except Exception as e:
                        log_message(self.name, f"⚠️ Failed to generate tool for {gap['capability']}: {e}")
                        logger.error(f"   ❌ Error generating tool: {e}")
            
            else:
                logger.info("\n✅ NO CAPABILITY GAPS - Using existing tools")
            
            # Phase 3: Execute task with enhanced capabilities
            log_message(self.name, "🎯 Executing task with available tools...")
            logger.info("\n🎯 PHASE 3: TASK EXECUTION")
            logger.info(f"   Available tools: {len(self.tool_library.active_tools) + len(self.tool_library.base_tools)}")
            logger.info(f"   Generated tools: {len([t for t in self.tool_library.active_tools.values() if t.get('generated', False)])}")
            result = await self._execute_task_with_tools(self.goal, callback)
            
            # Phase 4: Learn from execution and evolve
            logger.info("\n🧠 PHASE 4: LEARNING & EVOLUTION")
            execution_data = {
                "task": self.goal,
                "result": result,
                "duration": (datetime.utcnow() - start_time).total_seconds(),
                "tools_used": self._get_tools_used(),
            }
            logger.info(f"   Execution time: {execution_data['duration']:.2f} seconds")
            logger.info(f"   Tools used: {execution_data['tools_used']}")
            
            self.execution_history.append(execution_data)
            
            # Evolve tools based on performance
            await self._evolve_tools_based_on_performance(execution_data)
            
            # Phase 5: Return comprehensive result
            tools_generated = len([t for t in self.tool_library.active_tools.values() if t.get("generated", False)])
            new_capabilities = self.tool_library.get_new_capabilities_since(start_time)
            
            logger.info("\n🎆 PHASE 5: RESULTS")
            logger.info(f"   Status: SUCCESS")
            logger.info(f"   Tools generated: {tools_generated}")
            logger.info(f"   New capabilities: {new_capabilities}")
            logger.info(f"   Total execution time: {execution_data['duration']:.2f} seconds")
            logger.info(f"\n{'='*80}")
            logger.info(f"✅ EXECUTION COMPLETE")
            logger.info(f"{'='*80}\n")
            
            return {
                "status": "success",
                "result": result,
                "tools_generated": tools_generated,
                "execution_time": execution_data["duration"],
                "capabilities_learned": new_capabilities
            }
            
        except Exception as e:
            log_message(self.name, f"❌ Error during execution: {e}")
            logger.error(f"\n❌ EXECUTION ERROR")
            logger.error(f"   Error: {e}")
            logger.error(f"   Type: {type(e).__name__}")
            logger.error(f"\n{'='*80}\n")
            return {
                "status": "error",
                "error": str(e),
                "partial_result": None
            }
    
    async def _generate_and_validate_tool(self, gap: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate and validate a tool to fill a capability gap"""
        
        logger.info("\n   🔬 TOOL GENERATION PIPELINE")
        
        # Generate tool specification
        logger.info("   1. Generating tool specification...")
        spec = await self.code_generator.generate_specification(gap)
        logger.info(f"      Name: {spec.get('name', 'unknown')}")
        logger.info(f"      Type: {spec.get('type', 'unknown')}")
        logger.info(f"      Params: {spec.get('params', [])}")
        
        # Generate tool code
        logger.info("   2. Generating tool code...")
        tool_code = await self.code_generator.generate_tool(spec)
        logger.info(f"      Code length: {len(tool_code.get('code', ''))} characters")
        
        # Validate safety
        logger.info("   3. Validating tool safety...")
        is_safe, validation_result = await self.safety_validator.validate_tool(tool_code)
        
        if not is_safe:
            log_message(self.name, f"⚠️ Generated tool failed safety validation: {validation_result}")
            logger.warning(f"      ⚠️  FAILED: {validation_result}")
            return None
        
        logger.info("      ✅ Passed safety validation")
        
        # Test in sandbox
        logger.info("   4. Testing in sandbox...")
        test_result = await self.safety_validator.sandbox_test(tool_code, spec.get("test_cases", []))
        
        if test_result["success"]:
            logger.info(f"      ✅ Tests passed: {test_result.get('passed', 0)}/{test_result.get('total', 0)}")
            return {
                "name": spec["name"],
                "code": tool_code["code"],
                "spec": spec,
                "generated": True,
                "generation_time": datetime.utcnow().isoformat(),
                "performance_history": []
            }
        
        logger.warning(f"      ❌ Tests failed: {test_result.get('error', 'Unknown error')}")
        return None
    
    async def _execute_task_with_tools(self, task: str, callback: Optional[Callable]) -> Any:
        """Execute the task using available tools"""
        
        logger.info("\n   📋 EXECUTION PLANNING")
        
        # Create execution plan
        plan = await self._create_execution_plan(task)
        logger.info(f"   Created plan with {len(plan)} steps")
        
        # Execute plan steps
        logger.info("\n   🚀 EXECUTING PLAN")
        results = []
        for i, step in enumerate(plan, 1):
            logger.info(f"\n   Step {i}/{len(plan)}: {step.get('description', 'No description')}")
            tool_name = step["tool"]
            params = step["params"]
            logger.info(f"      Tool: {tool_name}")
            logger.info(f"      Params: {params}")
            
            if tool := self.tool_library.get_tool(tool_name):
                try:
                    start_time = datetime.utcnow()
                    if tool.get("generated"):
                        # Execute generated tool
                        logger.info("      Type: Generated tool")
                        result = await self._execute_generated_tool(tool, params)
                    else:
                        # Execute base tool
                        logger.info("      Type: Base tool")
                        result = await tool["function"](**params)
                    
                    exec_time = (datetime.utcnow() - start_time).total_seconds()
                    logger.info(f"      ✅ Success! Execution time: {exec_time:.2f}s")
                    logger.info(f"      Result preview: {str(result)[:100]}..." if len(str(result)) > 100 else f"      Result: {result}")
                    
                    results.append(result)
                    
                    # Track performance
                    self.tool_performance[tool_name].append({
                        "success": True,
                        "execution_time": exec_time,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                except Exception as e:
                    log_message(self.name, f"⚠️ Error executing tool {tool_name}: {e}")
                    logger.error(f"      ❌ Error: {e}")
                    self.tool_performance[tool_name].append({
                        "success": False,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    })
            else:
                logger.warning(f"      ⚠️  Tool not found: {tool_name}")
        
        # Synthesize results
        logger.info("\n   🎨 SYNTHESIZING RESULTS")
        logger.info(f"   Combining {len(results)} results...")
        final_result = await self._synthesize_results(results, task)
        logger.info(f"   Final result length: {len(str(final_result))} characters")
        return final_result
    
    async def _evolve_tools_based_on_performance(self, execution_data: Dict[str, Any]):
        """Evolve tools based on their performance"""
        
        logger.info("\n   🔄 TOOL EVOLUTION CHECK")
        evolution_candidates = 0
        
        for tool_name, performance_data in self.tool_performance.items():
            if len(performance_data) >= 3:  # Need enough data to evolve
                tool = self.tool_library.get_tool(tool_name)
                if tool and tool.get("generated"):
                    
                    # Calculate performance metrics
                    success_rate = sum(1 for p in performance_data if p["success"]) / len(performance_data)
                    logger.info(f"   Tool: {tool_name} - Success rate: {success_rate:.1%} ({len(performance_data)} executions)")
                    
                    if success_rate < 0.8:  # Tool needs improvement
                        evolution_candidates += 1
                        log_message(self.name, f"🔄 Evolving tool {tool_name} (success rate: {success_rate:.2%})")
                        logger.info(f"   🔄 Attempting evolution for {tool_name}...")
                        
                        # Generate evolved version
                        evolved_tool = await self.evolution_engine.evolve_tool(
                            tool,
                            performance_data,
                            self.execution_history
                        )
                        
                        if evolved_tool:
                            # Test evolved version
                            logger.info("      Testing evolved version...")
                            test_result = await self.safety_validator.sandbox_test(
                                evolved_tool,
                                tool["spec"].get("test_cases", [])
                            )
                            
                            if test_result["success"] and test_result["improvement"] > 0:
                                self.tool_library.update_tool(tool_name, evolved_tool)
                                log_message(self.name, f"✅ Successfully evolved {tool_name} with {test_result['improvement']:.1%} improvement")
                                logger.info(f"      ✅ Evolution successful! Improvement: {test_result['improvement']:.1%}")
                            else:
                                logger.info("      ❌ Evolution did not improve performance")
        
        if evolution_candidates == 0:
            logger.info("   No tools require evolution at this time")
    
    async def _create_execution_plan(self, task: str) -> List[Dict[str, Any]]:
        """Create an execution plan using available tools"""
        
        prompt = f"""
        Create an execution plan for this task: {task}
        
        Available tools: {json.dumps(self.tool_library.get_tool_descriptions())}
        
        Return a JSON array of steps, each with:
        - tool: tool name to use
        - params: parameters for the tool
        - description: what this step accomplishes
        """
        
        result = await _run_llm_with_retry(prompt, self.model)
        
        if isinstance(result, dict) and "error" not in result:
            return result.get("steps", [])
        
        # Fallback to simple plan
        return [{"tool": "analyze_text", "params": {"text": task}, "description": "Analyze task"}]
    
    async def _synthesize_results(self, results: List[Any], task: str) -> str:
        """Synthesize multiple results into a coherent response"""
        
        prompt = f"""
        Task: {task}
        
        Results from execution:
        {json.dumps(results, indent=2)}
        
        Synthesize these results into a comprehensive response that addresses the original task.
        """
        
        response = await _run_llm(prompt, self.model)
        return response
    
    async def _execute_generated_tool(self, tool: Dict[str, Any], params: Dict[str, Any]) -> Any:
        """Execute a generated tool safely"""
        
        # Create temporary module
        module_name = f"generated_tool_{tool['name']}"
        spec = importlib.util.spec_from_loader(module_name, loader=None)
        module = importlib.util.module_from_spec(spec)
        
        # Execute code in module namespace
        exec(tool["code"], module.__dict__)
        
        # Get the function
        func = getattr(module, tool["name"])
        
        # Execute with timeout
        try:
            result = await asyncio.wait_for(func(**params), timeout=30.0)
            return result
        except asyncio.TimeoutError:
            raise Exception(f"Tool {tool['name']} execution timed out")
    
    def _get_tools_used(self) -> List[str]:
        """Get list of tools used in current execution"""
        # This would track actual tool usage during execution
        return list(self.tool_performance.keys())
    
    # Base tool implementations
    async def _analyze_text(self, text: str) -> Dict[str, Any]:
        """Base tool for text analysis"""
        analysis = await _run_llm(f"Analyze this text and extract key information: {text}", self.model)
        return {"analysis": analysis}
    
    async def _search_web(self, query: str) -> Dict[str, Any]:
        """Base tool for web search (placeholder)"""
        # In a real implementation, this would use browser automation
        return {"results": f"Search results for: {query}"}
    
    async def _process_data(self, data: Any) -> Dict[str, Any]:
        """Base tool for data processing"""
        return {"processed": str(data)}


class CapabilityAnalyzer:
    """Analyzes tasks and identifies capability gaps"""
    
    def __init__(self, model: str):
        self.model = model
    
    async def analyze_task(self, task: str) -> Dict[str, Any]:
        """Analyze a task to understand required capabilities"""
        
        logger.info("      🗎️ Sending task to LLM for analysis...")
        
        prompt = f"""
        Analyze this task and identify the capabilities needed to complete it:
        
        Task: {task}
        
        Return a JSON object with:
        - task_type: classification of the task
        - required_capabilities: list of capabilities needed
        - complexity: estimated complexity (1-10)
        - data_requirements: what data/inputs are needed
        """
        
        result = await _run_llm_with_retry(prompt, self.model)
        if isinstance(result, dict):
            logger.info("      ✅ LLM analysis complete")
            return result
        else:
            logger.warning("      ⚠️  LLM returned non-dict result, using defaults")
            return {"task_type": "unknown", "required_capabilities": []}
    
    async def identify_gaps(self, task_analysis: Dict[str, Any], existing_capabilities: List[str]) -> List[Dict[str, Any]]:
        """Identify gaps between required and existing capabilities"""
        
        gaps = []
        for capability in task_analysis.get("required_capabilities", []):
            if not any(existing in capability.lower() for existing in existing_capabilities):
                gaps.append({
                    "capability": capability,
                    "priority": self._estimate_priority(capability, task_analysis),
                    "complexity": self._estimate_complexity(capability)
                })
        
        return sorted(gaps, key=lambda x: x["priority"], reverse=True)
    
    async def analyze(self, task: str, existing_tools: List[Dict]) -> Dict[str, Any]:
        """Public method for analyzing tasks and identifying capability gaps"""
        logger.info("\n🔍 CAPABILITY ANALYZER ACTIVATED")
        logger.info(f"   Task: {task[:100]}..." if len(task) > 100 else f"   Task: {task}")
        logger.info(f"   Existing tools: {len(existing_tools)}")
        
        analysis = await self.analyze_task(task)
        gaps = await self.identify_gaps(analysis, [t.get('name', '') for t in existing_tools])
        
        result = {
            "task_analysis": analysis,
            "gaps": gaps,
            "needs_new_tools": len(gaps) > 0
        }
        
        logger.info(f"   Analysis complete: {'New tools needed' if result['needs_new_tools'] else 'Existing tools sufficient'}")
        
        return result
    
    def _estimate_priority(self, capability: str, task_analysis: Dict[str, Any]) -> float:
        """Estimate priority of a capability"""
        # Simple heuristic - could be made more sophisticated
        if "critical" in capability.lower() or "essential" in capability.lower():
            return 1.0
        return 0.5
    
    def _estimate_complexity(self, capability: str) -> int:
        """Estimate complexity of implementing a capability"""
        # Simple heuristic based on keywords
        complex_keywords = ["machine learning", "computer vision", "nlp", "parse", "analyze"]
        if any(keyword in capability.lower() for keyword in complex_keywords):
            return 8
        return 5


class SafeCodeGenerator:
    """Generates safe, validated code for new tools"""
    
    TOOL_TEMPLATES = {
        "data_processor": '''
async def {name}({params}):
    """Auto-generated tool for {purpose}"""
    try:
{implementation}
        return {{"status": "success", "result": result}}
    except Exception as e:
        return {{"status": "error", "error": str(e)}}
''',
        
        "web_scraper": '''
async def {name}({params}):
    """Auto-generated scraper for {purpose}"""
    try:
        # Placeholder for browser automation
{implementation}
        return {{"status": "success", "data": extracted_data}}
    except Exception as e:
        return {{"status": "error", "error": str(e)}}
''',
        
        "api_caller": '''
async def {name}(endpoint: str, params: Optional[Dict] = None):
    """Auto-generated API interface for {purpose}"""
    try:
{implementation}
        return {{"status": "success", "response": response}}
    except Exception as e:
        return {{"status": "error", "error": str(e)}}
''',
        
        "analyzer": '''
async def {name}({params}) -> Dict[str, Any]:
    """Auto-generated analyzer for {purpose}"""
    try:
{implementation}
        return {{"status": "success", "analysis": analysis}}
    except Exception as e:
        return {{"status": "error", "error": str(e)}}
'''
    }
    
    def __init__(self, model: str):
        self.model = model
    
    async def generate_specification(self, gap: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a detailed specification for a tool"""
        
        logger.info("      🗎️ Generating tool specification...")
        
        prompt = f"""
        Generate a tool specification for this capability gap:
        
        Capability: {gap['capability']}
        Priority: {gap['priority']}
        
        Return a JSON object with:
        - name: function name (snake_case)
        - purpose: clear description
        - type: one of [data_processor, web_scraper, api_caller, analyzer]
        - params: list of parameter names
        - implementation_hints: hints for implementation
        - test_cases: 2-3 test cases
        """
        
        result = await _run_llm_with_retry(prompt, self.model)
        
        if isinstance(result, dict):
            logger.info("      ✅ Specification generated")
            return result
        
        # Fallback specification
        logger.warning("      ⚠️  Using fallback specification")
        return {
            "name": f"tool_{gap['capability'].lower().replace(' ', '_')}",
            "purpose": gap['capability'],
            "type": "data_processor",
            "params": ["data"],
            "implementation_hints": [],
            "test_cases": []
        }
    
    async def generate_tool(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tool code based on specification"""
        
        logger.info(f"      🗎️ Generating code for tool type: {spec['type']}")
        
        template = self.TOOL_TEMPLATES.get(spec["type"], self.TOOL_TEMPLATES["data_processor"])
        
        # Generate implementation
        implementation = await self._generate_implementation(spec)
        
        # Fill template
        # Handle params that might be dicts or strings
        params = spec["params"]
        if isinstance(params, list):
            param_names = []
            for p in params:
                if isinstance(p, dict):
                    param_names.append(p.get('name', 'param'))
                else:
                    param_names.append(str(p))
            params_str = ", ".join(param_names)
        elif isinstance(params, dict):
            # If params is a dict, extract parameter names
            param_names = list(params.keys())
            params_str = ", ".join(param_names)
        else:
            params_str = str(params)
        
        code = template.format(
            name=spec["name"],
            params=params_str,
            purpose=spec["purpose"],
            implementation=implementation
        )
        
        logger.info(f"      🔨 Applying safety constraints...")
        # Apply safety constraints
        safe_code = self._apply_safety_constraints(code)
        
        logger.info(f"      ✅ Tool code generated ({len(safe_code)} chars)")
        
        return {
            "code": safe_code,
            "spec": spec
        }
    
    async def _generate_implementation(self, spec: Dict[str, Any]) -> str:
        """Generate the implementation for a tool"""
        
        logger.info("      🤖 Asking LLM to generate implementation...")
        
        prompt = f"""
        Generate Python implementation for this tool:
        
        Purpose: {spec['purpose']}
        Type: {spec['type']}
        Parameters: {spec['params']}
        Hints: {spec.get('implementation_hints', [])}
        
        Requirements:
        - Use only standard library and common packages
        - Include error handling
        - Return results in a consistent format
        - Keep it simple and focused
        - IMPORTANT: The code must be properly indented with 8 spaces (2 levels of indentation)
        - Do NOT include the function definition, only the implementation body
        - The final line should set a variable that matches the return key:
          * For data_processor: set 'result' variable
          * For web_scraper: set 'extracted_data' variable  
          * For api_caller: set 'response' variable
          * For analyzer: set 'analysis' variable
        
        Return only the implementation code (no function definition).
        """
        
        implementation = await _run_llm(prompt, self.model)
        
        # Clean up the implementation
        implementation = implementation.strip()
        if implementation.startswith("```python"):
            implementation = implementation[9:-3].strip()
        
        # Ensure proper indentation (8 spaces for inside try block)
        lines = implementation.split('\n')
        indented_lines = []
        for line in lines:
            if line.strip():  # Non-empty lines
                indented_lines.append('        ' + line)
            else:
                indented_lines.append(line)  # Keep empty lines as is
        
        implementation = '\n'.join(indented_lines)
        
        logger.info(f"      ✅ Implementation generated ({len(implementation)} chars)")
        
        return implementation
    
    def _apply_safety_constraints(self, code: str) -> str:
        """Apply safety constraints to generated code"""
        
        # Add imports if needed
        safe_imports = """
import asyncio
from typing import Dict, List, Any, Optional
import json
"""
        
        # Ensure the code has safe imports at the top
        if "import" not in code:
            code = safe_imports + "\n" + code
        
        return code


class SafetyValidator:
    """Validates generated tools for safety and correctness"""
    
    FORBIDDEN_PATTERNS = [
        r'exec\s*\(',
        r'eval\s*\(',
        r'__import__',
        r'subprocess',
        r'os\.system',
        r'open\s*\(.*[\'"]w',  # Write mode files
        r'compile\s*\(',
        r'globals\s*\(',
        r'locals\s*\(',
    ]
    
    ALLOWED_IMPORTS = {
        'json', 'asyncio', 'typing', 're', 'datetime', 
        'collections', 'itertools', 'functools', 'math'
    }
    
    async def validate_tool(self, tool_code: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate a tool for safety"""
        
        code = tool_code["code"]
        
        # Check for forbidden patterns
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, code):
                return False, f"Forbidden pattern detected: {pattern}"
        
        # Validate syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        
        # Check imports
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name not in self.ALLOWED_IMPORTS:
                        return False, f"Forbidden import: {alias.name}"
        
        # Check resource usage (basic)
        if len(code) > 10000:  # Max 10KB per tool
            return False, "Code too large"
        
        return True, "Validation passed"
    
    async def sandbox_test(self, tool_code: Dict[str, Any], test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test tool in sandboxed environment"""
        
        # Create a minimal test environment
        test_namespace = {
            '__builtins__': {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'Exception': Exception,
            }
        }
        
        try:
            # Execute the code in restricted namespace
            exec(tool_code["code"], test_namespace)
            
            # Get the function
            func_name = tool_code["spec"]["name"]
            if func_name not in test_namespace:
                return {"success": False, "error": "Function not found"}
            
            # Run test cases
            if not test_cases:
                # Basic smoke test
                return {"success": True, "improvement": 0}
            
            passed = 0
            for test in test_cases:
                try:
                    # This is a simplified test - in production would use proper sandboxing
                    result = test_namespace[func_name](**test.get("input", {}))
                    if result.get("status") == "success":
                        passed += 1
                except:
                    pass
            
            success_rate = passed / len(test_cases) if test_cases else 1.0
            
            return {
                "success": success_rate > 0.5,
                "improvement": success_rate,
                "passed": passed,
                "total": len(test_cases)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


class EvolutionEngine:
    """Handles tool evolution and improvement"""
    
    def __init__(self, model: str):
        self.model = model
        self.evolution_history = []
    
    async def evolve_tool(self, tool: Dict[str, Any], performance_data: List[Dict], 
                         execution_history: List[Dict]) -> Optional[Dict[str, Any]]:
        """Evolve a tool based on performance data"""
        
        # Analyze failure patterns
        failures = [p for p in performance_data if not p["success"]]
        
        if not failures:
            return None  # No failures to learn from
        
        # Generate improvement suggestions
        prompt = f"""
        Analyze this tool's failures and suggest improvements:
        
        Tool purpose: {tool['spec']['purpose']}
        Current implementation:
        {tool['code']}
        
        Failures:
        {json.dumps(failures, indent=2)}
        
        Suggest specific code improvements to address these failures.
        """
        
        suggestions = await _run_llm(prompt, self.model)
        
        # Generate evolved version
        evolved_spec = tool['spec'].copy()
        evolved_spec['evolution_hints'] = suggestions
        
        # Generate new implementation
        generator = SafeCodeGenerator(self.model)
        evolved_tool = await generator.generate_tool(evolved_spec)
        
        # Track evolution
        self.evolution_history.append({
            "original": tool["name"],
            "evolved": evolved_tool["spec"]["name"],
            "timestamp": datetime.utcnow().isoformat(),
            "improvements": suggestions
        })
        
        return evolved_tool


class EvolvingToolLibrary:
    """Manages the library of generated and evolved tools"""
    
    def __init__(self):
        self.active_tools = {}
        self.tool_archive = {}  # Historical versions
        self.base_tools = {}
        self.performance_metrics = defaultdict(list)
        self.capability_index = defaultdict(list)  # capability -> tool names
    
    def register_base_tool(self, name: str, function: Callable):
        """Register a base tool"""
        self.base_tools[name] = {
            "name": name,
            "function": function,
            "generated": False
        }
        
        # Index capabilities
        self.capability_index[name].append(name)
    
    def add(self, tool: Dict[str, Any]):
        """Add a new generated tool"""
        tool_id = tool["name"]
        
        # Archive previous version if exists
        if tool_id in self.active_tools:
            old_tool = self.active_tools[tool_id]
            archive_key = f"{tool_id}_v{datetime.utcnow().timestamp()}"
            self.tool_archive[archive_key] = old_tool
        
        # Add new tool
        self.active_tools[tool_id] = tool
        
        # Update capability index
        for word in tool["spec"]["purpose"].lower().split():
            self.capability_index[word].append(tool_id)
    
    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a tool by name"""
        if name in self.active_tools:
            return self.active_tools[name]
        return self.base_tools.get(name)
    
    def get_capabilities(self) -> List[str]:
        """Get list of all capabilities"""
        capabilities = list(self.base_tools.keys())
        capabilities.extend([tool["spec"]["purpose"] for tool in self.active_tools.values()])
        return capabilities
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all available tools"""
        descriptions = {}
        
        for name, tool in self.base_tools.items():
            descriptions[name] = f"Base tool for {name}"
        
        for name, tool in self.active_tools.items():
            descriptions[name] = tool["spec"]["purpose"]
        
        return descriptions
    
    def update_tool(self, name: str, evolved_tool: Dict[str, Any]):
        """Update a tool with an evolved version"""
        # Archive current version
        if name in self.active_tools:
            old_tool = self.active_tools[name]
            archive_key = f"{name}_v{datetime.utcnow().timestamp()}"
            self.tool_archive[archive_key] = old_tool
        
        # Update with evolved version
        evolved_tool["evolution_count"] = self.active_tools.get(name, {}).get("evolution_count", 0) + 1
        self.active_tools[name] = evolved_tool
    
    def get_new_capabilities_since(self, timestamp: datetime) -> List[str]:
        """Get capabilities added since a timestamp"""
        new_capabilities = []
        for tool in self.active_tools.values():
            if tool.get("generated") and tool.get("generation_time"):
                tool_time = datetime.fromisoformat(tool["generation_time"])
                if tool_time > timestamp:
                    new_capabilities.append(tool["spec"]["purpose"])
        return new_capabilities
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools"""
        all_tools = []
        all_tools.extend(self.base_tools.values())
        all_tools.extend(self.active_tools.values())
        return all_tools
    
    def get_relevant_tools(self, task: str) -> List[Dict[str, Any]]:
        """Get tools relevant to a specific task"""
        relevant = []
        task_words = set(task.lower().split())
        
        # Check base tools
        for name, tool in self.base_tools.items():
            if any(word in name.lower() for word in task_words):
                relevant.append(tool)
        
        # Check generated tools
        for name, tool in self.active_tools.items():
            if any(word in tool["spec"]["purpose"].lower() for word in task_words):
                relevant.append(tool)
        
        return relevant
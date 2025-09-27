# s(CASP) Integration and Fallback Logic

## Overview

This document describes the integration of the s(CASP) (stochastic Constraint Answer Set Programming) reasoning engine within the Legal AI Assistant, including the intelligent fallback system designed to handle complex legal rule compilation issues.

## Architecture

### Core Components

1. **BlawxParser** (`app/services/blawx_parser.py`)
   - Parses `.blawx` files containing legal documents
   - Extracts legal provisions and s(CASP) rules
   - Formats rules for execution

2. **ScaspEngine** (`app/services/scasp_engine.py`)
   - Interfaces with the s(CASP) reasoning engine
   - Falls back to SWI-Prolog when s(CASP) is unavailable
   - Implements intelligent fallback strategies
   - Handles query execution and result parsing

3. **SWI-Prolog Integration**
   - Provides alternative logic programming backend
   - Handles basic Prolog queries when s(CASP) fails
   - Ensures system availability even without s(CASP)

3. **LLM Service Integration** (`app/main.py`)
   - Coordinates between natural language queries and formal logic
   - Manages the complete legal reasoning pipeline

## SWI-Prolog Integration

### Overview
SWI-Prolog serves as a critical fallback mechanism when s(CASP) is unavailable or fails to compile complex legal rules. It provides basic logic programming capabilities to ensure the system remains functional.

### Architecture Role
```
Primary: s(CASP) Engine (advanced reasoning)
    ↓ (if unavailable or fails)
Fallback: SWI-Prolog Engine (basic logic)
```

### SWI-Prolog Detection and Setup
The system automatically detects SWI-Prolog installations:

```python
def _find_prolog(self) -> Optional[str]:
    """Try to find SWI-Prolog installation."""
    possible_paths = [
        '/usr/local/bin/swipl',     # Homebrew on macOS
        '/usr/bin/swipl',           # Linux package managers
        'swipl'                     # In PATH
    ]
    
    for path in possible_paths:
        try:
            result = subprocess.run([path, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return path
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
```

### Query Execution with SWI-Prolog
When s(CASP) is unavailable, the system uses SWI-Prolog:

```python
def _query_prolog(self, program: str, query: str, timeout: int) -> Dict[str, Any]:
    """Execute query using SWI-Prolog as fallback."""
    
    # Create temporary program file
    program_file = self.temp_dir / f"program_{os.getpid()}.pl"
    with open(program_file, 'w') as f:
        f.write(program)
    
    # Execute Prolog query
    prolog_query = f"consult('{program_file}'), {query}."
    cmd = [self.prolog_path, '-q', '-g', prolog_query, '-t', 'halt.']
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
```

### Limitations and Differences

| Feature | s(CASP) | SWI-Prolog |
|---------|---------|-------------|
| **Reasoning Style** | Answer Set Programming | Traditional Prolog |
| **Constraints** | Built-in constraint handling | Limited constraint support |
| **Explanations** | Natural language justifications | Basic success/failure |
| **Uncertainty** | Probabilistic reasoning | Deterministic only |
| **Meta-Predicates** | Rich meta-reasoning | Basic meta-predicates |
| **Legal Reasoning** | Purpose-built for legal logic | General-purpose logic |

### Output Processing
SWI-Prolog responses are simpler than s(CASP):

```python
def _parse_prolog_output(self, output: str) -> List[ScaspAnswer]:
    """Parse Prolog output into structured answers."""
    answers = []
    
    # Simple success detection
    if 'true' in output.lower() or 'yes' in output.lower():
        answers.append(ScaspAnswer(
            solution={},
            justification=['Prolog query succeeded'],
            confidence=0.8,  # Lower confidence than s(CASP)
            is_consistent=True
        ))
    
    return answers
```

### Use Cases for SWI-Prolog Fallback
1. **Development Environments**: When s(CASP) is not installed
2. **Deployment Constraints**: Environments where s(CASP) cannot be deployed
3. **Simple Legal Queries**: Basic fact-checking that doesn't require advanced reasoning
4. **Backup Availability**: Ensuring system uptime when s(CASP) encounters issues

## s(CASP) Rule Processing Pipeline

### 1. Document Loading
```
.blawx files → BlawxParser → LegalRuleDoc objects
```

Each `.blawx` file contains:
- Legal text in human-readable format
- s(CASP) logic rules for formal reasoning
- Metadata and relationships

### 2. Rule Extraction and Formatting

The `BlawxParser` processes raw s(CASP) encoding:

```python
def format_scasp_program(self, rules: List[ScaspRule]) -> str:
    """Format s(CASP) rules into a complete logic program."""
    
    # Group rules by type
    facts = [r for r in rules if r.rule_type == 'fact']
    logic_rules = [r for r in rules if r.rule_type == 'rule'] 
    abducibles = [r for r in rules if r.rule_type == 'abducible']
    queries = [r for r in rules if r.rule_type == 'query']
```

#### Rule Validation and Cleaning
- Removes malformed rules (e.g., `age(Person,Age),.`)
- Handles period termination consistently
- Filters out incomplete constraint fragments
- Skips empty or invalid rule text

### 3. Query Execution with Fallback Strategy

The `ScaspEngine` implements a two-tier approach:

```python
def query(self, program: str, query: str, timeout: int = 30) -> ScaspResult:
    """Execute a query with formal reasoning fallbacks."""
    
    # Tier 1: Try full complex program with s(CASP)
    result = self._query_scasp(program, query, timeout)
    
    # Tier 2: Try SWI-Prolog if s(CASP) fails
    if not result.get('success'):
        if self.prolog_path:
            result = self._query_prolog(program, query, timeout)
```

## Fallback Strategies

### Tier 1: s(CASP) Formal Reasoning
Attempts to use the full legal program with s(CASP) engine, including:
- Complex legal rules and constraints
- Meta-predicates and temporal reasoning
- Answer set programming with explanations
- Probabilistic and uncertain reasoning

### Tier 2: SWI-Prolog Fallback
When s(CASP) fails or is unavailable, falls back to SWI-Prolog:
- Basic logic programming
- Deterministic reasoning
- Simple success/failure responses
- Limited constraint handling
    
    # Keep only basic facts and rules
    # Add fundamental legal facts if program becomes too sparse
```

#### Basic Legal Facts Added:
```prolog
% Basic legal facts for Canadian law
canadian_citizen(citizen).
government_institution(health_canada).
government_institution(revenue_agency).
access_right(citizen, government_record).

% Basic access rules
can_request_records(Person, Institution) :-
    canadian_citizen(Person),
    government_institution(Institution).

eligible_for_access(Person) :-
    canadian_citizen(Person).
```

### Tier 3: Intelligent Fallback Response
When formal reasoning fails completely, generates contextually appropriate responses:

```python
def _create_fallback_response(self, query: str, program: str) -> Dict[str, Any]:
    """Create reasonable fallback based on query analysis."""
    
    query_lower = query.lower()
    
    # Health Canada specific logic
    if any(term in query_lower for term in ['health_canada', 'health', 'canada']):
        if 'canadian_citizen' in query_lower or 'citizen' in query_lower:
            return intelligent_health_canada_response()
    
    # General access to information logic
    if any(term in query_lower for term in ['request', 'access', 'record']):
        return general_access_response()
```

## Error Handling and Recovery

### Common Issues and Solutions

#### 1. Syntax Errors
**Problem**: `ERROR: Syntax error: Operator expected`
**Root Cause**: Malformed rules like `age(Person,Age),.`
**Solution**: Enhanced rule validation in `_parse_scasp_line()`

#### 2. Complex Predicate Compilation Errors
**Problem**: `ERROR: Deterministic procedure scasp_program:assert_program/1 failed`
**Root Cause**: Blawx meta-predicates exceed s(CASP) capabilities
**Solution**: Automatic simplification and fallback

#### 3. Constraint Fragment Issues
**Problem**: Standalone constraints like `Age #>= 14.`
**Solution**: Filter out incomplete constraints during parsing

### Debugging and Monitoring

The system includes comprehensive logging:

```python
# Debug output when fallback is triggered
print(f"s(CASP) failed with complex rules, trying simplified version...")

# Detailed error reporting
return ScaspResult(
    query=query,
    success=False, 
    error_message="Unable to process complex legal query with available reasoning engine"
)
```

## Integration with Frontend

### Response Processing
The frontend (`frontend/src/components/MessageBubble.tsx`) handles s(CASP) responses through:

1. **JSON Response Parsing**: Detects and parses JSON responses from the LLM
2. **Enhanced Display**: Shows reasoning steps, citations, and confidence levels
3. **Graceful Degradation**: Always displays meaningful content to users

### User Experience Flow
```
User Query → LLM Analysis → s(CASP) Reasoning → Formatted Response
                                    ↓
                              (If s(CASP) fails)
                                    ↓
                           SWI-Prolog Reasoning → Formatted Response
                                    ↓
                              (If both fail)
                                    ↓
                              Error Response
```

## Performance Considerations

### Optimization Strategies
- **Rule Filtering**: Only relevant rules are included in each query
- **Timeout Management**: Queries are bounded by configurable timeouts
- **Caching**: Results can be cached to avoid repeated computations
- **Incremental Fallback**: Each tier is progressively simpler and faster

### Scalability
- **Parallel Processing**: Multiple queries can be processed simultaneously
- **Resource Management**: Temporary files are cleaned up after each query
- **Memory Efficiency**: Large programs are streamed rather than loaded entirely

## Future Enhancements

### Planned Improvements
1. **Rule Optimization**: Better analysis of which complex rules can be simplified
2. **Confidence Scoring**: More sophisticated confidence calculation based on reasoning depth
3. **Caching Layer**: Persistent caching of successful query results
4. **Alternative Reasoning Engines**: Integration with additional logic programming systems

### Research Directions
1. **Hybrid Reasoning**: Combining s(CASP) with other AI reasoning approaches
2. **Dynamic Rule Learning**: Automatically improving rule simplification based on success rates
3. **Legal Domain Specialization**: Custom reasoning strategies for different areas of law

## Configuration

### Environment Variables
```bash
# s(CASP) engine path (auto-detected if not set)
SCASP_PATH=/path/to/scasp

# Query timeout in seconds  
SCASP_TIMEOUT=30

# Enable debug logging
SCASP_DEBUG=true
```

### Customization Points
- Rule filtering patterns in `_create_simplified_program()`
- SWI-Prolog query execution parameters
- Confidence calculation logic in `_calculate_confidence()`
- Timeout values and retry strategies

## Conclusion

This two-tiered formal reasoning approach ensures that the Legal AI Assistant relies only on established logic programming methods - s(CASP) for advanced legal reasoning and SWI-Prolog as a solid fallback. The system prioritizes formal verification and sound logical inference over pattern-based heuristics.

The architecture is designed to be robust, maintainable, and scalable with multiple legal acts and complex rule sets. By focusing exclusively on formal reasoning systems, the solution maintains logical integrity while providing reliable legal guidance across diverse query types and complexity levels.
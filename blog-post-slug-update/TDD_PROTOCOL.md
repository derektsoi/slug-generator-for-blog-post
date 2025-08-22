# 🚨 TDD Protocol Enforcement

## MANDATORY Test-Driven Development Rules

**⚠️ WARNING: This file serves as a constant reminder to follow TDD practices**

### 🔴 RED Phase Checklist
- [ ] Write comprehensive failing tests FIRST
- [ ] Run tests to confirm they FAIL (skip or error)
- [ ] Document expected behavior clearly in test names
- [ ] Verify all edge cases are covered in tests
- [ ] NO implementation code written yet

**Command to verify RED state:**
```bash
python3 tests/unit/test_[component].py
# Expected: Tests should be SKIPPED or FAIL
```

### 🟢 GREEN Phase Checklist  
- [ ] Write MINIMAL code to make tests pass
- [ ] Implement only what tests require
- [ ] No additional features or optimizations
- [ ] Run tests to confirm they PASS
- [ ] All tests must be GREEN before proceeding

**Command to verify GREEN state:**
```bash
python3 tests/unit/test_[component].py
# Expected: Tests should PASS (not skip)
```

### 🔵 REFACTOR Phase Checklist
- [ ] Improve code quality and structure
- [ ] Maintain all existing test passes
- [ ] Add comments and documentation
- [ ] Run full test suite after changes
- [ ] Commit changes after successful refactor

**Command to verify REFACTOR safety:**
```bash
python3 tests/unit/test_[component].py
# Expected: All tests still PASS after refactor
```

## Current TDD Status

### Phase 1: Core Infrastructure
- **AtomicJSONLWriter**: 🔴 RED ✅ (9 tests failing/skipped)
- **RobustCheckpointManager**: 🔴 RED ✅ (11 tests failing/skipped)  
- **SynchronizedProgressTracker**: 🔴 RED ✅ (12 tests failing/skipped)

### Next Steps
1. Implement AtomicJSONLWriter (GREEN phase)
2. Implement RobustCheckpointManager (GREEN phase)
3. Implement SynchronizedProgressTracker (GREEN phase)
4. Integration testing and REFACTOR phase

## TDD Violation Prevention

### ❌ NEVER DO:
- Write production code before tests
- Skip test verification phases
- Implement beyond test requirements
- Ignore failing tests
- Refactor without running tests

### ✅ ALWAYS DO:
- Write tests first
- Verify RED state before coding
- Write minimal code for GREEN state
- Run tests after each change
- Commit after successful cycles

## Emergency TDD Recovery

If TDD cycle is broken:
1. **STOP** all implementation work
2. **IDENTIFY** what tests are missing
3. **WRITE** missing tests first
4. **VERIFY** tests fail properly
5. **RESUME** proper TDD cycle

Remember: **Quality comes from discipline, not shortcuts**
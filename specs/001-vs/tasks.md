# Tasks: 001-vs - Time-based Usage Pattern Analysis

**Input**: Design documents from `/specs/001-vs/`
**Prerequisites**: plan.md (required), research.md, data-model.md, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project - adjust based on plan.md structure

## ⚠️ Critical Design Constraint: Memory Efficiency ⚠️
The source Parquet files are extremely large (approx. 4GB each). All data loading and analysis code MUST be designed to be memory-efficient. Loading an entire file into memory at once is strictly forbidden.

#### Approach: Use a generator-based streaming pattern. Data should be read and processed in smaller, manageable chunks to avoid memory overflow.

## Phase 3.1: Setup
- [x] T001 Initialize Python project with `uv` and create virtual environment.
- [x] T002 Install primary dependencies: `pandas`, `matplotlib`, `seaborn`, `streamlit`, `geopandas`, `folium`, `ruff`.
- [x] T003 [P] Configure `ruff` for linting and formatting.

## Phase 3.2: Tests First (TDD - RED) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] T004 Create `tests/test_data_loader.py` and write unit tests for `src/data_load.py` functions (Parquet and CSV reading).
- [x] T005 Create `tests/test_preprocessor.py` and write unit tests for `src/preprocessor.py` functions (data cleaning, time-related column processing).

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [x] T006 Implement functions in `src/data_load.py` to pass tests in `tests/test_data_loader.py`.
- [s] T007 Implement functions in `src/preprocessor.py` to pass tests in `tests/test_preprocessor.py`. **It is not neccesery. Because preprocessor do not implement this project.**

## Phase 3.4: Core Analysis Function Implementation (TDD Loop)
- [x] T008 Create `src/analysis/time_analysis.py` module.
- [x] T009 Create `tests/analysis/test_time_analysis.py` and write unit tests for time-based pattern analysis functions in `src/analysis/time_analysis.py`.
- [x] T010 Implement time-based pattern analysis functions in `src/analysis/time_analysis.py` to pass tests in `tests/analysis/test_time_analysis.py`.

## Phase 3.5: Streamlit Visualization Page Development
- [x] T011 Set up basic Streamlit app layout and title in `src/main.py`.
- [x] T012 Create `src/pages/01_time_analysis_visualization.py` and implement the '시간대별 이용 패턴 분석' interactive dashboard, including input widgets (e.g., year, month, hour) to dynamically filter and display analysis results (charts, tables) from `src/analysis/time_analysis.py`.
- [x] T014 Implement `load_parquet_year_data` in `src/data_load.py`.
- [ ] T015 Update `tests/analysis/test_time_analysis.py` to test `analyze_time_data` and `analyze_monthly_usage_by_year`.

## Phase 3.6: Finalization
- [ ] T013 Update `README.md` with project description and execution instructions (`streamlit run src/main.py`).

## Dependencies
- T004, T005 (Tests) before T006, T007 (Implementation).
- T009 (Analysis Tests) before T010 (Analysis Implementation).
- T006, T007 (Data Processing) before T010 (Analysis Implementation).
- T010 (Analysis Implementation) before T012 (Streamlit Page).
- T011 (Main Streamlit App) before T012 (Streamlit Page).

## Parallel Example
```
# Launch T004 and T005 together:
Task: "Create tests/test_data_loader.py and write unit tests for src/data_loader.py functions."
Task: "Create tests/test_preprocessor.py and write unit tests for src/preprocessor.py functions."

# Launch T006 and T007 together (after T004 and T005 are RED):
Task: "Implement functions in src/data_loader.py to pass tests."
Task: "Implement functions in src/preprocessor.py to pass tests."
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**: (Not applicable for this feature)
   - Each contract file → contract test task [P]
   - Each endpoint → implementation task
   
2. **From Data Model**:
   - Each entity → model creation task [P] (Covered by data_loader and preprocessor tasks)
   - Relationships → service layer tasks (Covered by preprocessor and analysis tasks)
   
3. **From User Stories**:
   - Each story → integration test [P] (Covered by Streamlit page and overall goal)
   - Quickstart scenarios → validation tasks (Covered by setup and finalization)

4. **Ordering**:
   - Setup → Tests → Models/Data Processing → Analysis → Streamlit UI → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [ ] All contracts have corresponding tests (N/A)
- [ ] All entities have model tasks (Covered by data_loader and preprocessor)
- [ ] All tests come before implementation
- [ ] Parallel tasks truly independent
- [ ] Each task specifies exact file path
- [ ] No task modifies same file as another [P] task

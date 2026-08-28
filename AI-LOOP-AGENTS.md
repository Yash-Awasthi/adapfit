# AdapFit AI-Loop Agents — Parallel Execution Framework

Each agent operates independently on its own work stream. Agents don't block each other.
Multiple agents run per iteration for maximum throughput.

---

## Agent Roles

### 🔍 Inspector
**Role**: Verify existing code, find bugs, check consistency, validate data flows.
**Output**: List of issues with severity, file:line references, suggested fixes.
**Does NOT**: Edit files directly. Reports findings for Worker/Engineer to fix.

### 💡 Innovator
**Role**: Research new features, search GitHub/web for patterns, propose novel capabilities.
**Output**: Feature proposals with implementation sketches, research references.
**Does NOT**: Implement features. Designs them for Engineer to build.

### 🔨 Worker
**Role**: Build features, create files, write code. Fastest path to working code.
**Output**: New files and endpoints. Ponytail mode — simplest solution.
**Does NOT**: Run tests (goes to TEST-LOOP.md). Focuses on building.

### ⚙️ Engineer
**Role**: Refactor, optimize, harden code. Circuit breakers, caching, type safety.
**Output**: Improved existing files, performance optimizations, security fixes.
**Does NOT**: Add new features. Improves existing code quality.

### 📐 Architect
**Role**: System design, API contracts, data models, module boundaries.
**Output**: Architecture decisions, API specs, module diagrams.
**Does NOT**: Write implementation code. Defines the blueprint.

### 🧪 Tester (Deferred)
**Role**: Write test plans and test cases. Goes to TEST-LOOP.md.
**Output**: Test specifications, edge cases, boundary conditions.
**Does NOT**: Run tests in this loop. Documents what to test.

### 📊 Manager
**Role**: Track progress, prioritize tasks, identify blockers, coordinate agents.
**Output**: Status reports, task assignments, dependency maps.
**Does NOT**: Implement anything. Manages the workflow.

### 🎨 UI/UX Designer
**Role**: Design mobile screens, component layouts, user flows.
**Output**: React Native components, screen designs, interaction patterns.
**Does NOT**: Backend code. Focuses on mobile experience.

### 🗄️ Data Engineer
**Role**: Database schemas, migrations, data pipelines, analytics.
**Output**: SQL DDL, migration files, data processing logic.
**Does NOT**: Application code. Focuses on data layer.

### 🛡️ Security Reviewer
**Role**: OWASP review, input validation, auth checks, vulnerability scanning.
**Output**: Security findings with severity, remediation steps.
**Does NOT**: Fix vulnerabilities. Reports them for Engineer to fix.

---

## Parallel Execution Map

### Iteration Pattern

Each iteration runs 6-8 agents in parallel:

```
ITERATION N:
├── Inspector: Scan codebase for issues from last iteration
├── Innovator: Research 2-3 new feature ideas from web
├── Worker ×2: Build 2 features from Innovator's proposals
├── Engineer: Optimize a hot path or add resilience pattern
├── Architect: Design next feature's API contract
├── UI/UX: Build a mobile screen for the latest feature
├── Security: Review the new endpoints for vulnerabilities
└── Manager: Update AI-LOOP.md, assign next tasks
```

### Dependency Graph

```
Innovator → Architect → Worker → Inspector → Engineer → Security
    ↓                                        ↓
Manager ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ↓
```

Rules:
1. Innovator researches → Architect designs → Worker builds
2. Inspector reviews → Engineer improves → Security validates
3. Manager coordinates and tracks
4. No agent blocks another — parallel by default

---

## Current Agent Assignments

| Agent | Current Task | Output |
|-------|-------------|--------|
| **Inspector** | Scan all 42 services for missing error handling | Issue report |
| **Innovator** | Research: menstrual cycle AI, altitude training, team challenges | 3 proposals |
| **Worker-1** | Build meditation API endpoints from meditation.py | New endpoint |
| **Worker-2** | Build health advisor API endpoint from health_advisor.py | New endpoint |
| **Engineer** | Add circuit breaker to all LLM calls in chat.py | Improved chat |
| **Architect** | Design unified biometric data model across all sensors | Data schema |
| **UI/UX** | Build health conditions screen for mobile | New screen |
| **Security** | Review auth.py and deduplication.py for bypasses | Security report |
| **Data Engineer** | Design analytics schema for cross-metric correlations | SQL DDL |
| **Manager** | Update AI-LOOP.md with Iteration 5 status | Status update |

---

## Completed Agent Work

### Iteration 1 (Foundation)
| Agent | Task | Status |
|-------|------|--------|
| Worker | pose_estimation.py | ✅ |
| Worker | health_connect_bridge.py | ✅ |
| Engineer | logging_config.py | ✅ |
| UI/UX | onboarding.tsx | ✅ |
| Architect | event_bus.py | ✅ |
| Innovator | cycle_tracking.py | ✅ |

### Iteration 2 (Core CV + Sensors)
| Agent | Task | Status |
|-------|------|--------|
| Worker | form_scorer.py | ✅ |
| Innovator | food_vision.py | ✅ |
| Innovator | evolution_engine.py | ✅ |
| Worker | gps_tracking.py | ✅ |
| UI/UX | theme.ts | ✅ |

### Iteration 3 (Intelligence + Resilience)
| Agent | Task | Status |
|-------|------|--------|
| Engineer | anomaly_detector.py | ✅ |
| Engineer | circuit_breaker.py | ✅ |
| Engineer | cache.py | ✅ |
| Innovator | voice_coach.py | ✅ |

### Iteration 4 (Real-Time + Social)
| Agent | Task | Status |
|-------|------|--------|
| Worker | exercise_classifier.py | ✅ |
| Worker | sensor_hub.py | ✅ |
| Engineer | job_queue.py | ✅ |
| Innovator | workout_rooms.py | ✅ |
| Engineer | deduplication.py | ✅ |

### Iteration 5 (Health & Wellness)
| Agent | Task | Status |
|-------|------|--------|
| Worker | health_conditions.py | ✅ |
| Worker | diet_logging.py | ✅ |
| Innovator | meditation.py | ✅ |
| Innovator | health_advisor.py | ✅ |
| Worker | schedule.py | ✅ |

---

## Inventory After Iteration 5

| Category | Count |
|----------|-------|
| Backend Services | **46** (+4) |
| Core Modules | **9** |
| API Endpoints | **280+** (+20) |
| Mobile Components | **23** |
| WebSocket Endpoints | **4** |
| Meditation Sessions | **8** |
| Health Conditions Tracked | **40+** |
| Medication Interactions | **10** |
| Exercise Restriction Rules | **15** |

---

## Next Iteration Planning

### Iteration 6 Candidates
- **Innovator**: AI-powered symptom checker with web search integration
- **Worker-1**: Build all meditation API endpoints
- **Worker-2**: Build health advisor API endpoint
- **Engineer**: Add circuit breaker to all LLM calls
- **Architect**: Design unified biometric data model
- **UI/UX**: Build health conditions mobile screen
- **Security**: Review all new endpoints
- **Data Engineer**: Analytics schema for cross-metric correlations

### Iteration 7 Candidates
- **Innovator**: Workout music BPM auto-sync with heart rate
- **Worker**: Body composition photo timeline component
- **Engineer**: Add request deduplication to all POST endpoints
- **UI/UX**: Build diet logging daily chart screen
- **Architect**: Design microservice boundaries for scaling

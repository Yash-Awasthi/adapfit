# AdapFit AI-Loop — Enterprise-Grade Parallel Work Streams

**Current State: 113 iterations, 218 tests, 240+ API endpoints, 33 backend services, 21 mobile components**

---

## Loop Rules

- **MAX PARALLELIZATION**: Multiple independent tasks per iteration
- **NO TESTS**: Tests go in `TEST-LOOP.md` — never create or run tests here
- **PONYTAIL MODE**: Simplest solution that works. Stdlib before custom. No over-engineering.
- **VERIFY THEN BUILD**: Each stream owns its own verification
- **ITERATE UNTIL USER SAYS STOP**

---

## Work Streams (Run in Parallel)

### STREAM A: AI/ML — Computer Vision & Body Intelligence

**Goal**: Enterprise-grade computer vision for form correction, body composition analysis, and real-time coaching.

| Task | Research Source | Priority |
|------|----------------|----------|
| A1: MediaPipe Pose integration for real-time rep counting (33 landmarks, angle-based rep detection) | [GC_Fit](https://github.com/topics/ai-fitness), [FormAI](https://discuss.huggingface.co/t/175699) | HIGH |
| A2: Joint angle calculation engine (shoulder, elbow, hip, knee) with form scoring A-F | [AI Fitness Trainer](https://learnopencv.com/ai-fitness-trainer-using-mediapipe/) | HIGH |
| A3: Exercise classification from pose keypoints using lightweight classifier (TFLite/ONNX) | [exercise-recognition](https://github.com/topics/exercise-recognition) | HIGH |
| A4: Camera-based HRV via rPPG (remote photoplethysmography) — estimate HR/HRV from face video | [pyVHR](https://github.com/phuselab/pyVHR), [advanced-rppg](https://pypi.org/project/advanced-rppg/) | MEDIUM |
| A5: Fatigue detection from facial landmarks (eye aspect ratio, head tilt, yawn detection) | [fatigue-detection](https://github.com/topics/fatigue-detection) | MEDIUM |
| A6: Food photo recognition via Gemini Vision API — snap meal, auto-detect macros | [OpenNutriTracker](https://github.com/topics/calories-tracker), [Fud AI](https://github.com/apoorvdarshan/fud-ai) | HIGH |
| A7: Body composition estimation from photos (waist/shoulder ratio, visual BF% estimation) | Research: use anthropometric formulas with CV measurements | MEDIUM |
| A8: Self-evolving AI personalization engine — tracks user patterns, adjusts recommendations over time using RL-style feedback loop | [EvoAgentX](https://github.com/EvoAgentX/Awesome-Self-Evolving-Agents) | HIGH |
| A9: Anomaly detection for biometric data — z-score + Isolation Forest for outlier vitals | Build on existing ml_engine.py | HIGH |
| A10: NLP intent classifier upgrade — multi-turn conversation context, memory retrieval | Build on existing intent_classifier.py | MEDIUM |

### STREAM B: Connection — Sensors, Wearables, Health APIs

**Goal**: Deep integration with every health sensor and platform available.

| Task | Research Source | Priority |
|------|----------------|----------|
| B1: Health Connect v2 SDK — full data types: SleepSession, HeartRate, HRV, VO2Max, RestingHeartRate, BloodOxygen, Steps, Calories | [Health Connect](https://developer.android.com/health-and-fitness/health-connect) | HIGH |
| B2: BLE heart rate monitor pairing — real-time HR streaming during workouts | [Open Wearables](https://openwearables.io/docs/sdk/android) | HIGH |
| B3: Samsung Health API integration for Galaxy Watch users | [Samsung Health Blog](https://developer.samsung.com/health/blog/en/accessing-samsung-health-data-through-health-connect) | MEDIUM |
| B4: Fitbit Web API bridge for Fitbit users | REST API integration | MEDIUM |
| B5: Continuous Glucose Monitor (CGM) data ingestion — Libre, Dexcom | Research: Abbott/Dexcom developer APIs | LOW |
| B6: Blood pressure monitor integration — Withings, Omron BLE | BLE protocol research | LOW |
| B7: SpO2 sensor data pipeline — Oximeter BLE data collection | Bluetooth SIG SpO2 profile | MEDIUM |
| B8: Step counter with floor detection — indoor/outdoor activity classification | Accelerometer + barometer fusion | MEDIUM |
| B9: GPS route tracking for outdoor workouts — pace, elevation, map overlay | Expo Location + polyline | HIGH |
| B10: Real-time WebSocket sensor hub — multiple BLE devices streaming simultaneously | Build on existing ws_manager.py | HIGH |

### STREAM C: Code Quality — Enterprise Hardening

**Goal**: Production-ready code with proper error handling, security, and performance.

| Task | Details | Priority |
|------|---------|----------|
| C1: Structured logging everywhere — JSON logs with correlation IDs, request tracing | Build on existing logging_config.py | HIGH |
| C2: Input validation hardening — Pydantic v2 strict mode, SQL injection prevention | Audit all endpoints | HIGH |
| C3: API versioning strategy — v1 stable, v2 for breaking changes | Build on existing API_V1_STR | MEDIUM |
| C4: Circuit breaker pattern for external API calls (Gemini, Groq) — retry with exponential backoff | Add to LLM clients | HIGH |
| C5: Database connection pooling — asyncpg pool for Supabase, connection recycling | Configuration layer | HIGH |
| C6: Request deduplication — idempotency keys for POST endpoints | Middleware layer | MEDIUM |
| C7: Memory optimization — lazy loading, LRU caching for hot paths | Profile and optimize | MEDIUM |
| C8: Type safety audit — mypy strict mode, eliminate any/cast | Run mypy --strict | MEDIUM |
| C9: API response compression — gzip/Brotli for large responses | FastAPI middleware | LOW |
| C10: Graceful shutdown — drain connections, save state on SIGTERM | Lifespan handler | MEDIUM |

### STREAM D: UI/UX — Mobile App Polish

**Goal**: Professional, intuitive mobile experience that feels premium.

| Task | Details | Priority |
|------|---------|----------|
| D1: Onboarding flow — 5-step wizard: goals, experience, equipment, schedule, injuries | New screen | HIGH |
| D2: Dark/Light theme toggle — system-aware, user-override | Theme context | HIGH |
| D3: Pull-to-refresh on all list screens | Consistent UX pattern | HIGH |
| D4: Skeleton loading states — shimmer placeholders during API calls | Component library | HIGH |
| D5: Haptic feedback — vibration on workout complete, PR achieved, timer end | Expo Haptics API | MEDIUM |
| D6: Push notification deep links — tap notification opens specific screen | Expo Notifications | HIGH |
| D7: Offline indicator banner — show connection status prominently | SyncStatusBadge enhancement | MEDIUM |
| D8: Gesture shortcuts — swipe left to delete, swipe right to complete | Gesture handler | MEDIUM |
| D9: Accessibility pass — VoiceOver/TalkBack labels, contrast ratios, font scaling | WCAG 2.1 AA | HIGH |
| D10: App icon + splash screen — branded launch experience | Expo splash config | MEDIUM |

### STREAM E: Architecture — System Design

**Goal**: Scalable, maintainable architecture for growth.

| Task | Details | Priority |
|------|---------|----------|
| E1: Event-driven architecture — pub/sub for workout events, recovery events, achievement unlocks | Build on ws_manager.py | HIGH |
| E2: Caching layer — Redis-compatible in-memory cache for hot data (exercises, recommendations) | LRU + TTL cache | HIGH |
| E3: Background job queue — async task processing for ML inference, data sync, notifications | Build on existing tasks endpoint | HIGH |
| E4: API gateway pattern — rate limiting, auth, request routing in single layer | Enhance existing auth.py | HIGH |
| E5: Schema-first development — OpenAPI spec as source of truth, codegen client | FastAPI auto-gen | MEDIUM |
| E6: Database migration strategy — versioned migrations, rollback support | Enhance existing SQL migrations | HIGH |
| E7: Service mesh simulation — health checks, circuit breakers, retry policies | Python patterns | MEDIUM |
| E8: Configuration management — env-based config, secrets rotation | Build on existing config.py | MEDIUM |
| E9: Observability dashboard — Grafana JSON for API metrics, error rates, latency | Build on existing metrics.py | MEDIUM |
| E10: Blue-green deployment config — zero-downtime deploys | Docker Compose enhancement | LOW |

### STREAM F: Feature Exploration — New Capabilities

**Goal**: Innovate with cutting-edge features that differentiate AdapFit.

| Task | Research Source | Priority |
|------|----------------|----------|
| F1: Menstrual cycle tracking — phase-aware workout recommendations (follicular/luteal/menstrual) | Health Connect menstrual API | MEDIUM |
| F2: Altitude training simulation — elevation-based workout adjustments | Barometric pressure data | LOW |
| F3: Social workout rooms — multiplayer workout sessions via WebSocket | Build on ws_chat.py | HIGH |
| F4: AI voice coach — real-time audio coaching during workouts (TTS + cue engine) | Build on voice_workout.py | HIGH |
| F5: Workout gamification — XP system, level progression, unlock exercises | Build on achievements_engine.py | MEDIUM |
| F6: Team challenges — corporate wellness, friend groups with shared leaderboards | Build on fitness_challenges.py | HIGH |
| F7: Recovery protocol generator — ice bath, massage, stretching based on workout type | Build on warmup_cooldown endpoint | MEDIUM |
| F8: Training logbook export — PDF generation with charts, PRs, progress photos | Build on export endpoint | MEDIUM |
| F9: Sleep coaching — personalized sleep schedule optimization based on training load | Build on sleep_analyzer.py | HIGH |
| F10: Adaptive deload weeks — auto-detect overreaching, suggest deload timing | Build on injury_risk_engine.py | HIGH |

---

## Parallel Execution Strategy

### Iteration 1: Foundation (Tasks A1, B1, C1, D1, E1, F1)
- **A1**: MediaPipe pose landmark extraction pipeline
- **B1**: Health Connect v2 data type mapping
- **C1**: Structured JSON logging with correlation IDs
- **D1**: Onboarding flow screen
- **E1**: Event bus for workout/recovery events
- **F1**: Menstrual cycle tracker endpoint

### Iteration 2: Core CV + Sensors (Tasks A2, A6, B2, B9, C2, D2)
- **A2**: Joint angle calculator for form scoring
- **A6**: Food photo recognition via Gemini Vision
- **B2**: BLE HR monitor pairing
- **B9**: GPS route tracking
- **C2**: Input validation hardening
- **D2**: Dark/Light theme

### Iteration 3: Intelligence + UX (Tasks A8, A9, B10, C3, C4, D3, D4)
- **A8**: Self-evolving personalization engine
- **A9**: Biometric anomaly detection
- **B10**: Real-time WebSocket sensor hub
- **C3**: API versioning
- **C4**: Circuit breaker for LLM calls
- **D3**: Pull-to-refresh + skeleton loading

### Iteration 4: Advanced Features (Tasks A3, A4, B3, C5, D5, E2, F4)
- **A3**: Exercise classification from keypoints
- **A4**: Camera-based HRV estimation
- **B3**: Samsung Health integration
- **C5**: Connection pooling
- **D5**: Haptic feedback
- **E2**: Caching layer
- **F4**: AI voice coach

### Iteration 5: Social + Polish (Tasks A5, A7, B4, C6, D6, E3, F3, F6)
- **A5**: Fatigue detection from face
- **A7**: Body composition from photos
- **B4**: Fitbit bridge
- **C6**: Request deduplication
- **D6**: Push notification deep links
- **E3**: Background job queue
- **F3**: Social workout rooms
- **F6**: Team challenges

### Iteration 6: Enterprise Ready (Tasks A10, B5-B8, C7-C10, D7-D10, E4-E10, F2, F5, F7-F10)
- All remaining tasks grouped by dependency
- Final polish pass
- Documentation generation

---

## Key Open-Source References

| Project | URL | What to Adopt |
|---------|-----|---------------|
| GC_Fit | github.com/topics/ai-fitness | MediaPipe pose + rep counter pattern |
| pyVHR | github.com/phuselab/pyVHR | rPPG for camera-based HRV |
| OpenNutriTracker | github.com/topics/calories-tracker | Food photo recognition flow |
| EvoAgentX | github.com/EvoAgentX/Awesome-Self-Evolving-Agents | Self-evolving agent patterns |
| Open Wearables | openwearables.io | Health Connect + Samsung Health SDK |
| Health Connect | developer.android.com/health-and-fitness/health-connect | Full vitals API |
| FormAI | discuss.huggingface.co/t/175699 | Real-time form analysis pipeline |
| DashSentinel | reddit.com/r/computervision | Fatigue detection architecture |

---

## Current Inventory

| Category | Count |
|----------|-------|
| Backend Services | 33 |
| API Endpoints | 240+ |
| Mobile Components | 21 |
| SQL Tables | 15 |
| RLS Policies | 45+ |
| Tests | 218 |
| CI/CD Jobs | 4 |
| Docker Services | 4 |

---

## Loop Status

| Iteration | Tasks Completed | Stream |
|-----------|----------------|--------|
| 0 | Verified all 218 tests pass, 240+ endpoints, 33 services | AUDIT |
| 1 | A1 (pose_estimation.py), B1 (health_connect_bridge.py), C1 (logging_config.py), D1 (onboarding.tsx), E1 (event_bus.py), F1 (cycle_tracking.py) | Foundation |
| 1 | A1, B1, C1, D1, E1, F1 | Foundation |
| 2 | A2 (form_scorer.py), A6 (food_vision.py), A8 (evolution_engine.py), B9 (gps_tracking.py), D2 (theme.ts) | Core CV + Sensors |
| 3 | A9 (anomaly_detector.py), C4 (circuit_breaker.py), E2 (cache.py), F4 (voice_coach.py) | Intelligence + Resilience |
| 4 | A3 (exercise_classifier.py), B10 (sensor_hub.py), E3 (job_queue.py), F3 (workout_rooms.py), C6 (deduplication.py) | Real-Time + Social |
| 5 | health_conditions.py, diet_logging.py, meditation.py, health_advisor.py, schedule.py | Health & Wellness |
| 6 | M1 (health.tsx), M2 (diet.tsx), M3 (MeditationPlayer.tsx), A4 (med_interactions.py), A7 (adaptive_workout.py), F5 (health_chat.py) | Mobile + Health AI |
| 3 | A8, A9, B10, C3, C4, D3, D4 | Intelligence + UX |
| 4 | A3, A4, B3, C5, D5, E2, F4 | Advanced Features |
| 5 | A5, A7, B4, C6, D6, E3, F3, F6 | Social + Polish |
| 6 | A10, B5-B8, C7-C10, D7-D10, E4-E10, F2, F5, F7-F10 | Enterprise Ready |

# AdapFit — road to a commercial release

Each phase is one working session. Every phase starts with an investigation
step: measure the current state, write down what was found, then decide the
concrete work. The bullets below are starting questions, not a fixed task list.
`plan.md` holds the defect history; this file holds what is left to ship.
`docs/PRODUCT_SCOPE.md` holds the positioning every phase works inside: consumer
wellness, India first, every feature kept, nothing diagnoses.

---

## Phase 6 — Monetisation (rest)

Decided 2026-09-29: every feature free at launch. Done in plan.md Part 20:
the per-account daily AI quota. Left for when paid tiers are wanted (owner's
decisions): tiers, INR prices, trial length, what stays free; a Play Console
and payments profile; then server-side entitlements, Google Play Billing,
restore purchases, refunds and receipts.

## Phase 7 — AI and data quality (rest)

Done in plan.md Part 18. Left:

- Photo measurement of skin spots (`lesion_measure.py`) is tested on synthetic
  images only; calibrate on real phone photos of moles with a coin (needs the
  owner's photos).
- `screen_reply` only reads English; screen replies in Hindi and other
  languages before the app offers them.
- Verify on a device: Health Connect deletion reaching the server, and the
  home screen with no check-in today.

## Phase 8 — Infrastructure and operations (rest)

Done in plan.md Part 17. Left:

- Staging on the free Render + Neon setup in `docs/DEPLOYMENT.md`: needs the
  owner's accounts there, a Groq or Gemini key, and a Sentry DSN (all free).
- Uptime monitor on `/health` (free UptimeRobot) once staging exists.
- Remote push (FCM): needs a Firebase project, and a server event worth
  pushing; every notification today is a local reminder.
- iOS project, build profile, HealthKit entitlement and sync (deferred).
- Expo past SDK 55 for the moderate advisories in `docs/SECURITY.md`.

## Phase 9 — User experience and quality (rest)

Done in plan.md Part 19. Left:

- Stroke rehab, chronic disease management, hospital at home and wound
  assessment are API-only; design each with a clinician before giving it a screen.
- Coach marketplace: rebuild only with verified, real practitioners.
- API-only features still without a screen: peer support, vaccination records
  (health passport), accessible workout alternatives, the accessibility API.
- With the owner, on their phone: camera heart rate, pose and sensors, and a
  BLE heart-rate strap; decide which wearables to keep for launch. Also a
  Health Connect record deleted on the phone disappearing after a sync.
- Sleep sounds stop listening if the screen turns off (JS timers pause); the
  screen stays on under a black overlay. Native metering would lift that.
- A "Text strings must be rendered within a <Text>" console error appears in
  development after some screen interactions; not yet traced to its screen.
- Onboarding asks only name and gender; goal, level and equipment keep the
  profile defaults until the user edits Personal Info.
- Localisation completeness; performance and app size; end-to-end tests for
  the core journeys (the adb walk in Part 19 is manual).

## Phase 10 — Launch readiness (rest)

Done in plan.md Part 21: prohibited-FDC check in the medicine lookup, store
listing and Health Connect declaration drafts, legal placeholders flagged.
Left:

- Owner: who reviews community reports (they land in the security audit log
  as `community_report`); choose the Play target audience (sign-up already
  refuses under-13s).
- Owner: company and legal entity, insurance, payment accounts; legal review
  of third-party data (Indian Medicine Dataset, NMC register search) and of
  `backend/app/legal/` with the `[...]` placeholders filled; appoint the
  Grievance Officer; SMTP; DigiLocker age verification for guardian consent;
  third-party penetration test; closed beta and feedback loop; support
  channel, incident response and breach notification procedure; store
  graphics, screenshots and the answers marked `[...]` in
  `docs/STORE_LISTING.md` and `docs/HEALTH_CONNECT_DECLARATION.md`.
- Re-run `python -m scripts.build_cdsco_fdc` when a new 26A notification is
  published; the 2024 list comes from Goa FDA's copy until CDSCO publishes a
  consolidated one.

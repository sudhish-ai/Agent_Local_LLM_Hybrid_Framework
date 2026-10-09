# ALHF V2 E2E FLOW

Last Updated:

2026-10-07

---

# PURPOSE

Defines the complete ALHF V2 end-to-end execution path.

This document is the source of truth for:

- Architecture
- Integration Testing
- Demo Readiness
- Release Readiness

No V3 work is allowed until V2 is fully implemented,
tested, demonstrated, and validated.

---

# GOLDEN RULE

V2 IS NOT COMPLETE WHEN

- Classes compile
- Unit tests pass
- Components exist

V2 IS COMPLETE WHEN

- Entire E2E flow works
- Previous functionality still works
- Two real domains work
- Integration tests pass
- Demo succeeds
- Regression suite passes

Only then can V3 begin.

---

# ALHF V2 EXECUTION FLOW

User Request

↓

Intent Understanding

↓

Domain Selection

↓

Capability Selection

↓

Workflow Planning

↓

Workflow Validation

↓

Execution Planning

↓

Execution

↓

Result Aggregation

↓

Final Outcome

---

# V2 FLOW BREAKDOWN

## STEP 1

User Request

Example:

"Book a hotel in Goa next weekend."

Status:

✅ Exists

Input provided by user.

---

## STEP 2

Intent Understanding

Purpose:

Determine user intent.

Example:

Travel Booking

Status:

❌ Not Implemented

Required Components:

IntentDefinition

IntentDetector

Integration Test Required:

Input

↓

Intent

---

## STEP 3

Domain Selection

Purpose:

Determine best domain.

Example:

Travel

Healthcare

Finance

Status:

⚠ Partially Complete

Completed:

✅ DomainDefinition

✅ DomainRegistry

✅ DomainLoader

✅ BaseRegistry

Missing:

❌ Domain Selection Logic

Integration Test Required:

Intent

↓

Domain

---

## STEP 4

Capability Selection

Purpose:

Select domain capabilities.

Example:

Travel Domain

↓

Hotel Search Capability

Status:

❌ Not Implemented

Required Components:

CapabilityDefinition

CapabilityRegistry

Capability Selection Engine

Integration Test Required:

Domain

↓

Capability

---

## STEP 5

Workflow Planning

Purpose:

Generate execution workflow.

Example:

Find Hotels

↓

Compare Prices

↓

Build Response

Status:

⚠ Existing V1 Work Present

Verification Pending

Required Validation:

Planner still works after V2 integration.

Integration Test Required:

Capability

↓

Workflow

---

## STEP 6

Workflow Validation

Purpose:

Verify workflow correctness.

Status:

❌ Not Implemented

Integration Test Required:

Workflow

↓

Validated Workflow

---

## STEP 7

Execution Planning

Purpose:

Convert workflow into executable plan.

Status:

❌ Not Implemented

Integration Test Required:

Workflow

↓

Execution Plan

---

## STEP 8

Execution

Purpose:

Execute plan.

Status:

❌ Not Implemented

Integration Test Required:

Plan

↓

Result

---

## STEP 9

Result Aggregation

Purpose:

Combine results.

Status:

❌ Not Implemented

Integration Test Required:

Results

↓

Final Result

---

## STEP 10

Final Outcome

Purpose:

Return user outcome.

Status:

❌ Not Implemented

---

# CURRENT FOUNDATION STATUS

Core Layer

✅ BaseRegistry

✅ LoaderResult[T]

✅ BaseLoader[TItem, TSource]

---

Domain Layer

✅ DomainDefinition

✅ DomainRegistry

✅ DomainLoader

---

Testing

✅ BaseRegistry Tests

✅ DomainDefinition Tests

✅ DomainRegistry Tests

✅ LoaderResult Tests

✅ BaseLoader Tests

✅ DomainLoader Tests

Total:

69 Passing Tests

---

# REQUIRED V2 DOMAINS

V2 is not complete until at least:

✅ Travel

✅ Healthcare

are proven end-to-end.

Additional domains are optional.

---

# REQUIRED V2 INTEGRATION TESTS

## Integration Test 1

Filesystem Domain Discovery

Path

↓

DomainLoader

↓

DomainDefinition

Status:

❌ Not Created

---

## Integration Test 2

Domain Registration Pipeline

Path

↓

DomainLoader

↓

DomainRegistry

Status:

❌ Not Created

---

## Integration Test 3

Intent To Domain

Input

↓

Intent

↓

Domain

Status:

❌ Not Created

---

## Integration Test 4

Domain To Capability

Domain

↓

Capability

Status:

❌ Not Created

---

## Integration Test 5

Capability To Workflow

Capability

↓

Workflow

Status:

❌ Not Created

---

## Integration Test 6

Full Travel Demo

User Request

↓

Intent

↓

Domain

↓

Capability

↓

Workflow

↓

Result

Status:

❌ Not Created

---

## Integration Test 7

Full Healthcare Demo

User Request

↓

Intent

↓

Domain

↓

Capability

↓

Workflow

↓

Result

Status:

❌ Not Created

---

# V2 EXIT CRITERIA

Before V3 begins:

All previous tests green.

Integration tests green.

Travel demo green.

Healthcare demo green.

No critical defects.

Working tree clean.

Demo recorded.

Demo validated.

LinkedIn publication material prepared.

---

# NEXT IMPLEMENTATION DECISION RULE

Before implementing any file ask:

Does this move V2 closer to:

Travel E2E Demo

or

Healthcare E2E Demo?

If NO:

Do not build it yet.

---

# CURRENT NEXT DECISION

Review:

Intent Layer

Determine minimum components required
to move from:

User Request

↓

Intent

without introducing unnecessary V3 abstractions.

---

# CORE PHILOSOPHY

Think Hard Once.

Implement Many Times.

Test Early.

Integrate Early.

Demo Early.

Prove Everything.

Then Move Forward.

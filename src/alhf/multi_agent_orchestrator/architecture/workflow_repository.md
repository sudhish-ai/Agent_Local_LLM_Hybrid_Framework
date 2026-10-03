# Workflow Repository

## Status

Implemented (V1)

Current Implementation:

- InMemoryWorkflowRepository

---

## Why Does This Module Exist?

The Workflow Repository exists to persist workflow state independently from workflow execution.

Workflow state is a business record.

Workflow execution is a runtime activity.

These responsibilities must remain separated.

Without a dedicated repository layer, runtime execution becomes tightly coupled to persistence concerns.

---

## Production Problems It Solves

### Workflow State Persistence

A workflow has lifecycle state:

- Created
- Running
- Completed
- Failed

This state must remain available beyond the execution process.

The repository provides persistent workflow state storage.

### Workflow Auditability

Enterprise systems require visibility into:

- Which workflow executed
- Current workflow status
- Workflow execution history

The Workflow Repository acts as the authoritative workflow record.

### Recovery Foundation

Recovery requires access to workflow state.

Without persistence, workflow recovery becomes difficult or impossible.

The repository provides the foundation for future recovery capabilities.

---

## Core Responsibilities

- Store workflow state
- Retrieve workflow state
- Update workflow state
- Archive workflow state

---

## What This Module Must Never Do

- Execute workflows
- Execute tasks
- Execute agents
- Schedule tasks
- Validate workflows
- Plan workflows
- Make governance decisions

---

## Ownership

Workflow Repository owns:

- Workflow persistence

Workflow Engine owns:

- Workflow lifecycle

Workflow Executor owns:

- Workflow execution

These boundaries must remain intact.

---

## Runtime Position

Workflow Engine
        ↓
Workflow Repository

Workflow Repository remains outside execution flow
and serves as the persistence boundary.

---

## Inputs

- WorkflowContext

---

## Outputs

- WorkflowContext

---

## Dependencies

None

Repository implementations should remain independent from execution logic.

---

## Architectural Decision

Lifecycle management and persistence are separate concerns.

Workflow Engine:

- Creates state
- Updates state
- Uses state

Workflow Repository:

- Stores state

The repository must never own business behavior.

---

## Current Strategy

Runtime V1 uses:

- In-memory storage

Purpose:

- Development
- Testing
- Runtime prototyping

---

## Future Extensions

### V2

- SQLite Repository
- File-Based Repository

### V3

- PostgreSQL Repository
- Distributed Persistence
- Event-Sourced Persistence
- Workflow History Storage

---

## Consequences Of Removal

Without this module:

- Workflow state becomes transient
- Recovery becomes more difficult
- Auditability decreases
- Persistence concerns leak into runtime execution

---

## Architectural Principle

Execution owns behavior.

Repositories own persistence.

These responsibilities must never be merged.

---

## One Sentence

Workflow Repository is the workflow persistence boundary of ALHF responsible for storing and retrieving workflow 
lifecycle state independently from execution logic.

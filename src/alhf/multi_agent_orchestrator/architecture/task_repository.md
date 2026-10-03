# Task Repository

## Status

Implemented (V1)

Current Implementation:

- InMemoryTaskRepository

---

## Why Does This Module Exist?

The Task Repository exists to persist task state independently from execution.

Execution components should focus on execution.

Persistence components should focus on state management.

Separating persistence from execution reduces coupling and enables future storage implementations.

---

## Production Problems It Solves

### Task State Persistence

Tasks have lifecycle state:

- Created
- Running
- Completed
- Failed

Execution state must survive beyond execution.

The Task Repository stores this state.

### Execution Auditability

Production systems require visibility into:

- What executed
- When it executed
- How it completed

The repository provides an authoritative source of task history.

### Runtime Recovery Foundation

Recovery mechanisms require persisted state.

Task state persistence provides the foundation for future recovery capabilities.

---

## Core Responsibilities

- Store task state
- Retrieve task state
- Update task state
- Archive task state

---

## What This Module Must Never Do

- Execute tasks
- Execute workflows
- Execute agents
- Schedule tasks
- Resolve dependencies
- Perform planning
- Perform governance decisions

---

## Ownership

Task Repository owns:

- Task persistence

Task Executor owns:

- Task execution

Workflow Repository owns:

- Workflow persistence

These responsibilities must remain independent.

---

## Runtime Position

Workflow Engine
        ↓
Workflow Executor
        ↓
Task Executor
        ↓
Task Repository

---

## Inputs

- TaskContext

---

## Outputs

- TaskContext

---

## Dependencies

None

Repository implementations should remain independent from runtime execution logic.

---

## Architectural Decision

State ownership and execution ownership must remain separate.

Task Executor changes task state.

Task Repository stores task state.

The repository must never execute business logic.

---

## Current Strategy

Runtime V1 uses:

- In-memory storage

Purpose:

- Local execution
- Testing
- Prototyping

---

## Future Extensions

### V2

- SQLite Repository
- File-Based Repository

### V3

- PostgreSQL Repository
- Distributed Persistence
- Event-Sourced Persistence

---

## Consequences Of Removal

Without this module:

- Task state becomes transient
- Runtime recovery becomes difficult
- Auditability decreases
- Execution becomes tightly coupled to persistence

---

## Architectural Principle

Execution changes state.

Repositories persist state.

These responsibilities must remain separate.

---

## One Sentence

Task Repository is the persistence boundary of ALHF task execution that stores task lifecycle state independently 
from execution logic, enabling auditability, recovery, and future persistence evolution.
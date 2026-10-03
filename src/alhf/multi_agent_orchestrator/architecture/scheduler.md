# Scheduler

## Status

Implemented (V1)

Current Implementation:

- InMemoryScheduler

---

## Why Does This Module Exist?

The Scheduler exists to control task dispatch.

The scheduler is responsible for determining which executable task should be dispatched next.

It provides a separation between:

- Execution Planning
- Execution Dispatch

Without this separation, execution coordination becomes tightly coupled to workflow execution.

---

## Production Problems It Solves

### Dispatch Coordination

Multiple tasks may be ready for execution.

A dedicated scheduler provides a centralized place for task dispatch decisions.

### Scheduling Strategy Isolation

Execution strategy should not be embedded inside:

- Workflow Engine
- Workflow Executor
- Task Executor

The Scheduler isolates scheduling concerns.

### Future Scalability

Scheduling strategies evolve over time.

Examples:

- FIFO Scheduling
- Priority Scheduling
- Dependency-Aware Scheduling
- Parallel Scheduling
- Distributed Scheduling

The Scheduler provides the extension point.

---

## Core Responsibilities

- Accept executable tasks
- Queue executable tasks
- Dispatch executable tasks
- Pause scheduling
- Resume scheduling

---

## What This Module Must Never Do

- Create workflows
- Execute workflows
- Execute tasks
- Execute agents
- Resolve dependencies
- Validate workflows
- Enforce governance policies

---

## Ownership

Scheduler owns:

- Task dispatch

Workflow Executor owns:

- Execution orchestration

Dependency Resolver owns:

- Dependency enforcement

Task Executor owns:

- Task execution

---

## Runtime Position

Workflow Engine
        ↓
Execution Governor
        ↓
Workflow Validator
        ↓
Workflow Executor
        ↓
Dependency Resolution
        ↓
Scheduler
        ↓
Task Executor

---

## Inputs

- Executable TaskDefinition

---

## Outputs

- Dispatchable TaskDefinition

---

## Dependencies

None

The Scheduler should remain independent from execution logic.

---

## Key Architectural Decision

Scheduler and Dependency Resolver are different components.

Dependency Resolver answers:

Can this task run?

Scheduler answers:

Which executable task should be dispatched next?

These responsibilities must remain separate.

---

## Current Strategy

Runtime V1 uses:

FIFO Scheduling

First task enqueued is the first task dispatched.

---

## Future Extensions

### V2

- Priority Scheduling
- Queue Policies
- Scheduling Metrics

### V3

- Parallel Scheduling
- Distributed Scheduling
- Intelligent Scheduling
- Resource-Aware Scheduling

---

## Consequences Of Removal

Without a Scheduler:

- Dispatch logic spreads across runtime components.
- Scheduling strategies become difficult to evolve.
- Runtime coupling increases.

---

## Architectural Principle

Execution eligibility and execution dispatch are different concerns.

Dependency Resolver determines eligibility.

Scheduler determines dispatch order.

---

## One Sentence

Scheduler is the dispatch-control layer of ALHF that manages executable task queues and scheduling policies while 
remaining independent from workflow orchestration and task 

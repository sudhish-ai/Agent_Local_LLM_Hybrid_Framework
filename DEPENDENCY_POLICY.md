<!--
SPDX-FileCopyrightText: 2026 Sudhish Singh
SPDX-License-Identifier: MIT
Owner: Sudhish Singh
-->

# Dependency Policy

This project is built from scratch for mastery and production-grade understanding.

## Not Allowed in Core Implementation

- LangChain
- LangGraph
- CrewAI
- LlamaIndex
- Haystack
- AutoGen
- Semantic Kernel

## Allowed by Default

- Python standard library
- typing
- dataclasses
- pathlib
- hashlib
- json
- csv
- logging
- asyncio
- concurrent.futures
- sqlite3 when needed

## Allowed Only Behind Adapters

- PDF parser
- DOCX parser
- OCR engine
- embedding runtime
- vector database client
- LLM runtime client

## Design Rule

Core abstractions must remain framework-independent.

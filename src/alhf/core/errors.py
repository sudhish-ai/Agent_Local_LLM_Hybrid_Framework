# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh

"""Global error taxonomy for ALHF.

Design rule:
- Raise exceptions for fatal configuration or programmer errors.
- Return PipelineResult for per-record operational failures.
- Keep errors structured so logs, audit trails, tests, retry policies, and
  observability systems can reason about them.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

from alhf.core.status import ErrorSeverity


class ALHFError(Exception):
    """Base exception for all ALHF package errors.

    Attributes:
        message: Human-readable error message.
        error_code: Stable machine-readable error code.
        retryable: Whether retrying the same operation may succeed.
        severity: Error severity.
        details: Optional structured context.

    This class is intentionally structured instead of relying only on raw
    Python exception messages. Production systems need machine-readable error
    codes, retry hints, severity, and structured diagnostic details.
    """

    default_error_code = "ALHF_ERROR"
    default_retryable = False
    default_severity = ErrorSeverity.ERROR

    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[str] = None,
        retryable: Optional[bool] = None,
        severity: Optional[ErrorSeverity] = None,
        details: Optional[Mapping[str, Any]] = None,
    ) -> None:
        normalized_message = message.strip() if message else ""

        if not normalized_message:
            raise ValueError("Error message cannot be empty")

        self.message = normalized_message
        self.error_code = error_code or self.default_error_code
        self.retryable = self.default_retryable if retryable is None else retryable
        self.severity = severity or self.default_severity
        self.details = dict(details or {})

        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation of the exception."""

        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "retryable": self.retryable,
            "severity": self.severity.value,
            "details": self.details,
        }


class ConfigurationError(ALHFError):
    """Invalid configuration or unsafe runtime setting."""

    default_error_code = "CONFIGURATION_ERROR"
    default_retryable = False
    default_severity = ErrorSeverity.CRITICAL


class ValidationError(ALHFError):
    """Invalid input or invalid domain object."""

    default_error_code = "VALIDATION_ERROR"
    default_retryable = False


class IngestionError(ALHFError):
    """Base ingestion error."""

    default_error_code = "INGESTION_ERROR"


class FileDiscoveryError(IngestionError):
    """File discovery failed."""

    default_error_code = "FILE_DISCOVERY_ERROR"


class ExtractionError(IngestionError):
    """Document text extraction failed."""

    default_error_code = "EXTRACTION_ERROR"


class UnsupportedFileTypeError(ExtractionError):
    """Unsupported file type."""

    default_error_code = "UNSUPPORTED_FILE_TYPE"
    default_retryable = False


class CorruptDocumentError(ExtractionError):
    """Document appears corrupt or unreadable."""

    default_error_code = "CORRUPT_DOCUMENT"
    default_retryable = False


class ChunkingError(ALHFError):
    """Chunk creation failed."""

    default_error_code = "CHUNKING_ERROR"


class EmbeddingError(ALHFError):
    """Embedding generation failed."""

    default_error_code = "EMBEDDING_ERROR"
    default_retryable = True


class IndexingError(ALHFError):
    """Index write/read failed."""

    default_error_code = "INDEXING_ERROR"
    default_retryable = True


class RetrievalError(ALHFError):
    """Retrieval failed."""

    default_error_code = "RETRIEVAL_ERROR"
    default_retryable = True


class RerankingError(ALHFError):
    """Reranking failed."""

    default_error_code = "RERANKING_ERROR"
    default_retryable = True


class ContextPackingError(ALHFError):
    """Context packing failed."""

    default_error_code = "CONTEXT_PACKING_ERROR"
    default_retryable = False


class GenerationError(ALHFError):
    """Answer generation failed."""

    default_error_code = "GENERATION_ERROR"
    default_retryable = True


class SecurityError(ALHFError):
    """Security policy violation."""

    default_error_code = "SECURITY_ERROR"
    default_retryable = False
    default_severity = ErrorSeverity.CRITICAL


class AccessDeniedError(SecurityError):
    """User is not authorized for the requested content."""

    default_error_code = "ACCESS_DENIED"


class PromptInjectionRiskError(SecurityError):
    """Prompt injection risk detected."""

    default_error_code = "PROMPT_INJECTION_RISK"


class SensitiveDataLeakRiskError(SecurityError):
    """Potential sensitive-data leakage detected."""

    default_error_code = "SENSITIVE_DATA_LEAK_RISK"


class DataProtectionError(SecurityError):
    """Data protection, encryption boundary, or redaction failure."""

    default_error_code = "DATA_PROTECTION_ERROR"


class GuardrailError(ALHFError):
    """Guardrail evaluation failed."""

    default_error_code = "GUARDRAIL_ERROR"


class GovernanceError(ALHFError):
    """Governance, policy registry, approval, or decision-log error."""

    default_error_code = "GOVERNANCE_ERROR"


class RedTeamError(ALHFError):
    """Red-team scenario execution or finding generation failed."""

    default_error_code = "REDTEAM_ERROR"


class MCPProtocolError(ALHFError):
    """MCP-style protocol message or contract error."""

    default_error_code = "MCP_PROTOCOL_ERROR"


class ToolExecutionError(ALHFError):
    """Tool execution failed."""

    default_error_code = "TOOL_EXECUTION_ERROR"
    default_retryable = True


class LLMRuntimeError(ALHFError):
    """Local LLM runtime failure."""

    default_error_code = "LLM_RUNTIME_ERROR"
    default_retryable = True


class LLMInferenceError(ALHFError):
    """Local or remote LLM inference failed."""

    default_error_code = "LLM_INFERENCE_ERROR"
    default_retryable = True


class APIError(ALHFError):
    """API-layer error."""

    default_error_code = "API_ERROR"


class ServerLifecycleError(ALHFError):
    """ASGI/Uvicorn server lifecycle error."""

    default_error_code = "SERVER_LIFECYCLE_ERROR"
    default_severity = ErrorSeverity.CRITICAL


class StorageError(ALHFError):
    """Storage or persistence failure."""

    default_error_code = "STORAGE_ERROR"
    default_retryable = True


class EvaluationError(ALHFError):
    """Evaluation failed."""

    default_error_code = "EVALUATION_ERROR"


class OrchestrationError(ALHFError):
    """Agentic orchestration failed."""

    default_error_code = "ORCHESTRATION_ERROR"

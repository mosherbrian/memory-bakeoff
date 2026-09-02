"""Frozen Generation 19 Graphiti coding/experimental-memory profile.

This profile is deliberately domain-general and is not derived from held-out
queries.  It is a separately labeled Graphiti configured-product profile.
"""
from pydantic import BaseModel


class ArtifactResource(BaseModel):
    """A named repository, file, branch, credential, endpoint, identifier, or build artifact."""


class SystemComponent(BaseModel):
    """A named model, server, runtime, service, tool, host, hardware device, or software component."""


class Configuration(BaseModel):
    """A named release channel, quantization, flag set, context setting, version, or inference parameter set."""


class Environment(BaseModel):
    """A named machine, deployment, project, repository scope, or operating context."""


class ProcedureCommand(BaseModel):
    """A concrete command, workflow, operational procedure, or debugging procedure."""


class MeasurementResult(BaseModel):
    """A named throughput, latency, memory-use, quality, evaluation result, or other observed outcome."""


class DecisionConclusion(BaseModel):
    """A settled conclusion, selected approach, rejected approach, or verified finding."""


class GeneralRelation(BaseModel):
    """General relationship: HAS_VALUE, CONFIGURED_WITH, RUNS_ON, USES, LOCATED_AT, MEASURED_AS, PRODUCED, APPLIES_TO, OWNED_BY, REPLACES, CORRECTS, INVALIDATES, SUCCEEDED_WITH, FAILED_WITH, or SCOPED_TO."""


ENTITY_TYPES = {
    "ArtifactResource": ArtifactResource,
    "SystemComponent": SystemComponent,
    "Configuration": Configuration,
    "Environment": Environment,
    "ProcedureCommand": ProcedureCommand,
    "MeasurementResult": MeasurementResult,
    "DecisionConclusion": DecisionConclusion,
}
EDGE_TYPES = {"GENERAL_RELATION": GeneralRelation}
_NAMES = tuple(ENTITY_TYPES)
EDGE_TYPE_MAP = {(source, target): ["GENERAL_RELATION"] for source in _NAMES for target in _NAMES if source != target}
EXTRACTION_INSTRUCTIONS = (
    "Extract every explicit, concrete coding or experimental-memory fact using the provided general entity and relation schema. "
    "Treat a named release channel, configuration, procedure, command, branch, file, endpoint, identifier, or measurement as an entity when it participates in a stated relationship. "
    "Preserve exact literals. Do not create entities or facts that are not supported by the episode."
)

"""Minimal vendoring shim for the Habitus core used by memory-bakeoff.

The memory/runtime modules are copied verbatim from upstream.  This shim avoids
importing optional UI/audio/agent modules that the benchmark does not exercise.
"""
from .pipeline import BaseAgenticMemoryRAG, HabitusAI, HabitusMemory, RecallResult

__all__ = ["HabitusAI", "HabitusMemory", "BaseAgenticMemoryRAG", "RecallResult"]

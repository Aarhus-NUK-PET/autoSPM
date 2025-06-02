"""
autoSPM package for brain mask generation and SPM registration via MATLAB.

Modules:
- autoSPMwMask: Main interface for generating white matter mask and performing SPM registration.
- getMNIpath.m / SPMregister.m: MATLAB scripts invoked through matlab.engine.

Public Functions:
- autoSPMwMask: Generates a white matter mask and co-registers to MNI.
- validate_inputs: Validates file paths, labels, and registration arguments.

Usage:
    from autoSPM import autoSPMwMask, validate_inputs
"""

from .autoSPMwMask import autoSPMwMask, validate_inputs

__all__ = ["autoSPMwMask", "validate_inputs"]
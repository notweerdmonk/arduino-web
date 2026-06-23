"""Per-board sketch assignment registry — delegates to arduino_sketch_tools."""

from arduino_sketch_tools.sketch_registry import SketchRegistry
from medminder_dash import state

_registry = SketchRegistry(state._upload_registry, state._upload_registry_lock)

get_assignment = _registry.get_assignment
set_assignment = _registry.set_assignment
clear_assignment = _registry.clear_assignment
get_all_assignments = _registry.get_all_assignments
reset_for_tests = _registry.reset_for_tests

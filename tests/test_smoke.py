"""
Smoke tests for TrustMesh packaging and baseline configurations.
"""

import unittest
import trustmesh
from trustmesh.models import EMBEDDING_MODEL_ID, get_model_registry

def test_version():
    """Assert trustmesh version is 0.1.0."""
    assert trustmesh.__version__ == "0.1.0"

def test_model_registry():
    """Assert declared open-weight models are properly registered."""
    registry = get_model_registry()
    assert "embedding" in registry
    assert registry["embedding"]["model_id"] == EMBEDDING_MODEL_ID

class SmokeTestSuite(unittest.TestCase):
    """Unittest compatible test case."""
    def test_version_unittest(self):
        self.assertEqual(trustmesh.__version__, "0.1.0")

    def test_model_registry_unittest(self):
        registry = get_model_registry()
        self.assertEqual(registry["embedding"]["model_id"], EMBEDDING_MODEL_ID)

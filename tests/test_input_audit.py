
from src.input_audit import audit_input


def test_unsupported_parameter_is_detected():
    intent = (
        "Create URLLC with a made-up parameter "
        "quantum_priority=10."
    )

    result = audit_input(intent)

    assert result["valid"] is False
    assert "quantum_priority" in result["unsupported_parameters"]


def test_supported_parameter_is_not_rejected():
    result = audit_input(
        "Create URLLC with latency_ms=5."
    )

    assert result["valid"] is True
    assert result["unsupported_parameters"] == []

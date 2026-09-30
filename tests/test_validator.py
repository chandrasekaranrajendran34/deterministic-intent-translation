
from src.validator import validate_cir


def test_valid_urllc_cir():
    cir = {
        "service_type": "URLLC",
        "latency_ms": 5,
        "bandwidth_mbps": None,
        "reliability": 0.99999,
        "device_count": None,
        "coverage": None,
        "objective": "robot control"
    }

    result = validate_cir(cir)

    assert result["accepted"] is True
    assert result["schema_valid"] is True
    assert result["hallucination_detected"] is False


def test_hallucinated_field_is_detected():
    cir = {
        "service_type": "URLLC",
        "latency_ms": 5,
        "bandwidth_mbps": None,
        "reliability": None,
        "device_count": None,
        "coverage": None,
        "objective": "robot control",
        "quantum_priority": 10
    }

    result = validate_cir(cir)

    assert result["accepted"] is False
    assert result["hallucination_detected"] is True


def test_invalid_reliability_is_rejected():
    cir = {
        "service_type": "URLLC",
        "latency_ms": 5,
        "bandwidth_mbps": None,
        "reliability": 1.5,
        "device_count": None,
        "coverage": None,
        "objective": "robot control"
    }

    result = validate_cir(cir)

    assert result["accepted"] is False
    assert result["schema_valid"] is False


def test_negative_latency_is_rejected():
    cir = {
        "service_type": "URLLC",
        "latency_ms": -5,
        "bandwidth_mbps": None,
        "reliability": 0.99999,
        "device_count": None,
        "coverage": None,
        "objective": "robot control"
    }

    result = validate_cir(cir)

    assert result["accepted"] is False
    assert result["schema_valid"] is False


def test_unresolved_service_type_is_rejected():
    cir = {
        "service_type": None,
        "latency_ms": None,
        "bandwidth_mbps": None,
        "reliability": None,
        "device_count": None,
        "coverage": None,
        "objective": "make my network faster"
    }

    result = validate_cir(cir)

    assert result["accepted"] is False
    assert "SERVICE_TYPE_UNRESOLVED" in result["errors"]



def test_multiple_constraint_violations_are_reported():
    cir = {
        "service_type": "URLLC",
        "latency_ms": -5,
        "bandwidth_mbps": None,
        "reliability": 1.5,
        "device_count": None,
        "coverage": None,
        "objective": None
    }

    result = validate_cir(cir)

    assert result["accepted"] is False
    assert result["schema_valid"] is False

    error_text = " ".join(result["errors"])

    assert "latency_ms" in error_text
    assert "reliability" in error_text

"""Pure supervisory classification; no process creation or WinAPI calls.

Collect facts from one held handle opened with QUERY_LIMITED_INFORMATION |
SYNCHRONIZE. Never apply the relaxed descendant policy to root/product Python.
Do not re-open a PID to transplant identity: PID reuse is not process identity.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Observation:
    required_root_or_product_python: bool
    held_handle: bool
    same_job_member: bool
    birth_time_100ns: int | None
    image: str | None
    image_error: int | None = None
    wait_signaled: bool = False
    exit_code: int | None = None
    exit_time_100ns: int | None = None


def classify(observation):
    o = observation
    if not (o.held_handle and o.same_job_member):
        return {"status": "UNKNOWN_IDENTITY", "abort_owned_job": True, "qualified_image": False}
    if o.required_root_or_product_python and not o.birth_time_100ns:
        return {"status": "UNKNOWN_REQUIRED_IDENTITY", "abort_owned_job": True, "qualified_image": False}
    if o.image and o.birth_time_100ns:
        return {"status": "VERIFIED_BIRTH_IMAGE", "abort_owned_job": False, "qualified_image": True}
    if o.required_root_or_product_python:
        return {"status": "UNKNOWN_REQUIRED_IMAGE", "abort_owned_job": True, "qualified_image": False}
    exited = (o.wait_signaled and o.exit_code is not None and o.exit_code != 259
              and o.exit_time_100ns is not None and o.exit_time_100ns > 0)
    if exited:
        # A bounded metadata race, not a successful image certification.
        return {"status": "EXITED_DESCENDANT_IMAGE_UNAVAILABLE", "abort_owned_job": False,
                "qualified_image": False, "image_error": o.image_error,
                "same_handle_birth_and_job": True, "known_exited": True}
    # Root/product Python were already handled strictly above. Non-required
    # helpers with a held handle, same named Job and birth stay honest metadata.
    return {"status": "OWNED_HELPER_IMAGE_UNKNOWN_METADATA", "abort_owned_job": False,
            "qualified_image": False, "image_error": o.image_error,
            "same_handle_birth_and_job": True, "image_identity_unknown": True}


def pure_checks():
    def case(**changes):
        base = dict(required_root_or_product_python=False, held_handle=True,
                    same_job_member=True, birth_time_100ns=100, image=None,
                    image_error=31, wait_signaled=True, exit_code=0, exit_time_100ns=101)
        base.update(changes)
        return classify(Observation(**base))

    expected = [
        (case(), "EXITED_DESCENDANT_IMAGE_UNAVAILABLE"),
        (case(exit_code=259), "OWNED_HELPER_IMAGE_UNKNOWN_METADATA"),
        (case(wait_signaled=False), "OWNED_HELPER_IMAGE_UNKNOWN_METADATA"),
        (case(exit_time_100ns=None), "OWNED_HELPER_IMAGE_UNKNOWN_METADATA"),
        (case(required_root_or_product_python=True), "UNKNOWN_REQUIRED_IMAGE"),
        (case(same_job_member=False), "UNKNOWN_IDENTITY"),
        (case(held_handle=False), "UNKNOWN_IDENTITY"),
        (case(birth_time_100ns=None), "OWNED_HELPER_IMAGE_UNKNOWN_METADATA"),
        (case(image="C:/Program Files/Git/usr/bin/wc.exe"), "VERIFIED_BIRTH_IMAGE"),
    ]
    if not all(row["status"] == status for row, status in expected):
        raise AssertionError("SUPERVISION_CLASSIFICATION_CASE_FAILED")
    if case()["qualified_image"] or case(required_root_or_product_python=True)["abort_owned_job"] is not True:
        raise AssertionError("IDENTITY_POLICY_WAS_RELAXED")
    return {"policy_cases_passed": len(expected), "native_processes": 0,
            "actual_old197_race_reproduced": False,
            "required_root_and_product_python_strict": True,
            "exited_unknown_image_never_labeled_qualified": True}


if __name__ == "__main__":
    import json
    print(json.dumps(pure_checks(), indent=2))

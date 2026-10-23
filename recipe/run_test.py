"""Run langsmith's pytest suite against the built package.

langsmith's own code imports httpx2 aliased as `httpx` (see
langsmith/_openapi_client/_httpx.py), but several test modules still
`import httpx` directly, pre-dating the httpx2 migration. httpx2.alias_httpx()
makes `import httpx` resolve to httpx2 process-wide; it must run before
anything else imports httpx, which is why this lives in its own run_test.py
instead of a conftest.py or a plugin. This matches upstream's own test setup
(see tests/httpx2_alias/sitecustomize.py + PYTHONPATH in upstream's Makefile).
"""

import sys

import httpx2

httpx2.alias_httpx()

import pytest  # noqa: E402  (must follow alias_httpx())

IGNORE = [
    # tests/integration_tests (incl. wrappers/) needs a live LangSmith backend +
    # API key (e.g. 401 Client Error: Unauthorized for url: api.smith.langchain.com);
    # core client behavior is covered by unit_tests.
    "tests/integration_tests",
    # openai.OpenAIError: api_key client option must be set / OPENAI_API_KEY env var
    "tests/external/test_instructor_evals.py",
    # deepagents has no main-channel build.
    "tests/external/test_deepagent_compat.py",
    # requests.exceptions.HTTPError: 401 Client Error: Unauthorized for url: api.smith.langchain.com
    "tests/evaluation/test_evaluation.py",
    # pytest-httpx has no main-channel build — these sandbox tests import it.
    "tests/unit_tests/sandbox/test_access_delegation.py",
    "tests/unit_tests/sandbox/test_async_client.py",
    "tests/unit_tests/sandbox/test_async_sandbox.py",
    "tests/unit_tests/sandbox/test_aws_role_auth.py",
    "tests/unit_tests/sandbox/test_client.py",
    "tests/unit_tests/sandbox/test_proxy_config.py",
    "tests/unit_tests/sandbox/test_run_config_and_files.py",
    "tests/unit_tests/sandbox/test_sandbox.py",
    # strands-agents has no main-channel build.
    "tests/unit_tests/wrappers/test_strands_agents.py",
    # google-adk has no main-channel build.
    "tests/unit_tests/wrappers/test_google_adk.py",
    # respx has no main-channel build — this generated-client test imports it.
    "tests/test_client.py",
    # New 0.14.x sandbox tests; pytest-httpx has no main-channel build.
    "tests/unit_tests/sandbox/test_endpoints.py",
    "tests/unit_tests/sandbox/test_tracing.py",
    "tests/unit_tests/sandbox/test_verify.py",
    #  ModuleNotFoundError: No module named 'bench'
    "tests/unit_tests/test_background_thread.py",
]

DESELECT = [
    # Windows-only, deterministic: the fixture hardcodes pathlib.Path("/a/b")
    # expecting forward-slash JSON output, but WindowsPath renders it with
    # backslashes. Deselecting a non-matching id on other platforms is a no-op.
    "tests/unit_tests/secret/test_secret_serde.py"
    "::test_output_is_unchanged_for_payloads_without_secrets[path]",
]

args = ["-v", "tests"]
args += [f"--ignore={path}" for path in IGNORE]
args += [f"--deselect={node_id}" for node_id in DESELECT]
# A couple of test_multipart_retry_matrix.py cases race a background thread
# against a mock server and occasionally capture an extra log line; upstream's
# own dev group carries pytest-rerunfailures for the same reason.
args += ["--reruns=2"]

sys.exit(pytest.main(args))

#!/usr/bin/env python3
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import os
import subprocess
from asyncio import sleep
from typing import Any, AsyncGenerator

import pytest
from pytest_operator.plugin import OpsTest

logger = logging.getLogger(__name__)

MICROK8S_CLOUD_NAME = "uk8s"


@pytest.fixture(autouse=True, scope="module")
def opensearch_sysctl_settings():
    """Necessary settings for Opensearch

    This should probably rather go to ci.yaml"""
    subprocess.run(["sudo", "sysctl", "-w", "vm.swappiness=0"])
    subprocess.run(["sudo", "sysctl", "-w", "vm.max_map_count=262144"])
    subprocess.run(["sudo", "sysctl", "-w", "net.ipv4.tcp_retries2=5"])


@pytest.fixture
def charmk8s(charm_base):
    """Path to the k8s charm file to use for testing."""
    # Return str instead of pathlib.Path since python-lib juju's model.deploy(), juju deploy, and
    # juju bundle files expect local charms to begin with `./` or `/` to distinguish them from
    # Charmhub charms.
    return f"./opensearch-dashboards-k8s_{charm_base}-amd64.charm"


@pytest.fixture
def application_charm() -> str:
    """Path to the application charm to use for testing."""
    return "./tests/integration/dashboards_application_charm/application_ubuntu@24.04-amd64.charm"


@pytest.fixture
def dashboard_tester_charm() -> str:
    """Path to the application charm to use for testing."""
    return "./tests/integration/dashboards_tester_charm/dashboard-tester_ubuntu@24.04-amd64.charm"


def pytest_configure(config):
    if not getattr(config.option, "cloud", None):
        config.option.cloud = "uk8s"


class Flags:
    def __init__(self):
        self.test_tls = os.environ.get("TEST_TLS", "false").lower() == "true"
        self.traefik = os.environ.get("TEST_TRAEFIK", "false").lower() == "true"
        self.transfer_traefik_ca = os.environ.get("TRANSFER_TRAEFIK_CA", "false").lower() == "true"


@pytest.fixture(scope="class")
def test_flags() -> Flags:
    """Fixture to provide TLS and Traefik configuration groups from Spread."""
    return Flags()


@pytest.fixture(scope="module")
async def ops_test_vm(
    request, tmp_path_factory, ops_test: OpsTest
) -> AsyncGenerator[OpsTest, Any]:
    """Returns a VM OpsTest.

    When the primary substrate is k8s (ops_test points to k8s), this fixture creates and
    manages a secondary VM model for OpenSearch. When the primary substrate is vm, this
    fixture simply yields the same ops_test.
    """

    model_name = f"{ops_test.model_name}-vm"

    orig_cloud = getattr(request.config.option, "cloud", None)
    orig_model = getattr(request.config.option, "model", None)
    orig_alias = getattr(request.config.option, "model_alias", None)

    request.config.option.controller = ops_test.controller_name
    request.config.option.cloud = "localhost"
    request.config.option.model = model_name
    request.config.option.model_alias = model_name

    ops_res = OpsTest(request, tmp_path_factory)
    await ops_res._setup_model()

    request.config.option.cloud = orig_cloud
    request.config.option.model = orig_model
    request.config.option.model_alias = orig_alias

    yield ops_res

    if not ops_test.keep_model:
        await ops_res.forget_model(alias=model_name)
        await ops_res._controller.destroy_model(model_name, destroy_storage=True, force=True)
        while model_name in await ops_res._controller.list_models():
            await sleep(5)
    await ops_res._cleanup_models()

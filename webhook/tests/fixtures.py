# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from contextlib import contextmanager
from unittest import mock

from google.cloud import ndb
from google.cloud.ndb import context as context_module

import pytest


@pytest.fixture
def in_context(monkeypatch):
    """
    This fixture will create a context that won't connect to the datastore.
    At the same time it will mock context used in the code to do nothing
    to prevent double context creation.
    """
    ndb_client = mock.Mock(
        project="testing",
        namespace=None,
        stub=mock.Mock(spec=()),
        spec=("project", "namespace", "stub"),
    )
    context = context_module.Context(ndb_client).use()
    context.__enter__()

    class MockContext:
        @contextmanager
        def context(self):
            yield None

    def client():
        return MockContext()

    monkeypatch.setattr(ndb, 'Client', client)

    yield

    context.__exit__(None, None, None)


@pytest.fixture
def patch_transaction(monkeypatch):
    def transaction(func):
        func()

    monkeypatch.setattr(ndb, 'transaction', transaction)

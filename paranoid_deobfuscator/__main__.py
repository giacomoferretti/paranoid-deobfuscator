# Copyright 2024 Giacomo Ferretti
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

import click

from .commands import deobfuscate, helpers

logger = logging.getLogger(__name__)


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode")
def cli(verbose: bool):
    verbosity = logging.DEBUG if verbose else logging.INFO
    log_format = "[%(name)s:%(levelname)s] %(message)s" if verbose else "[%(levelname)s] %(message)s"

    logging.basicConfig(level=verbosity, format=log_format)


cli.add_command(deobfuscate.cli)
cli.add_command(helpers.cli)

if __name__ == "__main__":
    cli()

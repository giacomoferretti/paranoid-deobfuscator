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

__version_major__ = 3
__version_minor__ = 0
__version_patch__ = 1
__version_metadata__ = ""
__version__ = f"{__version_major__}.{__version_minor__}.{__version_patch__}{__version_metadata__}"
__issue_tracker__ = "https://github.com/giacomoferretti/paranoid-deobfuscator/issues"


def report_github_issue_message(data: str | None = None) -> str:  # pragma: no cover
    result = f"Please report this issue at {__issue_tracker__}"
    if data:
        result += f"\n\nReport information:\n{data}"
    return result

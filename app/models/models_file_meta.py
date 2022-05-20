# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from typing import Optional

from pydantic import BaseModel


class FileMetaCreation(BaseModel):
    """Create a File Info."""

    global_entity_id: str
    data_type: Optional[str] = 'File'
    operator: str
    zone: str
    file_size: int
    tags: list
    archived: bool
    location: str
    time_lastmodified: int
    time_created: int
    process_pipeline: str
    uploader: str
    file_name: str
    atlas_guid: str
    display_path: str
    project_code: str
    attributes: Optional[list] = []
    priority: Optional[int] = 20
    version: Optional[str] = None


class FileMetaUpdate(BaseModel):
    """Update a File Info."""

    global_entity_id: str
    updated_fields: dict

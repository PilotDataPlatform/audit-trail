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


class AuditLogCreation(BaseModel):
    """Create an Audit Log."""

    action: str
    operator: str
    target: str
    outcome: str
    resource: str
    display_name: str
    project_code: str
    extra: dict


class AuditLogQuery(BaseModel):
    """Query Audit Logs."""

    project_code: str
    action: Optional[str] = None
    resource: str
    operator: Optional[str] = None
    start_date: Optional[int] = None
    end_date: Optional[int] = None

"""medminder_dash/python/medminder_dash/medminder_dash/medicines_state.py

Medicine data model and persistent store.

Author: notweerdmonk
SPDX-License-Identifier: Apache-2.0

Copyright 2026 notweerdmonk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import copy
import json
import logging
import threading
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)


@dataclass
class Medicine:
    """A single medicine entry with schedule fields."""

    id: str = ""
    name: str = ""
    hour: int = 0
    minute: int = 0
    day_of_week: int = 0
    day_of_month: int = 0
    enabled: bool = True

    def __post_init__(self):
        """Generate a UUID id if none was provided."""
        if not self.id:
            self.id = uuid.uuid4().hex


def _compute_data_path() -> Path:
    """Return the filesystem path to the board_meta.json data file."""
    return Path(__file__).resolve().parent.parent / "data" / "board_meta.json"


class MedicineStore:
    """Thread-safe persistent store for medicine data per board port."""

    def __init__(self):
        self._lock = threading.Lock()
        self._data_file = _compute_data_path()
        self._board_meta: dict = {}
        self._medicines: list[Medicine] = []
        self._load()

    def _load(self):
        """Load board meta data from the JSON data file."""
        path = self._data_file
        if path.exists():
            try:
                raw = json.loads(path.read_text())
                self._board_meta = raw
            except Exception:
                logger.exception("Failed to load board meta, starting fresh")
                self._board_meta = {}
        else:
            self._board_meta = {}

    def _save(self):
        """Persist board meta data to the JSON data file."""
        if getattr(self, "_current_port", None):
            self._board_meta[self._current_port] = {"medicines": list(self._medicines)}
        serializable = {}
        for board, data in self._board_meta.items():
            meds = []
            for m in data.get("medicines", []):
                meds.append(asdict(m) if isinstance(m, Medicine) else m)
            serializable[board] = {"medicines": meds}
        path = self._data_file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(serializable, indent=2))

    def load_board(self, port: Optional[str]):
        """Load medicines for a given board port.

        Args:
            port: Board port string, or None to load nothing.
        """
        self._current_port = port
        self._medicines = []
        if port and port in self._board_meta:
            raw = self._board_meta[port].get("medicines", [])
            for item in raw:
                if isinstance(item, dict):
                    self._medicines.append(Medicine(**item))
                else:
                    self._medicines.append(item)

    def all(self) -> list:
        """Return a copy of all medicines.

        Returns:
            List of all Medicine instances.
        """
        with self._lock:
            return list(self._medicines)

    def only_enabled(self) -> list:
        """Return a list of only enabled medicines.

        Returns:
            List of enabled Medicine instances.
        """
        with self._lock:
            return [m for m in self._medicines if m.enabled]

    def add(self, medicine: Medicine) -> str:
        """Add a medicine to the store.

        Args:
            medicine: Medicine instance to add.

        Returns:
            The medicine's ID.
        """
        with self._lock:
            self._medicines.append(medicine)
            self._save()
        return medicine.id

    def get(self, med_id: str) -> Optional[Medicine]:
        """Retrieve a copy of a medicine by ID.

        Args:
            med_id: The medicine's unique ID.

        Returns:
            A copy of the Medicine, or None if not found.
        """
        with self._lock:
            for m in self._medicines:
                if m.id == med_id:
                    return copy.copy(m)
        return None

    def update(self, med_id: str, **kwargs):
        """Update fields on a medicine by ID.

        Args:
            med_id: The medicine's unique ID.
            **kwargs: Field name/value pairs to update.
        """
        with self._lock:
            for m in self._medicines:
                if m.id == med_id:
                    for k, v in kwargs.items():
                        setattr(m, k, v)
                    break
            self._save()

    def delete(self, med_id: str) -> bool:
        """Delete a medicine by ID.

        Args:
            med_id: The medicine's unique ID.

        Returns:
            True if deleted, False if not found.
        """
        with self._lock:
            before = len(self._medicines)
            self._medicines = [m for m in self._medicines if m.id != med_id]
            if len(self._medicines) == before:
                return False
            self._save()
        return True

    def toggle(self, med_id: str):
        """Toggle the enabled state of a medicine by ID.

        Args:
            med_id: The medicine's unique ID.
        """
        with self._lock:
            for m in self._medicines:
                if m.id == med_id:
                    m.enabled = not m.enabled
                    break
            self._save()


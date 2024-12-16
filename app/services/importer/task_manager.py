from typing import Dict
from app.models.importer import ImportTask, ImportEntry, ImportStatus

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, ImportTask] = {}

    def create_task(self, task_id: str, entity_type: str) -> ImportTask:
        task = ImportTask(task_id, entity_type)
        self.tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> ImportTask:
        return self.tasks.get(task_id)

    def add_entries_to_task(self, task_id: str, entries_data: list):
        task = self.get_task(task_id)
        for data in entries_data:
            task.entries.append(ImportEntry(data))

    def update_entry_status(self, task_id: str, entry_index: int, status: ImportStatus, error_message: str = None):
        task = self.get_task(task_id)
        entry = task.entries[entry_index]
        entry.status = status
        entry.error_message = error_message

task_manager = TaskManager()

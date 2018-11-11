import argparse
import socket
import time
import json
import uuid
import os.path
from collections import deque
from threading import Thread, RLock


class Task:
    def __init__(self, task_length,
                 task_data,
                 task_id=None,
                 task_created_at=None,
                 task_started_at=None):
        self.length = task_length
        self.data = task_data
        self.id = task_id or str(uuid.uuid4())
        self.created_at = task_created_at or time.time()
        self.started_at = task_started_at

    def info(self):
        return {"TASK_ID": self.id,
                "TASK_LENGTH": self.length,
                "TASK_DATA": self.data,
                "TASK_STARTED_AT": self.started_at,
                "TASK_CREATED_AT": self.created_at}


class TaskQueue:
    def __init__(self, queue_name):
        self.queue_name = queue_name
        self.tasks_undone = deque()
        self.tasks_in_progress = deque()

    def __contains__(self, task_id: str) -> bool:
        for task in self:
            if task.id == task_id:
                return True
        return False

    def __iter__(self):
        for task in self.tasks_undone:
            yield task
        for task in self.tasks_in_progress:
            yield task

    def info(self):
        with RLock():
            all_tasks = list()
            for task in self:
                all_tasks.append(task.info())
            return self.queue_name, all_tasks

    def _add_task_as_in_progress(self, task: Task):
        with RLock():
            if task.id not in self:
                self.tasks_in_progress.append(task)

    def _add_task_as_undone(self, task: Task):
        with RLock():
            if task.id not in self:
                index = 0
                for index, undone_task in enumerate(self.tasks_undone):
                    if task.created_at <= undone_task.created_at:
                        break
                    index += 1
                self.tasks_undone.insert(index, task)

    def add_task(self, task: Task) -> str:
        with RLock():
            if task.started_at:
                self._add_task_as_in_progress(task)
            else:
                self._add_task_as_undone(task)
            return task.id

    def get_task_to_execute(self) -> (Task, None):
        with RLock():
            if not len(self.tasks_undone):
                return None
            task = self.tasks_undone.popleft()
            task.started_at = time.time()
            self.tasks_in_progress.append(task)
            return task

    def confirm_execution(self, task_id: str) -> bool:
        with RLock():
            for index, task in enumerate(self.tasks_in_progress):
                if task.id == task_id:
                    del self.tasks_in_progress[index]
                    return True
            return False


class TaskQueueServer:
    def __init__(self, ip, port, path, timeout):
        self.ip = ip
        self.port = port
        self.path = path + 'backup.save'
        self.timeout = timeout
        self.queue_map = dict()
        freshness_checker = Thread(target=self.freshness_checker, args=())
        freshness_checker.start()

    def freshness_checker(self):
        while True:
            with RLock():
                for task_queue in self.queue_map.values():
                    for task in list(task_queue.tasks_in_progress):
                        if time.time() - task.started_at > self.timeout:
                            task_queue.tasks_in_progress.remove(task)
                            task.started_at = None
                            task_queue.add_task(task)
            time.sleep(1)

    def queue_add(self, arguments: list) -> bytes:
        if len(arguments) != 3:
            return b'ERROR'
        queue_name, length, data = arguments

        if queue_name not in self.queue_map:
            self.queue_map[queue_name] = TaskQueue(queue_name)
        new_task = Task(length, data)
        new_task_id = self.queue_map[queue_name].add_task(new_task)
        return new_task_id.encode()

    def queue_get(self, arguments: list) -> bytes:
        with RLock():
            if len(arguments) != 1:
                return b'ERROR'
            queue_name, = arguments

            if queue_name in self.queue_map:
                task_queue = self.queue_map[queue_name]
                task = task_queue.get_task_to_execute()
                if task:
                    return ' '.join([task.id, task.length, task.data]).encode()
            return b'NONE'

    def queue_ack(self, arguments: list) -> bytes:
        with RLock():
            if len(arguments) != 2:
                return b'ERROR'
            queue_name, task_id = arguments

            if queue_name in self.queue_map:
                task_queue = self.queue_map[queue_name]
                confirmed = task_queue.confirm_execution(task_id)
                if confirmed:
                    return b'YES'
            return b'NO'

    def queue_in(self, arguments: list) -> bytes:
        if len(arguments) != 2:
            return b'ERROR'
        queue_name, task_id = arguments
        if queue_name in self.queue_map:
            task_queue = self.queue_map[queue_name]
            if task_id in task_queue:
                return b'YES'
        return b'NO'

    def save(self, arguments):
        with RLock():
            if len(arguments) != 0:
                return b'ERROR'
            ark = list()
            for queue in self.queue_map.values():
                ark.append(queue.info())
            dump = json.dumps(ark, indent=4)
            with open(self.path, 'w') as f:
                f.write(dump)
            return b'SAVED'

    def load(self, arguments):
        with RLock():
            if not os.path.isfile(self.path) or len(arguments) != 0:
                return b'ERROR'
            with open(self.path, 'r') as f:
                ark = json.loads(f.read())
            for queue_info in ark:
                queue_name, queue_tasks = queue_info
                queue = TaskQueue(queue_name)
                self.queue_map[queue_name] = queue
                for task_info in queue_tasks:
                    task_length = task_info["TASK_LENGTH"]
                    task_data = task_info["TASK_DATA"]
                    task_id = task_info["TASK_ID"]
                    task_created_at = task_info["TASK_CREATED_AT"]
                    task_started_at = task_info["TASK_STARTED_AT"]
                    task = Task(task_length, task_data, task_id, task_created_at, task_started_at)
                    queue.add_task(task)
            return b'LOADED'

    def run(self):
        all_commands = {
            'ADD': self.queue_add,
            'GET': self.queue_get,
            'ACK': self.queue_ack,
            'IN': self.queue_in,
            'SAVE': self.save,
            'LOAD': self.load,
        }
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        connection.bind((self.ip, self.port))
        connection.listen(1)
        while True:
            current_connection, address = connection.accept()
            data = current_connection.recv(1024)
            data_args = data.split()
            if data_args[0] == b'ADD':
                while len(data_args) < 4:
                    data += current_connection.recv(1024)
                    data_args = data.split()
                length = int(data_args[2])
                while len(data_args[3]) < length:
                    data += current_connection.recv(1024)
                    data_args = data.split()
                if len(data_args[3]) != length:
                    current_connection.send(b'ERROR')
                    current_connection.close()
                    continue
            request = data.decode()
            request_args = request.split()

            command = None
            if len(request_args):
                command = request_args[0]

            func = all_commands.get(command, None)
            if func:
                response = func(request_args[1:])
            else:
                response = b'ERROR'

            current_connection.send(response)
            current_connection.close()


def parse_args():
    parser = argparse.ArgumentParser(description='This is a simple task queue server with custom protocol')
    parser.add_argument(
        '-p',
        action="store",
        dest="port",
        type=int,
        default=5555,
        help='Server port')
    parser.add_argument(
        '-i',
        action="store",
        dest="ip",
        type=str,
        default='0.0.0.0',
        help='Server ip adress')
    parser.add_argument(
        '-c',
        action="store",
        dest="path",
        type=str,
        default='./',
        help='Server checkpoints dir')
    parser.add_argument(
        '-t',
        action="store",
        dest="timeout",
        type=int,
        default=300,
        help='Task maximum GET timeout in seconds')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    server = TaskQueueServer(**args.__dict__)
    server.run()

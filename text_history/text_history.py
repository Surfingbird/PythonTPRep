class TextHistory:

    def __init__(self, text=""):
        self._text = text
        self._version = 0
        self._changes = dict()

    @property
    def text(self):
        return self._text

    @property
    def version(self):
        return self._version

    def action(self, action):
        if not (0 <= action.from_version < action.to_version):
            raise ValueError
        self._text = action.apply(self._text)
        self._version = action.to_version
        self._changes[self._version] = action
        return self._version

    def insert(self, text, pos=None):
        if pos is None:
            pos = len(self._text)
        if not (0 <= pos <= len(self._text)):
            raise ValueError
        action = InsertAction(pos, text, from_version=self._version, to_version=self._version + 1)
        self.action(action)
        return self._version

    def replace(self, text, pos=None):
        if pos is None:
            pos = len(self._text)
        if not (0 <= pos <= len(self._text)):
            raise ValueError
        action = ReplaceAction(pos, text, from_version=self._version, to_version=self._version + 1)
        self.action(action)
        return self._version

    def delete(self, pos, length):
        if not (0 <= pos <= pos + length <= len(self._text)):
            raise ValueError
        action = DeleteAction(pos, length, from_version=self._version, to_version=self._version + 1)
        self.action(action)
        return self._version

    def get_actions(self, from_version=None, to_version=None):
        if from_version is None:
            from_version = 0
        if to_version is None:
            to_version = len(self._changes)
        if not (0 <= from_version <= to_version <= self._version):
            raise ValueError
        raw_actions = [action for version, action in self._changes.items() if from_version < version <= to_version]
        optimiser = ActionOptimiser(raw_actions)
        optimised_actions = optimiser.optimise()
        return optimised_actions


class ActionOptimiser:
    def __init__(self, raw_actions):
        self.actions = raw_actions

    @staticmethod
    def get_stacks(actions):
        """
        Split stack with actions into smaller stacks with instances of the same *Action type.
        Rerurns splitted stacks
        """
        last_action = type(actions[0])
        stack = []
        stacks = []
        for action in actions:
            if type(action) == last_action:
                stack.append(action)
            else:
                stacks.append(stack.copy())
                stack.clear()
                last_action = type(action)
                stack.append(action)
        stacks.append(stack.copy())
        return stacks

    def optimise(self):
        optimised = []
        stacks = self.get_stacks(self.actions)
        for stack in stacks:
            stack_type = type(stack[0])
            opt_stack = stack_type.merge(stack)
            optimised += opt_stack
        return optimised


class Action:
    def __init__(self, pos, from_version, to_version):
        self.pos = pos
        self.from_version = from_version
        self.to_version = to_version


class InsertAction(Action):
    def __init__(self, pos, text, from_version, to_version):
        super().__init__(pos, from_version, to_version)
        self.text = text

    def __repr__(self):
        return f'insert(text="{self.text}", pos={self.pos}, from_ver={self.from_version}, to_ver={self.to_version})'

    def apply(self, original_text):
        return "".join([original_text[:self.pos], self.text, original_text[self.pos:]])

    @staticmethod
    def merge(stack):
        """Tries to merge intersected instances of InsertAction"""
        mod_stack = []
        while len(stack) > 1:
            ins_1 = stack.pop(0)
            ins_2 = stack[0]
            if ins_1.pos <= ins_2.pos <= ins_1.pos + len(ins_1.text):
                text = ins_1.text[:ins_2.pos - ins_1.pos] + ins_2.text + ins_1.text[ins_2.pos - ins_1.pos:]
                pos = ins_1.pos
                from_version = ins_1.from_version
                to_version = ins_2.to_version
                stack[0] = InsertAction(pos=pos, text=text, from_version=from_version, to_version=to_version)
            else:
                mod_stack.append(ins_1)
        mod_stack.append(stack.pop())
        return mod_stack


class ReplaceAction(Action):
    def __init__(self, pos, text, from_version, to_version):
        super().__init__(pos, from_version, to_version)
        self.text = text

    def __repr__(self):
        return f'replace(text="{self.text}", pos={self.pos}, from_ver={self.from_version}, to_ver={self.to_version})'

    def apply(self, original_text):
        return "".join([original_text[:self.pos], self.text, original_text[self.pos + len(self.text):]])

    @staticmethod
    def merge(stack):
        """Tries to merge intersected instances of ReplaceAction"""
        mod_stack = []
        while len(stack) > 1:
            both_replaces = dict()
            ins_1 = stack.pop(0)
            ins_2 = stack[0]
            if not (ins_1.pos > ins_2.pos + len(ins_2.text) or ins_2.pos > ins_1.pos + len(ins_1.text)):
                replace = dict(zip(range(ins_1.pos, ins_1.pos + len(ins_1.text)), ins_1.text))
                both_replaces.update(replace)
                replace = dict(zip(range(ins_2.pos, ins_2.pos + len(ins_2.text)), ins_2.text))
                both_replaces.update(replace)
                both_replaces = {key: both_replaces[key] for key in sorted(both_replaces.keys())}
                text = ''.join(both_replaces.values())
                pos = list(both_replaces.keys())[0]
                from_version = ins_1.from_version
                to_version = ins_2.to_version
                stack[0] = ReplaceAction(pos=pos, text=text, from_version=from_version, to_version=to_version)
            else:
                mod_stack.append(ins_1)
        mod_stack.append(stack.pop())
        return mod_stack


class DeleteAction(Action):
    def __init__(self, pos, length, from_version, to_version):
        super().__init__(pos, from_version, to_version)
        self.length = length

    def __repr__(self):
        return f'delete(pos={self.pos}, len={self.length}, from_ver={self.from_version}, to_ver={self.to_version})'

    def apply(self, original_text):
        return "".join([original_text[:self.pos], original_text[self.pos + self.length:]])

    @staticmethod
    def merge(stack):
        """Tries to merge instances of DeleteAction"""
        mod_stack = []
        while len(stack) > 1:
            del_1 = stack.pop(0)
            del_2 = stack[0]
            if del_2.pos <= del_1.pos <= del_2.pos + del_2.length:
                pos = del_2.pos
                length = del_1.length + del_2.length
                from_version = del_1.from_version
                to_version = del_2.to_version
                del_action = DeleteAction(pos=pos, length=length, from_version=from_version, to_version=to_version)
                stack[0] = del_action
            else:
                mod_stack.append(del_1)
        mod_stack.append(stack.pop())
        return mod_stack

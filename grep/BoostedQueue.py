from queue import Queue

class BoostedQueue:
    def __init__(self, size_pre, size_post):
        self.pre_queue_ = Queue()
        self.current = None
        self.post_queue_ = Queue()
        self.len_pre_ = size_pre
        self.len_post_ = size_post

    def enqueue(self, element):
        self.post_queue_.put(element)

        if self.post_queue_.qsize() > self.len_post_:
            if not self.current == None:
                self.pre_queue_.put(self.current)
            self.current = self.post_queue_.get()

        if self.pre_queue_.qsize() > self.len_pre_:
            self.post_queue_.get()

    def get_all_elem(self):
        result = []
        if not self.pre_queue_.empty():
            for i in range(0, self.pre_queue_.qsize()):
                result.append(self.pre_queue_.queue[i])

        if not None == self.current:
            result.append(self.current)

        if not self.post.empty():
            for i in range(0, self.post_queue_.qsize()):
                result.append(self.post_queue_.queue[i])

        return result

    def look_all_el(self):
        for i in range(0, self.pre_queue_.qsize()):
            print(self.pre_queue_.queue[i], " ")
        if not None == self.current:
            print(self.current, " ")
        for i in range(self.post_queue_.qsize()):
            print(self.post_queue_.queue[i], " ")


class Module:
    def __init__(self, ie, model, model_type):
        self.ie = ie
        self.model_type = model_type
        self.model = ie.read_network(model, model.with_suffix('.bin'))
        self.model_path = model
        self.active_requests = 0
        self.clear()

    def deploy(self, device, plugin_config, max_requests=1):
        self.max_requests = max_requests
        self.exec_net = self.ie.load_network(self.model, device, config=plugin_config, num_requests=max_requests)

    def enqueue(self, input):
        self.clear()

        if self.max_requests <= self.active_requests:
            return False

        self.exec_net.start_async(self.active_requests, input)
        self.active_requests += 1
        return True

    def wait(self):
        if self.active_requests <= 0:
            return

        self.outputs = [None, ] * self.active_requests
        for i in range(self.active_requests):
            self.exec_net.requests[i].wait()
            self.outputs[i] = self.exec_net.requests[i].output_blobs

        self.active_requests = 0

    def get_outputs(self):
        self.wait()
        return self.outputs

    def clear(self):
        self.outputs = []

    def infer(self, inputs):
        self.clear()
        self.start_async(*inputs)
        return self.postprocess()

#Vesrion 1.0
import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


class Neuron:
    def __init__(self, weights, bias):
        self.weights = weights
        self.bias = bias

    def feedforward(self, inputs):
        return sigmoid(np.dot(self.weights, inputs) + self.bias)

class NeuralNet:
    def __init__(self, layers):
        self.input_layer = layers[0]
        self.output_layer = layers[len(layers) - 1]
        self.hidden = []
        for i in range(1, len(layers) - 2):
            self.hidden.append(layers[i])

    def get_output(self, inputs):
        if len(self.hidden) == 0:
            q1 = [0 for i in range(0, len(self.input_layer))]
            for i in range(0, len(inputs)):
                q1[i] = self.input_layer[i].feedforward([inputs[i]])
            q2 = [0 for i in range(0, len(self.output_layer))]
            for i in range(0, len(self.output_layer)):
                q2[i] = self.output_layer[i].feedforward(q1)
            return q2
        else:
            q1 = [0 for i in range(0, len(self.input_layer))]
            for i in range(0, len(inputs)):
                q1[i] = self.input_layer[i].feedforward([inputs[i]])
            for i in range(0, len(self.hidden)):
                q2 = [0 for i in range(0, len(self.hidden[i]))]
                for j in range(0, len(self.hidden[i])):
                    q2[i] = self.hidden[i][j].feedforward(q1)
                q1 = q2
            q2 = [0 for i in range(0, len(self.output_layer))]
            for i in range(0, len(self.output_layer)):
                q2[i] = self.output_layer[i].feedforward(q1)
            return q2

    def mutate_weights(self, limit):
        for i in range(0, len(self.input_layer)):
            self.input_layer[i].bias+=np.random.uniform(-limit * 2, limit * 2)
            for j in range(0, len(self.input_layer[i].weights)):
                self.input_layer[i].weights[j] += np.random.uniform(-limit, limit)
                self.input_layer[i].weights[j] = max(-1, min(1, self.input_layer[i].weights[j]))
        for i in range(0, len(self.output_layer)):
            self.output_layer[i].bias += np.random.uniform(-limit * 2, limit * 2)
            for j in range(0, len(self.output_layer[i].weights)):
                self.output_layer[i].weights[j] += np.random.uniform(-limit, limit)
                self.output_layer[i].weights[j] = max(-1, min(1, self.output_layer[i].weights[j]))
        for i in range(0, len(self.hidden)):
            for j in range(0, len(self.hidden[i])):
                self.hidden[i][j].bias += np.random.uniform(-limit * 2, limit * 2)
                for k in range(0, len(self.hidden[i][j].weights)):
                    self.hidden[i][j].weights[k] += np.random.uniform(-limit, limit)
                    self.hidden[i][j].weights[k] = max(-1, min(1, self.hidden[i][j].weights[k]))

    def copy(self):
        a = []
        a.append(len(self.input_layer))
        for i in self.hidden:
            a.append(len(i))
        a.append(len(self.output_layer))
        new_net = NeuralNet(generate_layers(a))
        for i in range(0, len(self.input_layer)):
            new_net.input_layer[i].bias = self.input_layer[i].bias
            for j in range(0, len(self.input_layer[i].weights)):
                new_net.input_layer[i].weights[j] = self.input_layer[i].weights[j]
        for i in range(0, len(self.output_layer)):
            new_net.output_layer[i].bias = self.output_layer[i].bias
            for j in range(0, len(self.output_layer[i].weights)):
                new_net.output_layer[i].weights[j] = self.output_layer[i].weights[j]
        for i in range(0, len(self.hidden)):
            for j in range(0, len(self.hidden[i])):
                new_net.hidden[i][j].bias = self.hidden[i][j].bias
                for k in range(0, len(self.hidden[i][j].weights)):
                    new_net.hidden[i][j].weights[k] = self.hidden[i][j].weights[k]
        return new_net


def generate_layers(a):
    input_layer = []
    for i in range(0, a[0]):
        input_layer.append(Neuron([np.random.uniform(-1, 1)], np.random.uniform(-10, 10)))
    layers = [input_layer]
    output_layer = []
    for i in range(0, a[len(a) - 1]):
        output_layer.append(Neuron([np.random.uniform(-1, 1) for i in range(0, a[len(a) - 2])], np.random.uniform(-10, 10)))
    if len(a) > 2:
        for i in range(1, len(a)):
            hidden = []
            for j in range(0, a[i]):
                hidden.append(Neuron([np.random.uniform(-1, 1) for i in range(0, a[i - 1])], np.random.uniform(-10, 10)))
            layers.append(hidden)
    layers.append(output_layer)
    return layers

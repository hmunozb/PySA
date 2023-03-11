"""
Copyright © 2023, United States Government, as represented by the Administrator
of the National Aeronautics and Space Administration. All rights reserved.

The PySA, a powerful tool for solving optimization problems is licensed under
the Apache License, Version 2.0 (the "License"); you may not use this file
except in compliance with the License. You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import torch
import numpy as np
from pysa.sa import Solver

td = torch.distributions


class RBM_PySA(torch.nn.Module):
    """
    A class for building a Restricted Boltzmann Machine (RBM) model via PySA.
    
    Parameters:
        visible_dim (int): The number of visible units in the RBM.
        hidden_dim (int): The number of hidden units in the RBM.
        state_size (int): The number of samples used to approximate the negative phase.
        steps (int): The number of Gibbs sampling steps to perform in the negative phase.
        device (str, Optional): The device to run the RBM on, either 'cpu' or 'cuda'. Defaults to 'cuda' if available, else 'cpu'.
        **kwargs (dict, Optional): An optional keyword arguments for PySA settings.
    
    Attributes:
        W (torch.nn.Parameter): A matrix representing the weights between visible and hidden units.
        v_bias (torch.nn.Parameter): A vector representing the biases for the visible units.
        h_bias (torch.nn.Parameter): A vector representing the biases for the hidden units.
        v_state (torch.autograd.Variable): A matrix representing the visible state of the RBM.
        h_state (torch.autograd.Variable): A matrix representing the hidden state of the RBM.
    """

    def __init__(self,
                 visible_dim,
                 hidden_dim,
                 state_size=100,
                 steps=1,
                 device=None,
                 **kwargs):
        super(RBM_PySA, self).__init__()
        self.visible_dim = visible_dim
        self.hidden_dim = hidden_dim
        self.state_size = state_size
        self.steps = steps

        # Initialize PySA parameters for RBM negative phase sampling
        self.min_temp = kwargs['min_temp'] if 'min_temp' in kwargs else 1.0
        self.max_temp = kwargs['max_temp'] if 'max_temp' in kwargs else 3.5
        self.parallel = kwargs['parallel'] if 'parallel' in kwargs else True
        self.float_type = 'float32'

        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        self.W = torch.nn.Parameter(
            torch.randn(self.visible_dim, self.hidden_dim, device=self.device))
        self.v_bias = torch.nn.Parameter(
            torch.zeros(self.visible_dim, 1, device=self.device))
        self.h_bias = torch.nn.Parameter(
            torch.zeros(self.hidden_dim, 1, device=self.device))

        self.v_state = torch.autograd.Variable(torch.zeros(self.state_size,
                                                           self.visible_dim,
                                                           device=self.device),
                                               requires_grad=False)
        self.h_state = torch.autograd.Variable(torch.zeros(self.state_size,
                                                           self.hidden_dim,
                                                           device=self.device),
                                               requires_grad=False)

    def v2h(self, v):
        """
        Returns the hidden units of the RBM given the visible units.
        
        Parameters:
            v (torch.Tensor): A tensor of shape (batch_size, visible_dim).
        
        Returns:
            torch.Tensor: A tensor of shape (batch_size, hidden_dim).
        """
        hidden_logits = torch.nn.functional.linear(v, self.W.t(),
                                                   self.h_bias.t())
        return td.Bernoulli(logits=hidden_logits).sample()

    def h2v(self, h):
        """
        Returns the visible units of the RBM given the hidden units.
        
        Parameters:
            h (torch.Tensor): A tensor of shape (batch_size, hidden_dim).
        
        Returns:
            torch.Tensor: A tensor of shape (batch_size, visible_dim).
        """

        visible_logits = torch.nn.functional.linear(h, self.W, self.v_bias.t())
        return td.Bernoulli(logits=visible_logits).sample()

    def update_states_with_pysa(self):
        """Updates the state of the RBM by performing multiple steps of Parallel tempering sampling."""
        self.problem = torch.zeros(self.visible_dim + self.hidden_dim,
                                   self.visible_dim + self.hidden_dim)
        # Augment Problem
        self.problem[:self.visible_dim, self.visible_dim:] = self.W
        self.problem[self.visible_dim:, :self.visible_dim] = self.W.t()
        self.problem += torch.diag(
            torch.cat([self.v_bias, self.h_bias], dim=0).squeeze()).cpu()

        solver = Solver(problem=-self.problem.detach().numpy(),
                        problem_type='qubo',
                        float_type='float32')

        results = solver.metropolis_update(num_sweeps=self.steps,
                                           num_reads=1,
                                           num_replicas=self.state_size,
                                           update_strategy='sequential',
                                           min_temp=self.min_temp,
                                           max_temp=self.max_temp,
                                           initialize_strategy=torch.cat(
                                               [self.v_state, self.h_state],
                                               dim=1).cpu().detach().numpy(),
                                           parallel=self.parallel,
                                           verbose=False)

        states = torch.tensor(results['states'].values[0]).to(self.device)
        self.v_state, self.h_state = torch.split(states,
                                                 self.visible_dim,
                                                 dim=1)

    def _energy(self, v, h):
        """
        Calculates the energy of a binary RBM given binary input `v` and hidden layer `h`.

        Parameters:
            v (torch.tensor): The tensor representing the visible units.
            h (torch.tensor): The tensor representing the hidden units.

        Returns:
            torch.tensor: The energy configuration of a binary RBM given binary input `v` and hidden layer `h`.
        """
        return -(torch.matmul(v, self.v_bias) + torch.matmul(h, self.h_bias) +
                 torch.sum(torch.matmul(v, self.W) * h, dim=1, keepdim=True))

    def energy(self, v):
        """
        Calculates the energy of a binary RBM given binary input `v`. This function find the hidden config `h` and then uses `_energy` 
        to calculate energy.
        
        Parameters:
            v (torch.tensor): The tensor representing the visible units.
        
        Returns:
            torch.tensor: The energy configuration of a binary RBM given binary input `v` and hidden layer `h`.
        """

        h = self.v2h(v)
        return self._energy(v, h)

    def log_prob(self, v):
        """
        Computes the log-probability of the joint probability of visible and hidden units.

        Parameters:
            v (torch.tensor): The tensor representing the visible units.

        Returns:
            torch.tensor: The log-probability of the joint probability of visible and hidden units.
        """
        positive_phase = self.positive_phase(v)
        negative_phase = self.negative_phase()
        logpz = -(positive_phase - negative_phase)
        return logpz

    def positive_phase(self, v):
        """
        Computes the positive phase of the contrastive divergence.

        Parameters:
            v (torch.tensor): The tensor representing the visible units.

        Returns:
            torch.tensor: The mean positive phase of the contrastive divergence.
        """
        positive_phase = self.energy(v)
        return torch.mean(positive_phase, dim=-1)

    def negative_phase(self):
        """
        Calculate the negative phase of the RBM

        Returns:
            The mean of the energy calculated from the generated sample by the RBM
        """
        negative_phase = self._energy(self.v_state, self.h_state)
        return torch.mean(negative_phase)

    def forward(self, x):
        """
        Given an input tensor `x`, the forward method computes and returns the reconstruction of the input tensor `x` by computing
        the hidden activations and then passing the hidden activations to the reconstruction of visible units.

        Parameters:
            x (torch.Tensor): input tensor of shape (batch_size, visible_dim)

        Returns:
            reconstructed_x (torch.Tensor): The reconstructed version of `x` with the same shape as `x`
        """
        return self.h2v(self.v2h(x))

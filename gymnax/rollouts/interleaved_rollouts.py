import jax
import jax.numpy as jnp
from jax import lax, jit, vmap
from functools import partial
from gymnax.rollouts.base_rollouts import BaseRollouts


class InterleavedRollouts(BaseRollouts):
    """ Interleaved rollouts of acting-learning as in DQN-style algorithms. """
    def __init__(self, agent,
                 buffer, push_to_buffer, sample_from_buffer,
                 step, reset, env_params):
        BaseRollouts.__init__(self, step, reset, env_params)
        self.agent = agent
        self.buffer = buffer
        self.push_to_buffer = push_to_buffer
        self.sample_from_buffer = sample_from_buffer

    def action_selection(self, key, obs, agent_params, actor_state):
        """ Compute action to be executed in environment. """
        action = self.agent.actor_step(agent_params, obs)
        return action, None

    def prepare_experience(self, env_output, actor_state):
        """ Prepare generated data (net/env) to be stored in buffer. """
        step_experience = {"state": env_output[0],
                           "next_state": env_output[1],
                           "obs": env_output[2],
                           "next_obs": env_output[3],
                           "action": env_output[4],
                           "reward": env_output[5],
                           "done": env_output[6]}
        return step_experience

    def store_experience(self, step_experience):
        """ Store the transition data (net + env) in a buffer. """
        self.buffer = self.push_to_buffer(self.buffer, step_experience)

    def update_learner(self, agent_params, learner_state):
        """ Perform an update to the parameters of the learner. """
        return agent_params, None

    def init_learner_state(self, agent_params):
        """ Initialize the state of the learner (e.g. optimizer). """
        return None

    def init_actor_state(self):
        """ Initialize the state of the actor (e.g. for exploration). """
        return None

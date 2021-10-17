from collections import defaultdict
from tqdm import tqdm as _tqdm
import numpy as np

def tqdm(*args, **kwargs):
    return _tqdm(*args, **kwargs, mininterval=1)  # Safety, do not overflow buffer

class DoubleQLearning(object):

    def __init__(self):
        pass

    class EpsilonGreedyPolicy(object):
        """
        A simple epsilon greedy policy.
        """
        def __init__(self, Q_a : dict, Q_b: dict, epsilon):
            self.Q_a = Q_a
            self.Q_b = Q_b
            self.epsilon = epsilon

        def sample_action(self, obs):
            """
            This method takes a state as input and returns an action sampled from this policy.  

            Args:
                obs: current state

            Returns:
                An action (int).
            """
            action_values = self.Q_a[obs] + self.Q_b[obs]

            if (np.random.uniform(0, 1) <= self.epsilon):
                action = np.random.randint(0, len(action_values))
            else:
                action = np.argmax(action_values)
                            
            return action


    def double_q_learning(env, policy, num_episodes, Q_a=None, Q_b=None, discount_factor=1.0, alpha=0.5, show_episodes=True):
        """
        Q-Learning algorithm: Off-policy TD control. Finds the optimal greedy policy
        while following an epsilon-greedy policy
        
        Args:
            env: OpenAI environment.
            policy: A behavior policy which allows us to sample actions with its sample_action method.
            Q: Q value function
            num_episodes: Number of episodes to run for.
            discount_factor: Gamma discount factor.
            alpha: TD learning rate.
            
        Returns:
            A tuple (Q, stats).
            Q is a numpy array Q[s,a] -> state-action value.
            stats is a list of tuples giving the episode lengths and returns.
        """
        
        # Keeps track of useful statistics
        stats = []
        try:
            num_actions = env.action_space.n
        except AttributeError:
            num_actions = env.nA
            
        if Q_a is None:
            Q_a = policy.Q_a
        else:
            policy.Q_a = Q_a
        
        if Q_b is None:
            Q_b = policy.Q_b
        else:
            policy.Q_b = Q_b

        episode_range = tqdm(range(num_episodes)) if show_episodes else range(num_episodes)

        for i_episode in episode_range:
            i = 0
            R = 0
            
            state = env.reset()
            Q_a[state] = np.zeros(num_actions)
            Q_b[state] = np.zeros(num_actions)
            
            while True:
                
                action = policy.sample_action(state)
                transition = env.step(action)
                next_state, reward, done, _ = transition

                if np.random.randint(0, 2):
                    max_action = np.argmax(Q_a.setdefault(next_state, np.zeros(num_actions)))
                    Q_a[state][action] = Q_a[state][action] + alpha * (reward + discount_factor * \
                        Q_b.setdefault(next_state, np.zeros(num_actions))[max_action] - Q_a[state][action])
                else:
                    max_action = np.argmax(Q_b.setdefault(next_state, np.zeros(num_actions)))
                    Q_b[state][action] = Q_b[state][action] + alpha * (reward + discount_factor * \
                        Q_a.setdefault(next_state, np.zeros(num_actions))[max_action] - Q_b[state][action])
                
                state = next_state
                
                R += reward
                i += 1
                
                if done:
                    break
            
            stats.append((i, R))
        episode_lengths, episode_returns = zip(*stats)

        Q = {}
        for key in Q_a.keys():
            Q[key] = Q_a[key] + Q_b[key]
        return Q, (episode_lengths, episode_returns)
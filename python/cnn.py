"""Extrator de features para a observacao com visao.

A CNN padrao do SB3 (NatureCNN) foi feita para telas do Atari, 84x84, e usa
convolucao 8x8 com passo 4 - numa grade 36x28 isso destroi a resolucao logo na
primeira camada. Aqui a rede e' pequena e mantem detalhe espacial: kernels 3x3
e um unico pooling.
"""
import gymnasium as gym
import torch
import torch.nn as nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor


class VisaoMesaExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space: gym.spaces.Dict, dim_saida: int = 256):
        super().__init__(observation_space, features_dim=dim_saida)
        n_canais = observation_space["grade"].shape[0]
        n_vetor = observation_space["vetor"].shape[0]

        self.cnn = nn.Sequential(
            nn.Conv2d(n_canais, 32, kernel_size=3, stride=1, padding=1), nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1), nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=2, padding=1), nn.ReLU(),
            nn.Flatten(),
        )
        with torch.no_grad():
            amostra = torch.as_tensor(observation_space["grade"].sample()[None]).float()
            n_flat = self.cnn(amostra).shape[1]

        self.cabeca_grade = nn.Sequential(nn.Linear(n_flat, 192), nn.ReLU())
        self.cabeca_vetor = nn.Sequential(nn.Linear(n_vetor, 64), nn.ReLU())
        self.juncao = nn.Sequential(nn.Linear(192 + 64, dim_saida), nn.ReLU())

    def forward(self, obs) -> torch.Tensor:
        g = self.cabeca_grade(self.cnn(obs["grade"]))
        v = self.cabeca_vetor(obs["vetor"])
        return self.juncao(torch.cat([g, v], dim=1))

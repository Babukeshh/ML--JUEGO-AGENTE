import math
import random
import pickle
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from config import ARCHIVO_CEREBRO

class AgenteQLearning:
    def __init__(self, alpha=0.1, gamma=0.9, tau=5.0, tau_min=0.1, tau_decay=0.999):
        self.Q = {} 
        self.acciones = [0, 1, 2, 3]
        self.alpha = alpha
        self.gamma = gamma
        self.tau = tau
        self.tau_min = tau_min
        self.tau_decay = tau_decay

    def _get_q(self, estado, accion):
        if estado not in self.Q: self.Q[estado] = {a: 0.0 for a in self.acciones}
        return self.Q[estado][accion]

    def elegir_accion_softmax(self, estado):
        if estado not in self.Q: self.Q[estado] = {a: 0.0 for a in self.acciones}
        valores_q = [self.Q[estado][a] for a in self.acciones]
        max_q = max(valores_q)
        
        exps = [math.exp((q - max_q) / self.tau) for q in valores_q]
        sum_exp = sum(exps)
        probs = [p / sum_exp for p in exps]
        return random.choices(self.acciones, weights=probs, k=1)[0]

    def aprender(self, estado, accion, recompensa, sig_estado):
        q_act = self._get_q(estado, accion)
        if sig_estado not in self.Q: self.Q[sig_estado] = {a: 0.0 for a in self.acciones}
        max_q_sig = max(self.Q[sig_estado].values())
        self.Q[estado][accion] = q_act + self.alpha * (recompensa + self.gamma * max_q_sig - q_act)

    def reducir_tau(self):
        if self.tau > self.tau_min: self.tau *= self.tau_decay

    def guardar_agente(self):
        ARCHIVO_CEREBRO.parent.mkdir(parents=True, exist_ok=True)
        with open(ARCHIVO_CEREBRO, 'wb') as f: pickle.dump(self.Q, f)
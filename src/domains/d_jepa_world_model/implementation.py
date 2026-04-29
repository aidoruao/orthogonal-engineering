"""D_JEPA_WORLD_MODEL implementation — Joint-Embedding Predictive Architecture

Layer: 4 (Institutional - Machine Learning)
CardinalStrength: PREDICATIVE

Mathematical Standards:
- Cramér–Wold theorem (1936): matching all 1D marginals ⇔ matching joint distribution
- Epps–Pulley test (1983): univariate normality via empirical characteristic function
- Mean-squared error prediction in latent space
- Cross-Entropy Method (CEM) for latent MPC planning

Based on: LeWorldModel (LeWM), arXiv:2603.19312v2
Maes, Le Lidec, Scieur, LeCun, Balestriero — Mila / NYU / Samsung SAIL / Brown
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Tuple, List, Optional, Dict


# ---------------------------------------------------------------------------
# Latent representation types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LatentState:
    """A single latent state vector z_t in the embedding space.

    Falsifies if: any component is NaN or infinite (represented as non-Fraction).
    falsifies_if: any component is NaN or infinite (represented as non-Fraction).
    """
    components: Tuple[Fraction, ...]
    timestep: int
    trajectory_id: str

    def dimension(self) -> int:
        return len(self.components)

    def l2_norm_squared(self) -> Fraction:
        """‖z‖² = Σ z_i²."""
        return sum(c * c for c in self.components)

    def dot(self, other: LatentState) -> Fraction:
        """Inner product ⟨z₁, z₂⟩."""
        if self.dimension() != other.dimension():
            raise ValueError("Dimension mismatch")
        return sum(a * b for a, b in zip(self.components, other.components))


@dataclass(frozen=True)
class LatentTrajectory:
    """A sequence of latent states z_{1:T} with associated actions.

    Falsifies if: states is empty or actions length differs from states length minus one.
    falsifies_if: states is empty or actions length differs from states length minus one.
    """
    trajectory_id: str
    states: Tuple[LatentState, ...]
    actions: Tuple[Tuple[Fraction, ...], ...]

    def length(self) -> int:
        return len(self.states)

    def temporal_straightening(self) -> Fraction:
        """Average monotonic function of cosine similarity between consecutive velocity vectors.

        S_straight = (1 / (B(T-2))) Σ Σ ⟨v_t, v_{t+1}⟩ / (‖v_t‖² ‖v_{t+1}‖²)
        where v_t = z_{t+1} - z_t.

        Uses dot/(‖v‖² · ‖v'‖²), a monotonic function of cosine similarity,
        to keep the computation purely in Fractions without square roots.
        """
        if len(self.states) < 3:
            return Fraction(0)
        total = Fraction(0)
        count = 0
        for t in range(len(self.states) - 2):
            v_t = self._velocity(t)
            v_tp1 = self._velocity(t + 1)
            norm_sq_t = self._velocity_norm(v_t)
            norm_sq_tp1 = self._velocity_norm(v_tp1)
            if norm_sq_t == 0 or norm_sq_tp1 == 0:
                continue
            dot = sum(a * b for a, b in zip(v_t, v_tp1))
            # Monotonic proxy for cosine: dot / (‖v‖² · ‖v'‖²)
            total += Fraction(dot, norm_sq_t * norm_sq_tp1)
            count += 1
        if count == 0:
            return Fraction(0)
        return total / count

    def _velocity(self, t: int) -> Tuple[Fraction, ...]:
        z1 = self.states[t].components
        z2 = self.states[t + 1].components
        return tuple(b - a for a, b in zip(z1, z2))

    def _velocity_norm(self, v: Tuple[Fraction, ...]) -> Fraction:
        """Return squared norm ‖v‖² as Fraction."""
        # TODO: Expand _velocity_norm() - stub detected by Yeshua Agent
        return sum(vi * vi for vi in v)


# ---------------------------------------------------------------------------
# Encoder and Predictor
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EncoderConfig:
    """Configuration for the vision encoder (ViT-Tiny scale per LeWM)."""
    patch_size: int = 14
    hidden_dim: int = 192
    num_layers: int = 12
    num_heads: int = 3
    mlp_ratio: Fraction = Fraction(4)
    image_size: int = 224


@dataclass(frozen=True)
class PredictorConfig:
    """Configuration for the dynamics predictor (transformer per LeWM)."""
    hidden_dim: int = 192
    num_layers: int = 6
    num_heads: int = 16
    dropout: Fraction = Fraction(1, 10)
    action_dim: int = 4


@dataclass(frozen=True)
class WorldModelConfig:
    """Complete world model configuration."""
    encoder: EncoderConfig = field(default_factory=EncoderConfig)
    predictor: PredictorConfig = field(default_factory=PredictorConfig)
    embedding_dim: int = 192
    history_length: int = 1
    frame_skip: int = 5


@dataclass(frozen=True)
class EncoderOutput:
    """Output of the encoder: latent patch features + [CLS] token."""
    cls_embedding: LatentState
    patch_embeddings: Tuple[LatentState, ...]


@dataclass(frozen=True)
class PredictorOutput:
    """Output of the predictor: next latent state prediction."""
    predicted_next: LatentState
    target_next: Optional[LatentState] = None

    def prediction_error_squared(self) -> Fraction:
        """‖ẑ_{t+1} - z_{t+1}‖²."""
        if self.target_next is None:
            return Fraction(0)
        pred = self.predicted_next.components
        tgt = self.target_next.components
        return sum((p - t) * (p - t) for p, t in zip(pred, tgt))


# ---------------------------------------------------------------------------
# SIGReg — Sketched-Isotropic-Gaussian Regularizer
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SIGRegConfig:
    """Configuration for SIGReg regularization."""
    num_projections: int = 1024
    lambda_weight: Fraction = Fraction(1, 10)
    quadrature_start: Fraction = Fraction(1, 5)  # 0.2
    quadrature_end: Fraction = Fraction(4)
    quadrature_knots: int = 20


@dataclass(frozen=True)
class RandomProjection:
    """A single random unit-norm direction u^{(m)} ∈ S^{d-1}."""
    direction: Tuple[Fraction, ...]
    projection_id: int

    def norm_squared(self) -> Fraction:
        # TODO: Expand norm_squared() - stub detected by Yeshua Agent
        return sum(c * c for c in self.direction)


@dataclass(frozen=True)
class ProjectedEmbedding:
    """1D projection h^{(m)} = Z · u^{(m)} for a batch of embeddings."""
    values: Tuple[Fraction, ...]
    projection: RandomProjection


@dataclass(frozen=True)
class EppsPulleyResult:
    """Result of the Epps–Pulley normality test on a 1D projection."""
    test_statistic: Fraction
    projection_id: int
    sample_count: int


@dataclass(frozen=True)
class SIGRegResult:
    """Aggregated SIGReg regularization term over M projections."""
    aggregate_score: Fraction
    projection_results: Tuple[EppsPulleyResult, ...]
    num_projections: int

    def per_projection_mean(self) -> Fraction:
        if self.num_projections == 0:
            return Fraction(0)
        return self.aggregate_score / self.num_projections


# ---------------------------------------------------------------------------
# Planning
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CEMConfig:
    """Cross-Entropy Method configuration for latent MPC planning."""
    num_samples: int = 300
    num_iterations: int = 30
    num_elites: int = 30
    planning_horizon: int = 5
    action_dim: int = 4
    initial_mean: Fraction = Fraction(0)
    initial_std: Fraction = Fraction(1)


@dataclass(frozen=True)
class ActionSequence:
    """A candidate action sequence a_{1:H}."""
    actions: Tuple[Tuple[Fraction, ...], ...]
    sequence_id: str

    def horizon(self) -> int:
        # TODO: Expand horizon() - stub detected by Yeshua Agent
        return len(self.actions)


@dataclass(frozen=True)
class PlanningResult:
    """Result of latent-space MPC planning."""
    optimal_actions: Optional[ActionSequence]
    final_cost: Fraction
    converged: bool
    iterations_used: int
    goal_state: LatentState


@dataclass(frozen=True)
class SurpriseEvent:
    """A detected physically implausible event in latent space."""
    event_id: str
    trajectory_id: str
    timestep: int
    surprise_score: Fraction
    expected_state: LatentState
    observed_state: LatentState


# ---------------------------------------------------------------------------
# Training state
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TrainingStep:
    """A single training step with losses."""
    step_id: str
    prediction_loss: Fraction
    sigreg_loss: Fraction
    total_loss: Fraction
    lambda_weight: Fraction

    def is_collapsed(self, threshold: Fraction = Fraction(1, 1000)) -> bool:
        """Heuristic: prediction loss near zero with high SIGReg suggests collapse."""
        # TODO: Expand is_collapsed() - stub detected by Yeshua Agent
        return self.prediction_loss < threshold and self.sigreg_loss > Fraction(1)


@dataclass(frozen=True)
class TrainingRun:
    """Complete training run with loss trajectory."""
    run_id: str
    steps: Tuple[TrainingStep, ...]
    config: WorldModelConfig
    sigreg_config: SIGRegConfig

    def final_prediction_loss(self) -> Fraction:
        if not self.steps:
            return Fraction(0)
        return self.steps[-1].prediction_loss

    def final_sigreg_loss(self) -> Fraction:
        if not self.steps:
            return Fraction(0)
        return self.steps[-1].sigreg_loss


# ---------------------------------------------------------------------------
# Domain metadata
# ---------------------------------------------------------------------------

DOMAIN_METADATA = {
    "name": "d_jepa_world_model",
    "version": "1.0.0",
    "paper_id": "2603.19312v2",
    "paper_title": "LeWorldModel: Stable End-to-End Joint-Embedding Predictive Architecture from Pixels",
    "authors": ["Lucas Maes", "Quentin Le Lidec", "Damien Scieur", "Yann LeCun", "Randall Balestriero"],
    "institutions": ["Mila & Université de Montréal", "NYU", "Samsung SAIL", "Brown"],
    "theorems": ["Cramér–Wold (1936)", "Epps–Pulley (1983)"],
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}

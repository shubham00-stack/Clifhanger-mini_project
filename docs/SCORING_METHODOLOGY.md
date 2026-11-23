# Cliffhanger Scoring Methodology & Taxonomy

## 1. Mathematical Formulation
The backend executes deterministic arithmetic on model-calibrated ratings:

$$\text{Final Score} = \sum_{i=1}^9 w_i \times D_i$$

### 9 Scoring Dimensions & Weights ($w_i$)
| Dimension ($D_i$) | Weight ($w_i$) | Definition |
| :--- | :--- | :--- |
| `unresolved_question` | **0.20 (20%)** | Central narrative inquiry left hanging with high viewer curiosity. |
| `stakes` | **0.15 (15%)** | Severity of physical, psychological, existential, or relational loss. |
| `emotional_intensity` | **0.15 (15%)** | Peak arousal (dread, awe, shock, heartbreak) created at the cutoff. |
| `character_consequence` | **0.10 (10%)** | Impact on protagonist trajectory, status, moral standing, or bonds. |
| `surprise` | **0.10 (10%)** | Subversion of established audience expectation without feeling random. |
| `urgency` | **0.10 (10%)** | Time sensitivity (ticking clock, immediate peril, imminent choice). |
| `causal_setup` | **0.10 (10%)** | Logical continuity; the ending feels earned from prior narrative events. |
| `information_gap` | **0.05 (5%)** | Asymmetric knowledge between audience and characters. |
| `originality` | **0.05 (5%)** | Freshness of execution versus cliché or trope exhaustion. |

$$\sum_{i=1}^9 w_i = 0.20 + 0.15 + 0.15 + 0.10 + 0.10 + 0.10 + 0.10 + 0.05 + 0.05 = 1.00$$

---

## 2. Deterministic Score Bands
- **0–29: No Meaningful Cliffhanger** (Narrative closure or complete detachment)
- **30–49: Weak** (Low stakes, predictable resolution, or unearned abruptness)
- **50–64: Moderate** (Functional unresolved issue, but lacks acute tension)
- **65–79: Strong** (High urgency, evident stakes, compels next segment)
- **80–89: Very Strong** (Electrifying pivot, critical character peril/decision)
- **90–100: Exceptional** (Masterclass hook, monumental stakes, irreversible)

---

## 3. Multi-Label Taxonomy (12 Types)
1. `threat` (Direct physical or imminent danger)
2. `decision` (Irrevocable choice forced upon character)
3. `revelation` (Groundbreaking truth unveiled to audience/character)
4. `identity` (Shocking revelation of true identity or allegiance)
5. `relationship` (Romantic or interpersonal rupture/confession)
6. `mission` (Abrupt shift, failure, or escalation in core objective)
7. `moral` (Ethical dilemma testing core values)
8. `reversal` (Sudden inversion of power or circumstance)
9. `countdown` (Explicit temporal deadline)
10. `mystery` (Baffling phenomenon requiring explanation)
11. `parallel` (Cross-cutting cliffhangers across simultaneous storylines)
12. `existential` (Cosmic, metaphysical, or reality-altering disruption)

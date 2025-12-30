# 🧠 Neural_Wars — Competitive Game AI Agent

Neural_Wars is a time-aware adversarial game AI built for **Prometeo 2026: Neural Wars**.  
The agent is designed to play reliably under strict time constraints while maintaining strong tactical and positional decision-making.

---

## 🚀 Features

- Negamax search with Alpha–Beta pruning  
- Iterative Deepening for anytime move selection  
- Quiescence Search to avoid horizon effects  
- Dynamic per-move time management  
- Capture-based move ordering  
- Piece-Square Tables (PST) for positional evaluation  
- King safety, check pressure, and repetition awareness  

---

## 🧩 Search Architecture
get_best_move()
└── Iterative Deepening
└── Root Search
└── Negamax (Alpha–Beta)
└── Quiescence Search
└── Static Evaluation


Every recursive layer performs strict time checks to guarantee timeout safety.

---

## ⏱️ Time Management

- Total match time: **60 seconds**
- Time per move is dynamically allocated based on remaining turns
- Hard bounds:
  - Minimum: **0.05 seconds**
  - Maximum: **2.0 seconds**
- A safety buffer is deducted after each move to avoid time overruns

If the time limit is exceeded at any point, the search exits cleanly and returns the best move found so far.

---

## ♟️ Move Ordering

Moves are ordered to improve pruning efficiency:

- Capturing moves are prioritized using piece values
- High-value captures are searched first
- Light randomization among top moves avoids deterministic traps

This significantly improves Alpha–Beta performance in tactical positions.

---

## 🧠 Core Algorithms

### Negamax with Alpha–Beta Pruning
- Single-perspective minimax formulation
- Automatic score inversion per player
- Early cutoffs when bounds are exceeded

### Iterative Deepening
- Search depth increases progressively
- Ensures a valid move is always available
- Stops safely when time is exhausted

### Quiescence Search
- Activated at depth zero
- Extends search for:
  - Captures
  - Checking moves
- Prevents unstable evaluations in tactical positions

---

## 📊 Evaluation Function

The evaluation function combines multiple factors:

- **Material balance** using predefined piece values
- **Positional scoring** via Piece-Square Tables:
  - Pawns
  - Knights
  - Bishops
  - King (late-game table)
- **King safety** via adjacent enemy threats
- **Check penalty** when the side to move is in check
- **Repetition penalty** to discourage draw loops
- **Capture safety bonus** for high-value pieces

Scores are always returned from the perspective of the side to move.

---

## 🧪 Game State Handling

- Checkmate is evaluated as a decisive loss
- Stalemate is evaluated based on material advantage
- Repetitions are detected and penalized
- Illegal or empty move sets are handled safely

---

## ⚙️ Usage

The agent is plug-and-play within the tournament framework:

```python
from Neural_Wars import Neural_Wars

agent = Neural_Wars(board)
best_move = agent.get_best_move()

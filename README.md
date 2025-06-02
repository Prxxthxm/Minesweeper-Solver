# Minesweeper Solver

This repository contains intelligent solvers for Minesweeper grids of any size. These solvers use layered logic and probabilistic methods to solve grids with minimal risk.

## Solver_v1
A comprehensive Minesweeper solver that incorporates a **five-layered logical deduction engine** consisting of a **Monte Carlo simulation-based fallback** for uncertain scenarios.

- Accepts manual input for any rectangular grid  
- Applies deterministic constraint satisfaction  
- Falls back on probability-driven guesses only when necessary  

## Solver_v2
An enhanced and optimized version featuring:

- Improved brute-force constraint resolution with better pruning  
- Smarter guessing strategy based on calculated risk (minimized mine probability)    
- Automatically prioritizes safest cells when deduction stalls  


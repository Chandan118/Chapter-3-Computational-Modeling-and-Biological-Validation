# Computational Modeling and Biological Validation of Bio-Inspired Ant Foraging for Swarm Robotics

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19097072.svg)](https://doi.org/10.5281/zenodo.19097072)

## Overview

This repository contains the source code, experimental data, and simulation models for **Chapter 3** of the thesis titled:
> **"Bio-Inspired Ant Foraging and Communication Mechanisms Modeling and Application to Swarm Robotics"**

The project provides a robust framework for the computational modeling of ant foraging behaviors and their subsequent validation against biological observations. It features a unique integration between **NetLogo** (for high-level agent-based logic) and **Gazebo** (for 3D physics-based swarm robot visualization).

## Key Features

- **Decentralized Coordination**: Pheromone-based communication algorithms for swarm intelligence.
- **Hybrid Simulation**: Seamless integration between NetLogo agent-based modeling and Gazebo physics.
- **Analytical Tools**: Performance analysis scripts for evaluating swarm foraging efficiency.
- **CI/CD Integrated**: Automated validation of all simulation components via GitHub Actions.

## Setup and Installation

### Prerequisites
- Python 3.11+
- NetLogo 7.0.2+
- Java Runtime Environment
- (Optional) Gazebo 11 for 3D visualization

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Chandan118/Chapter-3-Computational-Modeling-and-Biological-Validation.git
   cd Chapter-3-Computational-Modeling-and-Biological-Validation
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running Experiments

To run the full suite of formicabot experiments:
```bash
python3 run_formicabot_experiments.py
```

For the complete production simulation with comprehensive analysis:
```bash
python3 complete_ant_simulation.py
```

## Citation

If you use this work in your research, please cite it as:

```bibtex
@software{sheikder_chandan_chapter3_2026,
  author       = {Sheikder, Chandan},
  title        = {Computational Modeling and Biological Validation of Bio-Inspired Ant Foraging for Swarm Robotics},
  month        = mar,
  year         = 2026,
  publisher    = {Zenodo},
  version      = {v1.0.0},
  doi          = {10.5281/zenodo.19097072},
  url          = {https://doi.org/10.5281/zenodo.19097072}
}
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.
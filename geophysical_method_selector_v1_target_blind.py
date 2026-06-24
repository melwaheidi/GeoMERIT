"""
Geophysical Method Selection Framework - 9 Methods (Scientifically Corrected)

This module implements a Weighted Sum Model (WSM) for geophysical method selection.

CORRECTED METHOD LIST (9 methods):
1. ERT (Electrical Resistivity Tomography) - includes DC resistivity
2. Induced Polarization
3. Self-Potential  
4. GPR (Ground Penetrating Radar)
5. TEM (Time-Domain Electromagnetics)
6. Seismic Refraction
7. Magnetometry - measures magnetic susceptibility
8. Gravity - includes microgravity variants
9. Radiometric

NOTE: DC Resistivity has been merged with ERT as they use the same physical principle
(Ohm's law) and measurement technique, differing only in electrode configuration.
"""

import numpy as np
from typing import Dict, List, Tuple

class GeophysicalMethodSelector:
    """
    Weighted Sum Model for geophysical method selection.
    """
    
    def __init__(self):
        """Initialize the selector with method parameters and weights."""
        
        # Define the 9 geophysical methods
        self.methods = {
            'ERT': {
                'depth_range': (1, 100),  # meters
                'resolution': 0.8,
                'cost_per_km': 3000,
                'time_per_km': 2.0,  # days
                'noise_sensitivity': 0.6,
                'conductivity_sensitivity': 0.9
            },
            'Induced_Polarization': {
                'depth_range': (1, 50),
                'resolution': 0.7,
                'cost_per_km': 4000,
                'time_per_km': 2.5,
                'noise_sensitivity': 0.7,
                'conductivity_sensitivity': 0.8
            },
            'Self_Potential': {
                'depth_range': (0.5, 30),
                'resolution': 0.6,
                'cost_per_km': 1500,
                'time_per_km': 1.0,
                'noise_sensitivity': 0.9,
                'conductivity_sensitivity': 0.5
            },
            'GPR': {
                'depth_range': (0.5, 15),
                'resolution': 0.95,
                'cost_per_km': 2500,
                'time_per_km': 1.5,
                'noise_sensitivity': 0.4,
                'conductivity_sensitivity': 0.95
            },
            'TEM': {
                'depth_range': (10, 300),
                'resolution': 0.6,
                'cost_per_km': 5000,
                'time_per_km': 3.0,
                'noise_sensitivity': 0.5,
                'conductivity_sensitivity': 0.9
            },
            'Seismic_Refraction': {
                'depth_range': (5, 100),
                'resolution': 0.7,
                'cost_per_km': 6000,
                'time_per_km': 4.0,
                'noise_sensitivity': 0.6,
                'conductivity_sensitivity': 0.2
            },
            'Magnetometry': {
                'depth_range': (0.5, 50),
                'resolution': 0.65,
                'cost_per_km': 2000,
                'time_per_km': 1.0,
                'noise_sensitivity': 0.5,
                'conductivity_sensitivity': 0.3
            },
            'Gravity': {
                'depth_range': (10, 500),
                'resolution': 0.5,
                'cost_per_km': 4500,
                'time_per_km': 3.5,
                'noise_sensitivity': 0.4,
                'conductivity_sensitivity': 0.1
            },
            'Radiometric': {
                'depth_range': (0, 0.5),
                'resolution': 0.8,
                'cost_per_km': 3500,
                'time_per_km': 1.5,
                'noise_sensitivity': 0.3,
                'conductivity_sensitivity': 0.0
            }
        }
        
        # Criteria weights (must sum to 1.0)
        self.weights = {
            'physical_contrast': 0.40,
            'data_quality': 0.30,
            'cost': 0.20,
            'effort': 0.10
        }
    
    def calculate_depth_factor(self, method: str, target_depth: float) -> float:
        """
        Calculate depth suitability factor.
        
        Returns:
            1.0 if within optimal range
            0.7 if target is deeper than max depth (above range)
            0.5 if target is shallower than min depth (below range)
        """
        min_depth, max_depth = self.methods[method]['depth_range']
        
        if min_depth <= target_depth <= max_depth:
            return 1.0
        elif target_depth > max_depth:
            return 0.7  # Target deeper than capability
        else:
            return 0.5  # Target shallower than optimal
    
    def calculate_noise_impact_factor(self, method: str, noise_level: float) -> float:
        """
        Calculate noise impact factor (CORRECTED FORMULA).
        
        Args:
            method: Method name
            noise_level: Site noise level (0-100%)
        
        Returns:
            Noise impact factor (0-1), where 1.0 = no impact
        """
        sensitivity = self.methods[method]['noise_sensitivity']
        noise_impact_factor = 1.0 - sensitivity * (noise_level / 100.0) ** 2
        return max(0.0, noise_impact_factor)
    
    def calculate_conductivity_factor(self, method: str, conductivity: float) -> float:
        """
        Calculate conductivity impact factor.
        
        Args:
            method: Method name
            conductivity: Site conductivity (mS/m)
        
        Returns:
            Conductivity factor (0-1)
        """
        sensitivity = self.methods[method]['conductivity_sensitivity']
        max_conductivity = 1000.0  # mS/m
        conductivity_factor = 1.0 - sensitivity * (conductivity / max_conductivity)
        return max(0.0, conductivity_factor)
    
    def rank_methods(self, site_params: Dict) -> List[Tuple[str, float]]:
        """
        Rank all methods for given site parameters.
        
        Args:
            site_params: Dictionary with keys:
                - target_depth (float): Target depth in meters
                - conductivity (float): Site conductivity in mS/m
                - noise_level (float): Noise level 0-100%
                - budget (float): Budget in USD
                - time_constraint (float): Time constraint in days
        
        Returns:
            List of (method_name, score) tuples, sorted by score descending
        """
        scores = {}
        
        for method in self.methods:
            # Calculate adjustment factors
            depth_factor = self.calculate_depth_factor(method, site_params['target_depth'])
            noise_factor = self.calculate_noise_impact_factor(method, site_params['noise_level'])
            cond_factor = self.calculate_conductivity_factor(method, site_params['conductivity'])
            
            # Calculate criterion scores (0-100 scale)
            physical_score = self.methods[method]['resolution'] * 100 * depth_factor * cond_factor
            quality_score = self.methods[method]['resolution'] * 100 * noise_factor
            
            # Normalize cost and time (inverse relationship)
            cost_score = max(0, 100 - (self.methods[method]['cost_per_km'] / site_params['budget']) * 100)
            time_score = max(0, 100 - (self.methods[method]['time_per_km'] / site_params['time_constraint']) * 100)
            
            # Calculate weighted sum
            total_score = (
                self.weights['physical_contrast'] * physical_score +
                self.weights['data_quality'] * quality_score +
                self.weights['cost'] * cost_score +
                self.weights['effort'] * time_score
            )
            
            scores[method] = total_score
        
        # Sort by score descending
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked

# Example usage
if __name__ == "__main__":
    selector = GeophysicalMethodSelector()
    
    # Example: Groundwater exploration
    site_params = {
        'target_depth': 50.0,  # meters
        'conductivity': 100.0,  # mS/m
        'noise_level': 30.0,  # %
        'budget': 5000.0,  # USD
        'time_constraint': 3.0  # days
    }
    
    rankings = selector.rank_methods(site_params)
    
    print("\\nGeophysical Method Rankings (9 Methods):")
    print("=" * 50)
    for rank, (method, score) in enumerate(rankings, 1):
        print(f"{rank}. {method:25s} Score: {score:6.2f}")

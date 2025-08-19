import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import json

class GridClassifier:
    def __init__(self, grid_size=0.01):  # 0.01 degrees ≈ 1.1 km
        """
        Initialize grid classifier
        
        Args:
            grid_size (float): Size of grid cells in degrees (latitude/longitude)
        """
        self.grid_size = grid_size
        self.grid_data = None
        self.risk_zones = None
        self.scaler = StandardScaler()
        
    def create_grid(self, crime_data):
        """
        Create grid from crime data and classify each grid cell
        
        Args:
            crime_data (pd.DataFrame): Crime data with Latitude, Longitude, Crime_Type, Severity
            
        Returns:
            dict: Grid classification results
        """
        print("Creating grid classification...")
        
        # Define grid boundaries
        min_lat = crime_data['Latitude'].min()
        max_lat = crime_data['Latitude'].max()
        min_lon = crime_data['Longitude'].min()
        max_lon = crime_data['Longitude'].max()
        
        # Create grid cells
        lat_bins = np.arange(min_lat, max_lat + self.grid_size, self.grid_size)
        lon_bins = np.arange(min_lon, max_lon + self.grid_size, self.grid_size)
        
        # Assign crimes to grid cells
        crime_data['grid_lat'] = pd.cut(crime_data['Latitude'], bins=lat_bins, labels=False)
        crime_data['grid_lon'] = pd.cut(crime_data['Longitude'], bins=lon_bins, labels=False)
        
        # Group crimes by grid cell
        grid_stats = crime_data.groupby(['grid_lat', 'grid_lon']).agg({
            'Crime_ID': 'count',  # Total crimes
            'Severity': ['mean', 'max'],  # Average and max severity
            'Crime_Type': lambda x: list(x),  # List of crime types
            'Latitude': 'mean',  # Center latitude of grid
            'Longitude': 'mean'  # Center longitude of grid
        }).reset_index()
        
        # Flatten column names
        grid_stats.columns = ['grid_lat', 'grid_lon', 'crime_count', 'avg_severity', 
                            'max_severity', 'crime_types', 'center_lat', 'center_lon']
        
        # Calculate risk score for each grid
        grid_stats['risk_score'] = self._calculate_risk_score(grid_stats)
        
        # Classify risk zones
        grid_stats['risk_zone'] = self._classify_risk_zones(grid_stats['risk_score'])
        
        self.grid_data = grid_stats
        return self._get_grid_summary()
    
    def _calculate_risk_score(self, grid_stats):
        """
        Calculate risk score for each grid cell
        
        Args:
            grid_stats (pd.DataFrame): Grid statistics
            
        Returns:
            np.array: Risk scores
        """
        # Normalize features
        features = grid_stats[['crime_count', 'avg_severity', 'max_severity']].values
        features_scaled = self.scaler.fit_transform(features)
        
        # Calculate risk score (weighted combination)
        weights = [0.4, 0.3, 0.3]  # crime_count, avg_severity, max_severity
        risk_scores = np.dot(features_scaled, weights)
        
        # Normalize to 0-1 range
        risk_scores = (risk_scores - risk_scores.min()) / (risk_scores.max() - risk_scores.min())
        
        return risk_scores
    
    def _classify_risk_zones(self, risk_scores):
        """
        Classify grid cells into risk zones
        
        Args:
            risk_scores (np.array): Risk scores
            
        Returns:
            np.array: Risk zone classifications
        """
        # Define risk thresholds
        thresholds = [0.2, 0.4, 0.6, 0.8]
        
        # Classify into zones
        zones = np.digitize(risk_scores, thresholds)
        zone_names = ['safe', 'low_risk', 'medium_risk', 'high_risk', 'critical']
        
        return [zone_names[zone] for zone in zones]
    
    def _get_grid_summary(self):
        """
        Get summary statistics of the grid
        
        Returns:
            dict: Grid summary
        """
        if self.grid_data is None:
            return {"error": "Grid not created yet"}
        
        summary = {
            'total_grids': len(self.grid_data),
            'risk_zone_distribution': self.grid_data['risk_zone'].value_counts().to_dict(),
            'avg_risk_score': self.grid_data['risk_score'].mean(),
            'max_risk_score': self.grid_data['risk_score'].max(),
            'grid_size_degrees': self.grid_size,
            'grid_size_km': self.grid_size * 111  # Approximate conversion
        }
        
        return summary
    
    def check_location(self, latitude, longitude):
        """
        Check if a location falls within any risk zone
        
        Args:
            latitude (float): Latitude of the location
            longitude (float): Longitude of the location
            
        Returns:
            dict: Risk information for the location
        """
        if self.grid_data is None:
            return {"error": "Grid not created yet"}
        
        # Find the grid cell for this location
        grid_lat = int((latitude - self.grid_data['center_lat'].min()) / self.grid_size)
        grid_lon = int((longitude - self.grid_data['center_lon'].min()) / self.grid_size)
        
        # Find matching grid
        matching_grid = self.grid_data[
            (self.grid_data['grid_lat'] == grid_lat) & 
            (self.grid_data['grid_lon'] == grid_lon)
        ]
        
        if len(matching_grid) == 0:
            return {
                "location": {"latitude": latitude, "longitude": longitude},
                "risk_zone": "unknown",
                "risk_score": 0.0,
                "crime_count": 0,
                "message": "Location not in mapped area"
            }
        
        grid_info = matching_grid.iloc[0]
        
        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "risk_zone": grid_info['risk_zone'],
            "risk_score": float(grid_info['risk_score']),
            "crime_count": int(grid_info['crime_count']),
            "avg_severity": float(grid_info['avg_severity']),
            "crime_types": grid_info['crime_types']
        }
    
    def get_nearby_risk_zones(self, latitude, longitude, radius_km=2.0):
        """
        Get risk zones within a specified radius
        
        Args:
            latitude (float): Center latitude
            longitude (float): Center longitude
            radius_km (float): Search radius in kilometers
            
        Returns:
            dict: Nearby risk zones information
        """
        if self.grid_data is None:
            return {"error": "Grid not created yet"}
        
        # Convert radius to degrees (approximate)
        radius_degrees = radius_km / 111.0
        
        # Find grids within radius
        distance = np.sqrt(
            (self.grid_data['center_lat'] - latitude)**2 + 
            (self.grid_data['center_lat'] - longitude)**2
        )
        
        nearby_grids = self.grid_data[distance <= radius_degrees].copy()
        
        if len(nearby_grids) == 0:
            return {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius_km": radius_km,
                "nearby_zones": [],
                "message": "No risk zones found in this area"
            }
        
        # Sort by distance
        nearby_grids['distance'] = distance[distance <= radius_degrees]
        nearby_grids = nearby_grids.sort_values('distance')
        
        # Format results
        nearby_zones = []
        for _, grid in nearby_grids.iterrows():
            nearby_zones.append({
                "latitude": float(grid['center_lat']),
                "longitude": float(grid['center_lon']),
                "risk_zone": grid['risk_zone'],
                "risk_score": float(grid['risk_score']),
                "crime_count": int(grid['crime_count']),
                "distance_km": float(grid['distance'] * 111.0)
            })
        
        return {
            "center": {"latitude": latitude, "longitude": longitude},
            "radius_km": radius_km,
            "nearby_zones": nearby_zones,
            "total_zones_found": len(nearby_zones)
        }
    
    def get_risk_zone_coordinates(self, risk_zone=None):
        """
        Get coordinates of all grids in a specific risk zone
        
        Args:
            risk_zone (str): Risk zone to filter (optional)
            
        Returns:
            dict: Coordinates and risk information
        """
        if self.grid_data is None:
            return {"error": "Grid not created yet"}
        
        if risk_zone:
            filtered_data = self.grid_data[self.grid_data['risk_zone'] == risk_zone]
        else:
            filtered_data = self.grid_data
        
        coordinates = []
        for _, grid in filtered_data.iterrows():
            coordinates.append({
                "latitude": float(grid['center_lat']),
                "longitude": float(grid['center_lon']),
                "risk_zone": grid['risk_zone'],
                "risk_score": float(grid['risk_score']),
                "crime_count": int(grid['crime_count'])
            })
        
        return {
            "risk_zone": risk_zone or "all",
            "total_locations": len(coordinates),
            "coordinates": coordinates
        }
    
    def export_grid_data(self, format='json'):
        """
        Export grid data in specified format
        
        Args:
            format (str): Export format ('json' or 'csv')
            
        Returns:
            str or bytes: Exported data
        """
        if self.grid_data is None:
            return {"error": "Grid not created yet"}
        
        if format.lower() == 'json':
            return self.grid_data.to_json(orient='records', indent=2)
        elif format.lower() == 'csv':
            return self.grid_data.to_csv(index=False)
        else:
            return {"error": "Unsupported format. Use 'json' or 'csv'"}
    
    def get_statistics(self):
        """
        Get comprehensive statistics about the grid
        
        Returns:
            dict: Statistical summary
        """
        if self.grid_data is None:
            return {"error": "Grid not created yet"}
        
        stats = {
            "grid_info": {
                "total_grids": len(self.grid_data),
                "grid_size_degrees": self.grid_size,
                "grid_size_km": self.grid_size * 111
            },
            "risk_distribution": self.grid_data['risk_zone'].value_counts().to_dict(),
            "crime_statistics": {
                "total_crimes": int(self.grid_data['crime_count'].sum()),
                "avg_crimes_per_grid": float(self.grid_data['crime_count'].mean()),
                "max_crimes_in_grid": int(self.grid_data['crime_count'].max())
            },
            "severity_statistics": {
                "avg_severity": float(self.grid_data['avg_severity'].mean()),
                "max_severity": float(self.grid_data['max_severity'].max())
            },
            "risk_score_statistics": {
                "min_risk_score": float(self.grid_data['risk_score'].min()),
                "max_risk_score": float(self.grid_data['risk_score'].max()),
                "avg_risk_score": float(self.grid_data['risk_score'].mean()),
                "std_risk_score": float(self.grid_data['risk_score'].std())
            }
        }
        
        return stats

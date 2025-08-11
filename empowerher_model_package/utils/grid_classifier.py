import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import folium
from folium import plugins
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
            list: Risk zone classifications
        """
        risk_zones = []
        for score in risk_scores:
            if score >= 0.7:
                risk_zones.append('high_risk')
            elif score >= 0.4:
                risk_zones.append('medium_risk')
            else:
                risk_zones.append('low_risk')
        
        return risk_zones
    
    def _get_grid_summary(self):
        """
        Get summary of grid classification
        
        Returns:
            dict: Grid classification summary
        """
        if self.grid_data is None:
            return None
        
        summary = {
            'total_grids': len(self.grid_data),
            'high_risk_grids': len(self.grid_data[self.grid_data['risk_zone'] == 'high_risk']),
            'medium_risk_grids': len(self.grid_data[self.grid_data['risk_zone'] == 'medium_risk']),
            'low_risk_grids': len(self.grid_data[self.grid_data['risk_zone'] == 'low_risk']),
            'grid_size_km': self.grid_size * 111,  # Approximate km
            'grids': self.grid_data.to_dict('records')
        }
        
        return summary
    
    def check_location_in_grid(self, latitude, longitude):
        """
        Check which risk zone a location falls into
        
        Args:
            latitude (float): Location latitude
            longitude (float): Location longitude
            
        Returns:
            dict: Risk zone information for the location
        """
        if self.grid_data is None:
            return {'error': 'Grid not initialized. Run create_grid() first.'}
        
        # Find the grid cell for the location
        grid_lat = int((latitude - self.grid_data['center_lat'].min()) / self.grid_size)
        grid_lon = int((longitude - self.grid_data['center_lon'].min()) / self.grid_size)
        
        # Find matching grid
        matching_grid = self.grid_data[
            (self.grid_data['grid_lat'] == grid_lat) & 
            (self.grid_data['grid_lon'] == grid_lon)
        ]
        
        if len(matching_grid) == 0:
            return {
                'location': {'latitude': latitude, 'longitude': longitude},
                'risk_zone': 'unknown',
                'risk_score': 0.0,
                'message': 'Location not in classified grid area'
            }
        
        grid_info = matching_grid.iloc[0]
        
        return {
            'location': {'latitude': latitude, 'longitude': longitude},
            'grid_center': {'latitude': grid_info['center_lat'], 'longitude': grid_info['center_lon']},
            'risk_zone': grid_info['risk_zone'],
            'risk_score': float(grid_info['risk_score']),
            'crime_count': int(grid_info['crime_count']),
            'avg_severity': float(grid_info['avg_severity']),
            'max_severity': int(grid_info['max_severity']),
            'crime_types': grid_info['crime_types']
        }
    
    def create_risk_map(self, output_file='risk_zones_map.html'):
        """
        Create an interactive map showing risk zones
        
        Args:
            output_file (str): Output HTML file path
            
        Returns:
            str: Path to generated map file
        """
        if self.grid_data is None:
            return None
        
        # Calculate map center
        center_lat = self.grid_data['center_lat'].mean()
        center_lon = self.grid_data['center_lon'].mean()
        
        # Create map
        risk_map = folium.Map(location=[center_lat, center_lon], zoom_start=12)
        
        # Color mapping for risk zones
        colors = {
            'high_risk': 'red',
            'medium_risk': 'orange', 
            'low_risk': 'green'
        }
        
        # Add grid cells to map
        for _, grid in self.grid_data.iterrows():
            # Create rectangle for grid cell
            bounds = [
                [grid['center_lat'] - self.grid_size/2, grid['center_lon'] - self.grid_size/2],
                [grid['center_lat'] + self.grid_size/2, grid['center_lon'] + self.grid_size/2]
            ]
            
            folium.Rectangle(
                bounds=bounds,
                color=colors[grid['risk_zone']],
                fill=True,
                fillOpacity=0.6,
                popup=f"""
                <b>Risk Zone:</b> {grid['risk_zone'].replace('_', ' ').title()}<br>
                <b>Risk Score:</b> {grid['risk_score']:.3f}<br>
                <b>Crime Count:</b> {grid['crime_count']}<br>
                <b>Avg Severity:</b> {grid['avg_severity']:.2f}<br>
                <b>Max Severity:</b> {grid['max_severity']}
                """
            ).add_to(risk_map)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>Risk Zones</b></p>
        <p><i class="fa fa-square" style="color:red"></i> High Risk</p>
        <p><i class="fa fa-square" style="color:orange"></i> Medium Risk</p>
        <p><i class="fa fa-square" style="color:green"></i> Low Risk</p>
        </div>
        '''
        risk_map.get_root().html.add_child(folium.Element(legend_html))
        
        # Save map
        risk_map.save(output_file)
        return output_file
    
    def get_nearby_risk_zones(self, latitude, longitude, radius_km=2):
        """
        Get risk zones within a certain radius of a location
        
        Args:
            latitude (float): Center latitude
            longitude (float): Center longitude
            radius_km (float): Search radius in kilometers
            
        Returns:
            dict: Nearby risk zones information
        """
        if self.grid_data is None:
            return {'error': 'Grid not initialized'}
        
        # Convert radius to degrees (approximate)
        radius_deg = radius_km / 111
        
        # Find grids within radius
        nearby_grids = self.grid_data[
            ((self.grid_data['center_lat'] - latitude) ** 2 + 
             (self.grid_data['center_lon'] - longitude) ** 2) ** 0.5 <= radius_deg
        ]
        
        if len(nearby_grids) == 0:
            return {
                'location': {'latitude': latitude, 'longitude': longitude},
                'radius_km': radius_km,
                'nearby_zones': [],
                'message': 'No risk zones found within radius'
            }
        
        # Calculate average risk in the area
        avg_risk_score = nearby_grids['risk_score'].mean()
        
        # Count risk zones by type
        risk_counts = nearby_grids['risk_zone'].value_counts().to_dict()
        
        return {
            'location': {'latitude': latitude, 'longitude': longitude},
            'radius_km': radius_km,
            'avg_risk_score': float(avg_risk_score),
            'risk_zone_counts': risk_counts,
            'nearby_zones': nearby_grids.to_dict('records')
        }

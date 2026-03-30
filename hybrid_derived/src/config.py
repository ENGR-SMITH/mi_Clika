"""
Configuration Module - Handles CSV-based data storage for Single Target Mode
No external services, Firebase, or analytics
"""

import csv
import os
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List


@dataclass
class ClickTarget:
    """Represents a single click target configuration"""
    id: int
    name: str
    x_pos: int
    y_pos: int
    click_interval: int  # milliseconds
    stop_condition: int  # 0=indefinite, 1=time, 2=cycles
    stop_value: int  # time in seconds or number of cycles
    anti_detection: bool = False
    is_active: bool = True


@dataclass
class ClickSettings:
    """Single Target Mode settings"""
    click_interval: int = 500  # milliseconds
    stop_condition: int = 0  # 0=indefinite, 1=by time, 2=by cycles
    stop_value: int = 0  # duration in seconds or cycles
    anti_detection: bool = False
    anti_detection_max_offset: int = 5  # pixels


class ConfigManager:
    """
    Manages all configuration storage using CSV files
    No Firebase, no external services - pure local storage
    """
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Default to data folder in project root
            self.data_dir = Path(__file__).parent.parent / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self.data_dir.mkdir(exist_ok=True)
        
        self.targets_file = self.data_dir / "targets.csv"
        self.settings_file = self.data_dir / "settings.json"
        
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Create CSV files if they don't exist"""
        # Create targets.csv if missing
        if not self.targets_file.exists():
            with open(self.targets_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'id', 'name', 'x_pos', 'y_pos', 'click_interval',
                    'stop_condition', 'stop_value', 'anti_detection', 'is_active'
                ])
                writer.writeheader()
        
        # Create settings.json if missing
        if not self.settings_file.exists():
            default_settings = asdict(ClickSettings())
            with open(self.settings_file, 'w') as f:
                json.dump(default_settings, f, indent=2)
    
    def save_target(self, target: ClickTarget) -> bool:
        """Save or update a click target configuration"""
        try:
            targets = self.load_all_targets()
            
            # Check if target already exists
            existing = [t for t in targets if t.id == target.id]
            if existing:
                targets = [t for t in targets if t.id != target.id]
            
            targets.append(target)
            
            # Sort by ID
            targets.sort(key=lambda t: t.id)
            
            # Write to CSV
            with open(self.targets_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'id', 'name', 'x_pos', 'y_pos', 'click_interval',
                    'stop_condition', 'stop_value', 'anti_detection', 'is_active'
                ])
                writer.writeheader()
                for t in targets:
                    writer.writerow(asdict(t))
            
            return True
        except Exception as e:
            print(f"Error saving target: {e}")
            return False
    
    def load_all_targets(self) -> List[ClickTarget]:
        """Load all click targets from CSV"""
        try:
            targets = []
            with open(self.targets_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row:
                        target = ClickTarget(
                            id=int(row['id']),
                            name=row['name'],
                            x_pos=int(row['x_pos']),
                            y_pos=int(row['y_pos']),
                            click_interval=int(row['click_interval']),
                            stop_condition=int(row['stop_condition']),
                            stop_value=int(row['stop_value']),
                            anti_detection=row['anti_detection'].lower() == 'true',
                            is_active=row['is_active'].lower() == 'true'
                        )
                        targets.append(target)
            return targets
        except Exception as e:
            print(f"Error loading targets: {e}")
            return []
    
    def get_target_by_id(self, target_id: int) -> Optional[ClickTarget]:
        """Get specific target by ID"""
        targets = self.load_all_targets()
        for target in targets:
            if target.id == target_id:
                return target
        return None
    
    def delete_target(self, target_id: int) -> bool:
        """Delete a target by ID"""
        try:
            targets = self.load_all_targets()
            targets = [t for t in targets if t.id != target_id]
            
            with open(self.targets_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'id', 'name', 'x_pos', 'y_pos', 'click_interval',
                    'stop_condition', 'stop_value', 'anti_detection', 'is_active'
                ])
                writer.writeheader()
                for t in targets:
                    writer.writerow(asdict(t))
            
            return True
        except Exception as e:
            print(f"Error deleting target: {e}")
            return False
    
    def get_next_target_id(self) -> int:
        """Get the next available target ID"""
        targets = self.load_all_targets()
        if not targets:
            return 1
        return max(t.id for t in targets) + 1
    
    def save_settings(self, settings: ClickSettings) -> bool:
        """Save application settings to JSON"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(asdict(settings), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def load_settings(self) -> ClickSettings:
        """Load application settings from JSON"""
        try:
            with open(self.settings_file, 'r') as f:
                data = json.load(f)
                return ClickSettings(
                    click_interval=data.get('click_interval', 500),
                    stop_condition=data.get('stop_condition', 0),
                    stop_value=data.get('stop_value', 0),
                    anti_detection=data.get('anti_detection', False),
                    anti_detection_max_offset=data.get('anti_detection_max_offset', 5)
                )
        except Exception as e:
            print(f"Error loading settings: {e}")
            return ClickSettings()
    
    def export_target_to_csv(self, target_id: int, output_file: str) -> bool:
        """Export a specific target to a standalone CSV file"""
        try:
            target = self.get_target_by_id(target_id)
            if not target:
                return False
            
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'id', 'name', 'x_pos', 'y_pos', 'click_interval',
                    'stop_condition', 'stop_value', 'anti_detection', 'is_active'
                ])
                writer.writeheader()
                writer.writerow(asdict(target))
            
            return True
        except Exception as e:
            print(f"Error exporting target: {e}")
            return False
    
    def import_target_from_csv(self, input_file: str) -> bool:
        """Import a target from a CSV file"""
        try:
            with open(input_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row:
                        # Generate new ID to avoid conflicts
                        new_id = self.get_next_target_id()
                        
                        target = ClickTarget(
                            id=new_id,
                            name=row['name'] + f" (Imported {new_id})",
                            x_pos=int(row['x_pos']),
                            y_pos=int(row['y_pos']),
                            click_interval=int(row['click_interval']),
                            stop_condition=int(row['stop_condition']),
                            stop_value=int(row['stop_value']),
                            anti_detection=row['anti_detection'].lower() == 'true',
                            is_active=row['is_active'].lower() == 'true'
                        )
                        self.save_target(target)
            
            return True
        except Exception as e:
            print(f"Error importing target: {e}")
            return False
    
    def get_data_dir(self) -> str:
        """Get the data directory path"""
        return str(self.data_dir)
    
    def get_targets_file_path(self) -> str:
        """Get the targets CSV file path"""
        return str(self.targets_file)


# Global config manager instance
_config_manager = None


def get_config_manager(data_dir: str = None) -> ConfigManager:
    """Get or create the global config manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(data_dir)
    return _config_manager

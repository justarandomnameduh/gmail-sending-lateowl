#!/usr/bin/env python3
"""
Script to create a sample participants Excel file.
Run this to create the participants.xlsx file with sample data.
"""

import pandas as pd

def create_sample_excel():
    """Create a sample participants Excel file."""
    # Sample data for participants
    data = {
        'email': [
            'participant1@example.com',
            'participant2@example.com', 
            'participant3@example.com',
            'inactive@example.com'
        ],
        'name': [
            'John Doe',
            'Jane Smith',
            'Bob Johnson', 
            'Inactive User'
        ],
        'active': [1, 1, 1, 0]
    }
    
    df = pd.DataFrame(data)
    df.to_excel('participants.xlsx', index=False)
    print("✓ Sample participants.xlsx file created successfully!")
    print("Please replace this with your actual participant data.")

if __name__ == "__main__":
    create_sample_excel() 
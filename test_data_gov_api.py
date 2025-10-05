#!/usr/bin/env python3
"""
Test script for data.gov.in API integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.data_gov_api_service import DataGovAPIService

def test_data_gov_apis():
    """Test the data.gov.in API service"""
    print("🧪 Testing data.gov.in API integration...")
    
    # Initialize service
    api_service = DataGovAPIService()
    
    # Test physical progress data
    print("\n📈 Testing Physical Progress API...")
    try:
        physical_data = api_service.fetch_physical_progress_data()
        if not physical_data.empty:
            print(f"✅ Physical Progress Data: {len(physical_data)} records")
            print(f"Columns: {list(physical_data.columns)}")
            print(f"Sample data:\n{physical_data.head(3)}")
        else:
            print("⚠️ No physical progress data received")
    except Exception as e:
        print(f"❌ Error fetching physical progress data: {e}")
    
    # Test renewable potential data
    print("\n🌱 Testing Renewable Potential API...")
    try:
        renewable_data = api_service.fetch_renewable_potential_data()
        if not renewable_data.empty:
            print(f"✅ Renewable Potential Data: {len(renewable_data)} records")
            print(f"Columns: {list(renewable_data.columns)}")
            print(f"Sample data:\n{renewable_data.head(3)}")
        else:
            print("⚠️ No renewable potential data received")
    except Exception as e:
        print(f"❌ Error fetching renewable potential data: {e}")
    
    print("\n🎉 API testing completed!")

if __name__ == "__main__":
    test_data_gov_apis()

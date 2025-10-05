#!/usr/bin/env python3
"""
Test script for the Smart EMS system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_data_loading():
    """Test data loading functionality"""
    print("=== Testing Data Loading ===")
    try:
        from utils.data_loader import DataLoader
        data_loader = DataLoader('..')
        
        # Test CSV data loading
        print("Loading CSV data...")
        combined_data = data_loader.prepare_training_data()
        print(f"✅ CSV data loaded: {combined_data.shape[0]} rows, {combined_data.shape[1]} columns")
        
        if not combined_data.empty:
            print(f"Sample data columns: {list(combined_data.columns)[:5]}")
            print(f"Date range: {combined_data['DATE_TIME'].min()} to {combined_data['DATE_TIME'].max()}")
        
        return True
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return False

def test_prediction_service():
    """Test prediction service functionality"""
    print("\n=== Testing Prediction Service ===")
    try:
        from services.simple_prediction_service import SimplePredictionService
        service = SimplePredictionService('..')
        
        # Test current recommendations
        print("Getting current recommendations...")
        recommendations = service.get_current_recommendations()
        print(f"✅ Recommendations: {recommendations}")
        
        # Test system status
        print("Getting system status...")
        status = service.get_system_status()
        print(f"✅ System status: {status}")
        
        return True
    except Exception as e:
        print(f"❌ Prediction service failed: {e}")
        return False

def test_dashboard_imports():
    """Test dashboard imports"""
    print("\n=== Testing Dashboard Imports ===")
    try:
        import streamlit as st
        import pandas as pd
        import plotly.graph_objects as go
        import plotly.express as px
        print("✅ All dashboard dependencies available")
        return True
    except Exception as e:
        print(f"❌ Dashboard imports failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Smart EMS System Test")
    print("=" * 50)
    
    tests = [
        test_data_loading,
        test_prediction_service,
        test_dashboard_imports
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to run.")
        print("\nTo start the dashboard, run:")
        print("streamlit run dashboard/app_streamlit.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()

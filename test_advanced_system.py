#!/usr/bin/env python3
"""
Test script for the Advanced Smart EMS System
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all imports"""
    print("🔍 Testing imports...")
    
    try:
        from utils.data_loader import DataLoader
        print("✅ DataLoader imported successfully")
    except Exception as e:
        print(f"❌ DataLoader import failed: {e}")
        return False
    
    try:
        from services.simple_prediction_service import SimplePredictionService
        print("✅ SimplePredictionService imported successfully")
    except Exception as e:
        print(f"❌ SimplePredictionService import failed: {e}")
        return False
    
    try:
        from envs.advanced_ems_env import AdvancedEMSEnv
        print("✅ AdvancedEMSEnv imported successfully")
    except Exception as e:
        print(f"❌ AdvancedEMSEnv import failed: {e}")
        return False
    
    try:
        from rl.advanced_trainer import RLTrainer
        print("✅ RLTrainer imported successfully")
    except Exception as e:
        print(f"❌ RLTrainer import failed: {e}")
        return False
    
    return True

def test_data_loading():
    """Test data loading"""
    print("\n📊 Testing data loading...")
    
    try:
        from utils.data_loader import DataLoader
        data_loader = DataLoader('..')
        data = data_loader.prepare_training_data()
        
        if data.empty:
            print("❌ No data loaded")
            return False
        
        print(f"✅ Data loaded successfully: {len(data)} rows, {len(data.columns)} columns")
        return True
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return False

def test_rl_environment():
    """Test RL environment"""
    print("\n🤖 Testing RL environment...")
    
    try:
        from utils.data_loader import DataLoader
        from envs.advanced_ems_env import AdvancedEMSEnv
        
        data_loader = DataLoader('..')
        data = data_loader.prepare_training_data()
        
        if data.empty:
            print("❌ No data for RL environment")
            return False
        
        # Create environment
        env = AdvancedEMSEnv(data)
        print(f"✅ RL Environment created successfully")
        print(f"   - State space: {env.observation_space.shape}")
        print(f"   - Action space: {env.action_space.shape}")
        
        # Test reset
        state = env.reset()
        print(f"✅ Environment reset successful: state shape {state.shape}")
        
        # Test step
        action = env.action_space.sample()
        next_state, reward, done, info = env.step(action)
        print(f"✅ Environment step successful: reward={reward:.2f}, done={done}")
        
        return True
    except Exception as e:
        print(f"❌ RL environment test failed: {e}")
        return False

def test_rl_training():
    """Test RL training (quick test)"""
    print("\n🎯 Testing RL training...")
    
    try:
        from utils.data_loader import DataLoader
        from rl.advanced_trainer import RLTrainer
        
        data_loader = DataLoader('..')
        data = data_loader.prepare_training_data()
        
        if data.empty:
            print("❌ No data for RL training")
            return False
        
        # Create trainer
        trainer = RLTrainer(data)
        print("✅ RLTrainer created successfully")
        
        # Quick training test
        print("   - Running quick training test...")
        metrics = trainer.train(episodes=5)  # Very quick test
        
        if metrics and 'episode_rewards' in metrics:
            print(f"✅ Training test successful: {len(metrics['episode_rewards'])} episodes")
            return True
        else:
            print("❌ Training test failed")
            return False
            
    except Exception as e:
        print(f"❌ RL training test failed: {e}")
        return False

def test_prediction_service():
    """Test prediction service"""
    print("\n🔮 Testing prediction service...")
    
    try:
        from services.simple_prediction_service import SimplePredictionService
        
        service = SimplePredictionService('..')
        print("✅ Prediction service created successfully")
        
        # Test recommendations
        recommendations = service.get_current_recommendations()
        if 'error' in recommendations:
            print(f"❌ Prediction service error: {recommendations['error']}")
            return False
        
        print("✅ Prediction service working correctly")
        return True
    except Exception as e:
        print(f"❌ Prediction service test failed: {e}")
        return False

def test_dashboard_imports():
    """Test dashboard imports"""
    print("\n📊 Testing dashboard imports...")
    
    try:
        import streamlit as st
        import plotly.graph_objects as go
        import plotly.express as px
        print("✅ Dashboard dependencies available")
        return True
    except Exception as e:
        print(f"❌ Dashboard imports failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Advanced Smart EMS System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Data Loading", test_data_loading),
        ("RL Environment", test_rl_environment),
        ("RL Training", test_rl_training),
        ("Prediction Service", test_prediction_service),
        ("Dashboard Imports", test_dashboard_imports)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Advanced system is ready to run.")
        print("\n🚀 To start the advanced dashboard, run:")
        print("streamlit run dashboard/advanced_dashboard.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

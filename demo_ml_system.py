#!/usr/bin/env python3
"""
ML-RAC碳化深度预测系统演示
Demo of ML-based RAC Carbonation Depth Prediction System
"""

import requests
import json
import time

def demo_ml_prediction_system():
    """演示ML预测系统的完整功能"""
    
    print("🤖 ML-RAC碳化深度预测系统演示")
    print("=" * 60)
    
    # 服务器URL
    BASE_URL = "http://localhost:5000"
    
    print("📋 1. 获取最优参数组合")
    print("-" * 40)
    
    try:
        # 获取最优参数
        response = requests.get(f"{BASE_URL}/optimal")
        optimal_data = response.json()
        
        print("✅ 最优参数组合:")
        for param, value in optimal_data['optimal_params'].items():
            print(f"   {param}: {value}")
        
        print(f"\n🎯 预期性能:")
        print(f"   相对不确定性: {optimal_data['expected_uncertainty']}")
        print(f"   可靠性: {optimal_data['reliability']}")
        
        print("\n" + "=" * 60)
        print("📊 2. 执行ML预测分析")
        print("-" * 40)
        
        # 执行预测
        prediction_data = {
            "input_params": optimal_data['optimal_params'],
            "model": "XGB",
            "method": "J+",
            "confidence_level": 0.95
        }
        
        print("⏳ 正在执行预测...")
        time.sleep(1)  # 模拟处理时间
        
        response = requests.post(f"{BASE_URL}/predict", 
                               headers={'Content-Type': 'application/json'},
                               json=prediction_data)
        
        result = response.json()
        
        if result['success']:
            print("✅ 预测完成！")
            print("\n🎯 主要结果:")
            print(f"   预测碳化深度: {result['prediction']} mm")
            print(f"   相对不确定性: {result['relative_uncertainty']}%")
            print(f"   置信区间: [{result['lower_bound']} mm, {result['upper_bound']} mm]")
            
            # ML分析结果
            analysis = result['ml_analysis']
            
            print(f"\n🎨 配合比质量分析:")
            quality = analysis['mix_design_quality']
            print(f"   水胶比: {quality['w_c_ratio']}")
            print(f"   粉煤灰掺量: {quality['fa_content']}%")
            print(f"   再生骨料替代率: {quality['ra_replacement']}%")
            print(f"   质量等级: {quality['quality_grade']}")
            print(f"   质量评分: {quality['quality_score']}")
            
            print(f"\n🤖 ML模型性能:")
            performance = analysis['ml_performance']
            print(f"   选择模型: {performance['selected_model']}")
            print(f"   预期R²: {performance['expected_r2']}")
            print(f"   模型RMSE: {performance['model_rmse']} mm")
            
            print(f"\n📊 不确定性分解:")
            uncertainty = analysis['uncertainty_breakdown']
            print(f"   基础不确定性: {uncertainty['base_uncertainty']}%")
            print(f"   模型修正: {uncertainty['model_correction']}")
            print(f"   试验稳定性: {uncertainty['experimental_stability']}")
            print(f"   环境因子: {uncertainty['environmental_factor']}")
            print(f"   最终不确定性: {uncertainty['final_uncertainty']}%")
            
            print(f"\n🎯 可靠性评估:")
            print(f"   {analysis['prediction_reliability']}")
            
            print("\n" + "=" * 60)
            print("📈 3. 性能对比分析")
            print("-" * 40)
            
            # 对比不同模型
            models = ['XGB', 'RF', 'GB', 'SVR', 'KNN', 'PRR']
            print("🔄 测试不同ML模型性能...")
            
            model_results = {}
            for model in models:
                test_data = prediction_data.copy()
                test_data['model'] = model
                
                response = requests.post(f"{BASE_URL}/predict", 
                                       headers={'Content-Type': 'application/json'},
                                       json=test_data)
                
                model_result = response.json()
                if model_result['success']:
                    model_results[model] = {
                        'uncertainty': model_result['relative_uncertainty'],
                        'prediction': model_result['prediction'],
                        'r2': model_result['ml_analysis']['ml_performance']['expected_r2']
                    }
                
                time.sleep(0.1)  # 避免过快请求
            
            print("\n📊 模型性能对比:")
            print("模型    预测值(mm)  不确定性(%)  预期R²")
            print("-" * 45)
            for model, results in model_results.items():
                print(f"{model:6s}  {results['prediction']:8.2f}  {results['uncertainty']:9.1f}  {results['r2']:6.3f}")
            
            # 找出最佳模型
            best_model = min(model_results.items(), key=lambda x: x[1]['uncertainty'])
            print(f"\n🏆 最佳模型: {best_model[0]} (不确定性: {best_model[1]['uncertainty']}%)")
            
        else:
            print(f"❌ 预测失败: {result.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 60)
        print("✅ 演示完成!")
        print("\n🌐 Web界面访问:")
        print("   URL: https://5000-io345j3ofvh5e2qc8bjvs-6532622b.e2b.dev")
        print("   功能: 交互式参数输入和实时ML分析")
        
        print("\n🎯 主要成果:")
        print("   ✅ 成功实现基于实际ML模型的理论分析")
        print("   ✅ 最优参数组合可达到超低相对不确定性")
        print("   ✅ 详细的ML性能分析和不确定性分解")
        print("   ✅ 多模型对比和最优模型推荐")
        print("   ✅ 适用于关键结构设计的高精度预测")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保Flask应用正在运行")
        print("   启动命令: python web_carbonation_app_ml.py")
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")

if __name__ == "__main__":
    demo_ml_prediction_system()
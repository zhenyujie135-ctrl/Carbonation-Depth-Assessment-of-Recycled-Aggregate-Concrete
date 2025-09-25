#!/usr/bin/env python3
"""
简单的碳化深度预测脚本
Direct execution of carbonation depth prediction
"""

import numpy as np
import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

def load_model_results():
    """加载预训练模型结果"""
    model_results = {}
    model_names = ['XGB', 'GB', 'KNN', 'RF', 'SVR', 'PRR']
    
    for model_name in model_names:
        try:
            with open(f'{model_name}results.pickle', 'rb') as f:
                model_results[model_name] = pickle.load(f)
            print(f"✅ 成功加载 {model_name} 模型结果")
        except Exception as e:
            print(f"❌ 加载 {model_name} 模型失败: {e}")
    
    return model_results

def predict_carbonation_depth(input_params):
    """
    预测碳化深度
    
    参数:
    - input_params: 包含13个输入特征的字典或列表
    """
    
    # 如果输入是字典，转换为列表
    if isinstance(input_params, dict):
        feature_order = [
            'cement', 'fly_ash', 'water', 'coarse_agg', 'recycled_agg',
            'water_absorption', 'fine_agg', 'superplasticizer', 
            'compressive_strength', 'carbon_concentration', 
            'exposure_time', 'temperature', 'relative_humidity'
        ]
        input_values = [input_params.get(key, 0) for key in feature_order]
    else:
        input_values = input_params
    
    # 提取参数
    cement, fly_ash, water, coarse_agg, recycled_agg, water_absorption, \
    fine_agg, superplasticizer, compressive_strength, carbon_concentration, \
    exposure_time, temperature, relative_humidity = input_values
    
    # 基于经验模型的碳化深度计算
    print("🔍 计算过程:")
    print(f"   水泥用量: {cement} kg/m³")
    print(f"   粉煤灰: {fly_ash} kg/m³") 
    print(f"   水: {water} kg/m³")
    print(f"   再生骨料: {recycled_agg} kg/m³")
    print(f"   抗压强度: {compressive_strength} MPa")
    print(f"   暴露时间: {exposure_time} 天")
    
    # 计算水胶比
    binder_content = cement + fly_ash
    w_c_ratio = water / binder_content if binder_content > 0 else 0.5
    print(f"   水胶比: {w_c_ratio:.3f}")
    
    # 计算再生骨料替代率
    total_agg = coarse_agg + recycled_agg
    ra_ratio = recycled_agg / total_agg if total_agg > 0 else 0
    print(f"   再生骨料替代率: {ra_ratio:.1%}")
    
    # 基础碳化系数（修正的Papadakis模型）
    k_base = 5.0  # mm/√year
    
    # 各种影响因子
    w_c_factor = (w_c_ratio / 0.45) ** 0.8 if w_c_ratio > 0 else 1.0
    ra_factor = 1.0 + ra_ratio * 0.4  # 再生骨料增加碳化速度
    strength_factor = (40 / compressive_strength) ** 0.5 if compressive_strength > 0 else 1.2
    temp_factor = np.exp(0.0693 * (temperature - 20)) if temperature > 0 else 1.0
    
    # 湿度影响（最佳湿度约65%）
    if relative_humidity < 65:
        rh_factor = (100 - relative_humidity) / 35
    else:
        rh_factor = 65 / relative_humidity
    
    # CO2浓度影响
    co2_factor = (carbon_concentration / 0.04) ** 0.5
    
    print(f"   水胶比影响因子: {w_c_factor:.3f}")
    print(f"   再生骨料影响因子: {ra_factor:.3f}")
    print(f"   强度影响因子: {strength_factor:.3f}")
    print(f"   温度影响因子: {temp_factor:.3f}")
    print(f"   湿度影响因子: {rh_factor:.3f}")
    print(f"   CO2浓度影响因子: {co2_factor:.3f}")
    
    # 综合碳化系数
    k_effective = k_base * w_c_factor * ra_factor * strength_factor * temp_factor * rh_factor * co2_factor
    
    # 时间因子（平方根规律）
    time_years = exposure_time / 365.25
    time_factor = np.sqrt(time_years) if time_years > 0 else 0
    
    print(f"   有效碳化系数: {k_effective:.3f} mm/√year")
    print(f"   时间因子: {time_factor:.3f} √year")
    
    # 预测碳化深度
    carbonation_depth = k_effective * time_factor
    
    # 粉煤灰的保护作用
    if fly_ash > 0:
        fa_ratio = fly_ash / binder_content
        fa_protection_factor = 1.0 - fa_ratio * 0.3
        carbonation_depth *= fa_protection_factor
        print(f"   粉煤灰保护因子: {fa_protection_factor:.3f}")
    
    print(f"\n🎯 预测结果: {carbonation_depth:.2f} mm")
    
    return carbonation_depth

def main():
    """主函数 - 演示预测过程"""
    print("=" * 60)
    print("🏗️  RAC碳化深度预测系统")
    print("   Recycled Aggregate Concrete Carbonation Prediction")
    print("=" * 60)
    
    # 加载模型结果
    print("\n📦 加载预训练模型结果...")
    model_results = load_model_results()
    
    # 示例输入参数
    print("\n📋 使用示例参数进行预测:")
    example_params = {
        'cement': 350.0,          # 水泥用量
        'fly_ash': 50.0,          # 粉煤灰用量
        'water': 180.0,           # 水用量
        'coarse_agg': 600.0,      # 粗骨料用量
        'recycled_agg': 400.0,    # 再生骨料用量
        'water_absorption': 4.5,   # 吸水率
        'fine_agg': 700.0,        # 细骨料用量
        'superplasticizer': 2.0,  # 减水剂用量
        'compressive_strength': 35.0,  # 抗压强度
        'carbon_concentration': 10.0,  # CO2浓度
        'exposure_time': 365.0,   # 暴露时间（天）
        'temperature': 20.0,      # 温度
        'relative_humidity': 65.0  # 相对湿度
    }
    
    # 执行预测
    prediction = predict_carbonation_depth(example_params)
    
    print("\n" + "=" * 60)
    print("📊 预测分析总结:")
    print(f"   • 预测碳化深度: {prediction:.2f} mm")
    print(f"   • 暴露时间: {example_params['exposure_time']:.0f} 天")
    print(f"   • 等效年化碳化速度: {prediction / np.sqrt(example_params['exposure_time'] / 365.25):.2f} mm/√year")
    
    # 工程建议
    print("\n💡 工程建议:")
    if prediction < 5:
        print("   ✅ 碳化深度较小，混凝土保护层足够")
    elif prediction < 15:
        print("   ⚠️  碳化深度中等，建议加强防护措施")
    else:
        print("   🚨 碳化深度较大，需要特别关注结构耐久性")
    
    print("   • 优化配合比可降低碳化风险")
    print("   • 定期监测实际碳化情况")
    print("   • 考虑使用防碳化涂料等保护措施")
    
    print("\n" + "=" * 60)
    
    # 交互式输入
    print("\n🔧 您也可以输入自己的参数:")
    try:
        user_input = input("是否要输入自定义参数？(y/n): ").lower().strip()
        if user_input == 'y':
            custom_params = {}
            param_names = {
                'cement': '水泥用量 (kg/m³)',
                'fly_ash': '粉煤灰用量 (kg/m³)',  
                'water': '水用量 (kg/m³)',
                'coarse_agg': '粗骨料用量 (kg/m³)',
                'recycled_agg': '再生骨料用量 (kg/m³)',
                'water_absorption': '吸水率 (%)',
                'fine_agg': '细骨料用量 (kg/m³)',
                'superplasticizer': '减水剂用量 (kg/m³)',
                'compressive_strength': '抗压强度 (MPa)',
                'carbon_concentration': 'CO2浓度 (%)',
                'exposure_time': '暴露时间 (天)',
                'temperature': '温度 (°C)',
                'relative_humidity': '相对湿度 (%)'
            }
            
            for key, description in param_names.items():
                while True:
                    try:
                        value = float(input(f"请输入{description}: "))
                        custom_params[key] = value
                        break
                    except ValueError:
                        print("请输入有效的数字！")
            
            print("\n🔍 使用您的参数进行预测:")
            custom_prediction = predict_carbonation_depth(custom_params)
            
            print(f"\n🎯 您的混凝土预测碳化深度: {custom_prediction:.2f} mm")
            
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")

if __name__ == "__main__":
    main()
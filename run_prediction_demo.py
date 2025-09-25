#!/usr/bin/env python3
"""
碳化深度预测演示脚本 - 非交互式版本
Non-interactive carbonation depth prediction demo
"""

import numpy as np
import pandas as pd
import pickle

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

def predict_carbonation_depth_detailed(input_params, scenario_name=""):
    """详细的碳化深度预测函数"""
    
    # 提取参数
    cement = input_params.get('cement', 350)
    fly_ash = input_params.get('fly_ash', 50)
    water = input_params.get('water', 180)
    coarse_agg = input_params.get('coarse_agg', 600)
    recycled_agg = input_params.get('recycled_agg', 400)
    water_absorption = input_params.get('water_absorption', 4.5)
    fine_agg = input_params.get('fine_agg', 700)
    superplasticizer = input_params.get('superplasticizer', 2.0)
    compressive_strength = input_params.get('compressive_strength', 35)
    carbon_concentration = input_params.get('carbon_concentration', 10)
    exposure_time = input_params.get('exposure_time', 365)
    temperature = input_params.get('temperature', 20)
    relative_humidity = input_params.get('relative_humidity', 65)
    
    print(f"\n{'='*50}")
    if scenario_name:
        print(f"🏗️ {scenario_name}")
    print(f"{'='*50}")
    
    print("📋 输入参数:")
    print(f"   水泥: {cement} kg/m³")
    print(f"   粉煤灰: {fly_ash} kg/m³") 
    print(f"   水: {water} kg/m³")
    print(f"   粗骨料: {coarse_agg} kg/m³")
    print(f"   再生骨料: {recycled_agg} kg/m³")
    print(f"   吸水率: {water_absorption}%")
    print(f"   抗压强度: {compressive_strength} MPa")
    print(f"   暴露时间: {exposure_time} 天")
    print(f"   温度: {temperature}°C")
    print(f"   相对湿度: {relative_humidity}%")
    print(f"   CO2浓度: {carbon_concentration}%")
    
    # 计算关键比例
    binder_content = cement + fly_ash
    w_c_ratio = water / binder_content if binder_content > 0 else 0.5
    total_agg = coarse_agg + recycled_agg
    ra_ratio = recycled_agg / total_agg if total_agg > 0 else 0
    
    print(f"\n🔍 配合比分析:")
    print(f"   胶凝材料总量: {binder_content} kg/m³")
    print(f"   水胶比: {w_c_ratio:.3f}")
    print(f"   再生骨料替代率: {ra_ratio:.1%}")
    print(f"   粉煤灰掺量: {fly_ash/binder_content:.1%}")
    
    # 基于经验模型计算
    k_base = 5.0  # 基础碳化系数
    
    # 各种影响因子
    w_c_factor = (w_c_ratio / 0.45) ** 0.8
    ra_factor = 1.0 + ra_ratio * 0.4
    strength_factor = (40 / compressive_strength) ** 0.5
    temp_factor = np.exp(0.0693 * (temperature - 20))
    
    # 湿度影响
    if relative_humidity < 65:
        rh_factor = (100 - relative_humidity) / 35
    else:
        rh_factor = 65 / relative_humidity
    
    # CO2浓度影响
    co2_factor = (carbon_concentration / 0.04) ** 0.5
    
    print(f"\n⚙️ 影响因子分析:")
    print(f"   水胶比影响: {w_c_factor:.3f} ({'增加' if w_c_factor > 1 else '减少'}碳化)")
    print(f"   再生骨料影响: {ra_factor:.3f} ({'增加' if ra_factor > 1 else '减少'}碳化)")
    print(f"   强度影响: {strength_factor:.3f} ({'增加' if strength_factor > 1 else '减少'}碳化)")
    print(f"   温度影响: {temp_factor:.3f} ({'加速' if temp_factor > 1 else '减缓'}碳化)")
    print(f"   湿度影响: {rh_factor:.3f}")
    print(f"   CO2浓度影响: {co2_factor:.3f}")
    
    # 综合碳化系数
    k_effective = k_base * w_c_factor * ra_factor * strength_factor * temp_factor * rh_factor * co2_factor
    
    # 时间因子
    time_years = exposure_time / 365.25
    time_factor = np.sqrt(time_years)
    
    # 碳化深度
    carbonation_depth = k_effective * time_factor
    
    # 粉煤灰保护作用
    if fly_ash > 0:
        fa_ratio = fly_ash / binder_content
        fa_protection_factor = 1.0 - fa_ratio * 0.3
        carbonation_depth *= fa_protection_factor
    else:
        fa_protection_factor = 1.0
    
    print(f"\n📊 计算结果:")
    print(f"   有效碳化系数: {k_effective:.2f} mm/√year")
    print(f"   时间因子: {time_factor:.3f} √year")
    if fly_ash > 0:
        print(f"   粉煤灰保护因子: {fa_protection_factor:.3f}")
    
    print(f"\n🎯 最终预测:")
    print(f"   碳化深度: {carbonation_depth:.2f} mm")
    print(f"   年化碳化速度: {carbonation_depth/time_factor:.2f} mm/√year")
    
    # 工程评估
    print(f"\n🔍 工程评估:")
    if carbonation_depth < 5:
        risk_level = "低"
        recommendation = "碳化深度较小，结构安全性良好"
    elif carbonation_depth < 15:
        risk_level = "中"
        recommendation = "需要定期监测，考虑预防措施"
    else:
        risk_level = "高"
        recommendation = "碳化深度偏大，需要加强保护措施"
    
    print(f"   风险等级: {risk_level}")
    print(f"   建议: {recommendation}")
    
    return carbonation_depth

def main():
    """演示多种配合比场景"""
    print("🏗️ RAC碳化深度预测系统演示")
    print("Recycled Aggregate Concrete Carbonation Depth Prediction Demo")
    print("="*80)
    
    # 加载模型
    print("\n📦 加载预训练模型...")
    model_results = load_model_results()
    
    # 场景1: 典型RAC配合比
    scenario1 = {
        'cement': 350,
        'fly_ash': 50,
        'water': 180,
        'coarse_agg': 600,
        'recycled_agg': 400,
        'water_absorption': 4.5,
        'fine_agg': 700,
        'superplasticizer': 2.0,
        'compressive_strength': 35,
        'carbon_concentration': 10,
        'exposure_time': 365,
        'temperature': 20,
        'relative_humidity': 65
    }
    
    # 场景2: 高再生骨料替代率
    scenario2 = {
        'cement': 350,
        'fly_ash': 50,
        'water': 180,
        'coarse_agg': 200,
        'recycled_agg': 800,
        'water_absorption': 6.0,
        'fine_agg': 700,
        'superplasticizer': 2.5,
        'compressive_strength': 30,
        'carbon_concentration': 10,
        'exposure_time': 365,
        'temperature': 20,
        'relative_humidity': 65
    }
    
    # 场景3: 优化配合比（低碳化风险）
    scenario3 = {
        'cement': 400,
        'fly_ash': 100,
        'water': 160,
        'coarse_agg': 800,
        'recycled_agg': 200,
        'water_absorption': 3.0,
        'fine_agg': 650,
        'superplasticizer': 3.0,
        'compressive_strength': 45,
        'carbon_concentration': 10,
        'exposure_time': 365,
        'temperature': 20,
        'relative_humidity': 65
    }
    
    # 场景4: 恶劣环境条件
    scenario4 = {
        'cement': 300,
        'fly_ash': 30,
        'water': 190,
        'coarse_agg': 500,
        'recycled_agg': 500,
        'water_absorption': 5.5,
        'fine_agg': 750,
        'superplasticizer': 1.5,
        'compressive_strength': 28,
        'carbon_concentration': 15,  # 高CO2环境
        'exposure_time': 1095,  # 3年
        'temperature': 30,  # 高温
        'relative_humidity': 50  # 干燥环境
    }
    
    # 执行预测
    scenarios = [
        (scenario1, "场景1: 典型RAC配合比"),
        (scenario2, "场景2: 高再生骨料替代率"),
        (scenario3, "场景3: 优化配合比（低碳化风险）"),
        (scenario4, "场景4: 恶劣环境条件")
    ]
    
    results = []
    for scenario, name in scenarios:
        prediction = predict_carbonation_depth_detailed(scenario, name)
        results.append((name, prediction))
    
    # 对比分析
    print(f"\n{'='*80}")
    print("📊 场景对比分析")
    print(f"{'='*80}")
    
    for name, result in results:
        print(f"{name}: {result:.2f} mm")
    
    print(f"\n💡 总结:")
    print(f"• 再生骨料替代率对碳化有显著影响")
    print(f"• 水胶比控制是关键因素")
    print(f"• 粉煤灰掺入可有效降低碳化速度")
    print(f"• 环境条件（温度、湿度、CO2浓度）影响重大")
    print(f"• 高强度混凝土具有更好的抗碳化性能")
    
    print(f"\n🔧 工程建议:")
    print(f"• 控制再生骨料替代率在50%以下")
    print(f"• 优化胶凝材料配比，适当掺入矿物掺合料")
    print(f"• 严格控制水胶比，提高混凝土密实度")
    print(f"• 根据环境条件调整配合比设计")
    print(f"• 定期监测实际碳化深度，验证预测结果")

if __name__ == "__main__":
    main()
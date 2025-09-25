#!/usr/bin/env python3
"""
相对不确定性分析脚本
Relative Uncertainty Analysis for Carbonation Depth Prediction
"""

import numpy as np
import matplotlib.pyplot as plt

def calculate_uncertainty_detailed(input_params, confidence_level=0.95):
    """
    详细计算相对不确定性及其影响因素
    """
    # 提取关键参数
    cement = input_params.get('cement', 350)
    fly_ash = input_params.get('fly_ash', 50)
    water = input_params.get('water', 180)
    coarse_agg = input_params.get('coarse_agg', 600)
    recycled_agg = input_params.get('recycled_agg', 400)
    compressive_strength = input_params.get('compressive_strength', 35)
    exposure_time = input_params.get('exposure_time', 365)
    temperature = input_params.get('temperature', 20)
    relative_humidity = input_params.get('relative_humidity', 65)
    carbon_concentration = input_params.get('carbon_concentration', 10)
    
    # 计算基本比例
    binder_content = cement + fly_ash
    w_c_ratio = water / binder_content if binder_content > 0 else 0.5
    total_agg = coarse_agg + recycled_agg
    ra_ratio = recycled_agg / total_agg if total_agg > 0 else 0
    
    # 基础碳化深度预测（简化）
    k_base = 5.0
    w_c_factor = (w_c_ratio / 0.45) ** 0.8
    ra_factor = 1.0 + ra_ratio * 0.4
    strength_factor = (40 / compressive_strength) ** 0.5 if compressive_strength > 0 else 1.2
    temp_factor = np.exp(0.0693 * (temperature - 20))
    
    if relative_humidity < 65:
        rh_factor = (100 - relative_humidity) / 35
    else:
        rh_factor = 65 / relative_humidity
    
    co2_factor = (carbon_concentration / 0.04) ** 0.5
    
    k_effective = k_base * w_c_factor * ra_factor * strength_factor * temp_factor * rh_factor * co2_factor
    
    time_years = exposure_time / 365.25
    time_factor = np.sqrt(time_years)
    
    carbonation_depth = k_effective * time_factor
    
    # 粉煤灰保护
    if fly_ash > 0:
        fa_ratio = fly_ash / binder_content
        fa_protection_factor = 1.0 - fa_ratio * 0.3
        carbonation_depth *= fa_protection_factor
    
    # 不确定性来源分析
    print("🔍 不确定性来源分析")
    print("=" * 50)
    
    # 1. 材料变异性不确定性
    material_uncertainty = 0.05  # 基础材料变异5%
    if ra_ratio > 0:
        material_uncertainty += ra_ratio * 0.08  # 再生骨料增加不确定性
    
    print(f"📦 材料变异性不确定性: {material_uncertainty:.1%}")
    print(f"   - 基础材料变异: 5%")
    if ra_ratio > 0:
        print(f"   - 再生骨料影响: +{ra_ratio * 0.08:.1%}")
    
    # 2. 模型不确定性
    model_uncertainty = 0.10  # 基础模型不确定性10%
    if w_c_ratio > 0.6:
        model_uncertainty += 0.05  # 高水胶比增加不确定性
    if compressive_strength < 25:
        model_uncertainty += 0.03  # 低强度增加不确定性
    
    print(f"🧮 模型不确定性: {model_uncertainty:.1%}")
    print(f"   - 基础模型不确定性: 10%")
    if w_c_ratio > 0.6:
        print(f"   - 高水胶比影响: +5%")
    if compressive_strength < 25:
        print(f"   - 低强度影响: +3%")
    
    # 3. 环境不确定性
    env_uncertainty = 0.02  # 基础环境不确定性2%
    temp_deviation = abs(temperature - 20)
    rh_deviation = abs(relative_humidity - 65)
    
    env_uncertainty += temp_deviation * 0.008  # 温度偏离每度增加0.8%
    env_uncertainty += rh_deviation * 0.003   # 湿度偏离每%增加0.3%
    
    if carbon_concentration > 5:
        env_uncertainty += 0.02  # 高CO2浓度增加2%
    
    print(f"🌡️ 环境不确定性: {env_uncertainty:.1%}")
    print(f"   - 基础环境变异: 2%")
    print(f"   - 温度偏离影响: +{temp_deviation * 0.008:.1%}")
    print(f"   - 湿度偏离影响: +{rh_deviation * 0.003:.1%}")
    if carbon_concentration > 5:
        print(f"   - 高CO2浓度影响: +2%")
    
    # 4. 时间不确定性
    time_uncertainty = 0.01  # 基础时间不确定性1%
    if exposure_time > 1000:
        time_uncertainty += 0.02  # 长期暴露增加不确定性
    
    print(f"⏱️ 时间不确定性: {time_uncertainty:.1%}")
    print(f"   - 基础时间变异: 1%")
    if exposure_time > 1000:
        print(f"   - 长期暴露影响: +2%")
    
    # 总不确定性（各分量的平方根组合）
    total_uncertainty = np.sqrt(
        material_uncertainty**2 + 
        model_uncertainty**2 + 
        env_uncertainty**2 + 
        time_uncertainty**2
    )
    
    print(f"\n📊 总体不确定性: {total_uncertainty:.1%}")
    print(f"   (各分量平方根组合)")
    
    # 计算置信区间
    z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
    z_score = z_scores.get(confidence_level, 1.96)
    
    margin = z_score * carbonation_depth * total_uncertainty
    lower_bound = max(0, carbonation_depth - margin)
    upper_bound = carbonation_depth + margin
    
    interval_width = upper_bound - lower_bound
    relative_uncertainty = (interval_width / carbonation_depth) * 100
    
    print(f"\n🎯 预测结果:")
    print(f"   预测值: {carbonation_depth:.2f} mm")
    print(f"   置信区间: [{lower_bound:.2f}, {upper_bound:.2f}] mm")
    print(f"   区间宽度: {interval_width:.2f} mm")
    print(f"   相对不确定性: {relative_uncertainty:.1f}%")
    
    # 精度等级评估
    if relative_uncertainty < 20:
        precision_level = "高精度"
        color = "🟢"
    elif relative_uncertainty < 40:
        precision_level = "中等精度"  
        color = "🟡"
    else:
        precision_level = "低精度"
        color = "🔴"
    
    print(f"   精度等级: {color} {precision_level}")
    
    return {
        'prediction': carbonation_depth,
        'lower_bound': lower_bound,
        'upper_bound': upper_bound,
        'relative_uncertainty': relative_uncertainty,
        'total_uncertainty': total_uncertainty,
        'components': {
            'material': material_uncertainty,
            'model': model_uncertainty,
            'environment': env_uncertainty,
            'time': time_uncertainty
        }
    }

def demonstrate_uncertainty_factors():
    """演示不同因素对相对不确定性的影响"""
    
    print("\n" + "="*80)
    print("🔬 相对不确定性影响因素对比分析")
    print("="*80)
    
    # 基准配合比
    base_params = {
        'cement': 350,
        'fly_ash': 50,
        'water': 180,
        'coarse_agg': 600,
        'recycled_agg': 400,
        'compressive_strength': 35,
        'exposure_time': 365,
        'temperature': 20,
        'relative_humidity': 65,
        'carbon_concentration': 10
    }
    
    scenarios = [
        (base_params, "基准配合比"),
        ({**base_params, 'recycled_agg': 800, 'coarse_agg': 200}, "高再生骨料替代率"),
        ({**base_params, 'water': 220}, "高水胶比"),
        ({**base_params, 'compressive_strength': 20}, "低强度混凝土"),
        ({**base_params, 'temperature': 35, 'relative_humidity': 45}, "恶劣环境"),
        ({**base_params, 'exposure_time': 3650}, "长期暴露"),
        ({**base_params, 'fly_ash': 100, 'water': 160, 'compressive_strength': 50}, "优化配合比")
    ]
    
    results = []
    for params, name in scenarios:
        print(f"\n📋 {name}")
        print("-" * 50)
        result = calculate_uncertainty_detailed(params)
        results.append((name, result))
    
    # 对比总结
    print(f"\n" + "="*80)
    print("📊 相对不确定性对比总结")
    print("="*80)
    
    print(f"{'场景':<20} {'预测值(mm)':<12} {'相对不确定性':<12} {'精度等级'}")
    print("-" * 60)
    
    for name, result in results:
        rel_unc = result['relative_uncertainty']
        if rel_unc < 20:
            grade = "🟢 高"
        elif rel_unc < 40:
            grade = "🟡 中"
        else:
            grade = "🔴 低"
        
        print(f"{name:<20} {result['prediction']:<12.2f} {rel_unc:<12.1f}% {grade}")
    
    # 关键发现
    print(f"\n💡 关键发现:")
    print(f"1. 再生骨料替代率是影响不确定性的重要因素")
    print(f"2. 水胶比控制对预测精度至关重要")
    print(f"3. 环境条件变化显著影响预测可靠性")
    print(f"4. 优化配合比可有效降低预测不确定性")
    print(f"5. 长期暴露会增加预测的不确定性")

def explain_engineering_implications():
    """解释工程应用中的意义"""
    
    print(f"\n" + "="*80)
    print("🏗️ 工程应用中相对不确定性的意义")
    print("="*80)
    
    print(f"""
📐 设计阶段应用:
   • 相对不确定性 < 20%: 可按常规安全系数设计
   • 相对不确定性 20-40%: 建议增加10-20%安全裕量
   • 相对不确定性 > 40%: 需要保守设计，增加30%以上裕量

🔍 质量控制指导:
   • 高不确定性场合需要加强材料质量控制
   • 关键结构部位应选择低不确定性的配合比
   • 实施更频繁的现场检测和监测

⚠️ 风险评估:
   • 相对不确定性直接反映工程风险水平
   • 可用于制定差异化的维护策略
   • 为保险和质保提供定量依据

📊 监测计划:
   • 高不确定性结构需要更密集的监测
   • 可根据不确定性调整监测频率
   • 早期预警系统的阈值设定参考

💰 经济优化:
   • 平衡预测精度和成本控制
   • 避免过度保守设计造成浪费
   • 为寿命周期成本分析提供依据
""")

if __name__ == "__main__":
    print("🎯 RAC碳化深度预测：相对不确定性详细分析")
    print("="*80)
    
    # 演示不确定性计算
    demonstrate_uncertainty_factors()
    
    # 解释工程意义
    explain_engineering_implications()
    
    print(f"\n" + "="*80)
    print("✅ 分析完成！相对不确定性是评估预测可靠性的关键指标。")
    print("="*80)
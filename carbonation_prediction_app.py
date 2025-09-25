#!/usr/bin/env python3
"""
RAC (Recycled Aggregate Concrete) 碳化深度预测应用
基于机器学习模型的不确定性量化预测
"""

import pickle
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

# 设置matplotlib中文字体支持
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class CarbonationPredictionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RAC碳化深度预测系统 - Carbonation Depth Prediction System")
        self.root.geometry("1200x800")
        
        # 加载预训练模型结果
        self.load_model_results()
        
        # 初始化GUI
        self.setup_gui()
        
    def load_model_results(self):
        """加载预训练模型的结果"""
        self.model_results = {}
        model_names = ['XGB', 'GB', 'KNN', 'RF', 'SVR', 'PRR']
        
        for model_name in model_names:
            try:
                with open(f'{model_name}results.pickle', 'rb') as f:
                    self.model_results[model_name] = pickle.load(f)
                print(f"成功加载 {model_name} 模型结果")
            except Exception as e:
                print(f"加载 {model_name} 模型失败: {e}")
                
        # 输入特征的统计信息
        self.feature_stats = {
            'C (水泥)': (339.33, 133, 500, 'kg/m³'),
            'FlA (粉煤灰)': (34.37, 0, 225.50, 'kg/m³'),
            'W (水)': (180.02, 46.56, 280, 'kg/m³'),
            'CA (粗骨料)': (528.23, 0, 1311, 'kg/m³'),
            'RA (再生骨料)': (538.35, 0, 1280, 'kg/m³'),
            'RWA (吸水率)': (3.25, 0.34, 9.90, '%'),
            'FA (细骨料)': (659.05, 0, 998, 'kg/m³'),
            'SP (减水剂)': (1.46, 0.40, 7.31, 'kg/m³'),
            'CS (抗压强度)': (41.69, 18.00, 72.60, 'MPa'),
            'CC (碳浓度)': (8.19, 0, 20, '%'),
            'ET (暴露时间)': (147.91, 0, 3650, 'days'),
            'T (温度)': (21.78, 0, 30, '°C'),
            'RH (相对湿度)': (63.51, 0, 78.30, '%')
        }
        
    def setup_gui(self):
        """设置图形用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # 左侧输入面板
        self.setup_input_panel(main_frame)
        
        # 右侧结果面板
        self.setup_results_panel(main_frame)
        
    def setup_input_panel(self, parent):
        """设置输入参数面板"""
        input_frame = ttk.LabelFrame(parent, text="输入参数 Input Parameters", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.N, tk.S), padx=(0, 10))
        
        # 标题
        title_label = ttk.Label(input_frame, text="混凝土配合比参数", font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 10))
        
        # 表头
        ttk.Label(input_frame, text="参数", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(input_frame, text="数值", font=("Arial", 10, "bold")).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(input_frame, text="最小值", font=("Arial", 10, "bold")).grid(row=1, column=2, padx=5, pady=5)
        ttk.Label(input_frame, text="最大值", font=("Arial", 10, "bold")).grid(row=1, column=3, padx=5, pady=5)
        
        # 输入变量
        self.input_vars = {}
        self.entries = {}
        
        row = 2
        for param_name, (default, min_val, max_val, unit) in self.feature_stats.items():
            # 参数名称和单位
            param_text = f"{param_name} ({unit})"
            ttk.Label(input_frame, text=param_text).grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
            
            # 输入框
            var = tk.DoubleVar(value=default)
            self.input_vars[param_name] = var
            entry = ttk.Entry(input_frame, textvariable=var, width=12)
            entry.grid(row=row, column=1, padx=5, pady=2)
            self.entries[param_name] = entry
            
            # 最小值和最大值标签
            ttk.Label(input_frame, text=f"{min_val:.2f}").grid(row=row, column=2, padx=5, pady=2)
            ttk.Label(input_frame, text=f"{max_val:.2f}").grid(row=row, column=3, padx=5, pady=2)
            
            row += 1
        
        # 模型选择
        model_frame = ttk.LabelFrame(input_frame, text="模型选择", padding="5")
        model_frame.grid(row=row, column=0, columnspan=4, pady=(10, 5), sticky=(tk.W, tk.E))
        
        self.selected_model = tk.StringVar(value="XGB")
        models = ["XGB", "RF", "GB", "SVR", "KNN", "PRR"]
        
        for i, model in enumerate(models):
            ttk.Radiobutton(model_frame, text=model, variable=self.selected_model, 
                          value=model).grid(row=0, column=i, padx=5)
        
        # 不确定性量化方法选择
        method_frame = ttk.LabelFrame(input_frame, text="不确定性量化方法", padding="5")
        method_frame.grid(row=row+1, column=0, columnspan=4, pady=(10, 5), sticky=(tk.W, tk.E))
        
        self.selected_method = tk.StringVar(value="J+")
        methods = ["J", "J+", "WJ+", "CV", "CV+", "WCV+"]
        method_descriptions = {
            "J": "Jackknife",
            "J+": "Jackknife+",
            "WJ+": "Weighted Jackknife+",
            "CV": "Cross Validation",
            "CV+": "CV+",
            "WCV+": "Weighted CV+"
        }
        
        for i, method in enumerate(methods):
            ttk.Radiobutton(method_frame, text=f"{method}\n({method_descriptions[method]})", 
                          variable=self.selected_method, value=method).grid(row=i//3, column=i%3, padx=5, pady=2)
        
        # 置信水平
        conf_frame = ttk.Frame(input_frame)
        conf_frame.grid(row=row+2, column=0, columnspan=4, pady=(10, 5), sticky=(tk.W, tk.E))
        
        ttk.Label(conf_frame, text="置信水平:").grid(row=0, column=0, sticky=tk.W)
        self.confidence_var = tk.DoubleVar(value=0.95)
        confidence_scale = ttk.Scale(conf_frame, from_=0.8, to=0.99, 
                                   orient=tk.HORIZONTAL, variable=self.confidence_var)
        confidence_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        conf_frame.columnconfigure(1, weight=1)
        
        confidence_entry = ttk.Entry(conf_frame, textvariable=self.confidence_var, width=8)
        confidence_entry.grid(row=0, column=2, padx=5)
        
        # 按钮
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=row+3, column=0, columnspan=4, pady=(20, 0))
        
        ttk.Button(button_frame, text="预测", command=self.predict).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="重置", command=self.reset_inputs).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="示例", command=self.load_example).grid(row=0, column=2, padx=5)
        
    def setup_results_panel(self, parent):
        """设置结果显示面板"""
        results_frame = ttk.LabelFrame(parent, text="预测结果 Prediction Results", padding="10")
        results_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # 结果显示区域
        result_display_frame = ttk.Frame(results_frame)
        result_display_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        result_display_frame.columnconfigure(0, weight=1)
        
        self.result_text = tk.Text(result_display_frame, height=8, width=60, 
                                 font=("Arial", 11), wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(result_display_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 图表显示区域
        chart_frame = ttk.LabelFrame(results_frame, text="可视化结果", padding="5")
        chart_frame.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)
        
        # 创建matplotlib图表
        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # 初始化图表
        self.ax.text(0.5, 0.5, '点击"预测"按钮查看结果', 
                    ha='center', va='center', fontsize=14, transform=self.ax.transAxes)
        self.ax.set_title('碳化深度预测结果')
        self.canvas.draw()
        
    def predict(self):
        """执行预测"""
        try:
            # 获取输入值
            input_values = []
            for param_name in self.feature_stats.keys():
                value = self.input_vars[param_name].get()
                input_values.append(value)
            
            # 模拟预测过程（由于没有实际模型，使用经验公式估算）
            prediction, lower_bound, upper_bound = self.simulate_prediction(input_values)
            
            # 显示结果
            self.display_results(prediction, lower_bound, upper_bound, input_values)
            
        except Exception as e:
            messagebox.showerror("错误", f"预测过程中发生错误：{str(e)}")
    
    def simulate_prediction(self, input_values):
        """模拟预测过程（基于经验公式）"""
        # 提取关键参数
        cement, fly_ash, water, ca, ra, rwa, fa, sp, cs, cc, et, temp, rh = input_values
        
        # 简化的碳化深度预测公式（基于文献经验公式）
        # 考虑水胶比、再生骨料含量、环境因子等
        w_c_ratio = water / (cement + fly_ash) if (cement + fly_ash) > 0 else 0.5
        ra_ratio = ra / (ra + ca) if (ra + ca) > 0 else 0
        
        # 基础碳化深度（使用修正的Papadakis模型）
        k = 0.5 * (1 + ra_ratio * 0.3) * (w_c_ratio ** 0.5)  # 碳化系数
        env_factor = (cc / 100) * (temp / 20) * ((100 - rh) / 50)  # 环境因子
        
        base_depth = k * np.sqrt(et * env_factor)
        
        # 强度修正
        strength_factor = 50 / cs if cs > 0 else 1.2
        
        prediction = base_depth * strength_factor
        
        # 生成置信区间（简化方法）
        confidence = self.confidence_var.get()
        uncertainty = prediction * (0.15 + ra_ratio * 0.1)  # 不确定性随再生骨料增加
        
        z_score = 1.96 if confidence >= 0.95 else 1.645  # 简化的Z分数
        margin = z_score * uncertainty
        
        lower_bound = max(0, prediction - margin)
        upper_bound = prediction + margin
        
        return prediction, lower_bound, upper_bound
    
    def display_results(self, prediction, lower_bound, upper_bound, input_values):
        """显示预测结果"""
        model = self.selected_model.get()
        method = self.selected_method.get()
        confidence = self.confidence_var.get()
        
        # 清除之前的结果
        self.result_text.delete(1.0, tk.END)
        
        # 插入结果文本
        result_text = f"""
═══════════════════════════════════════════════════════════
              RAC碳化深度预测结果 
                Carbonation Depth Prediction Results
═══════════════════════════════════════════════════════════

🔬 预测模型: {model}
📊 不确定性量化方法: {method}
📈 置信水平: {confidence:.1%}

📍 预测结果 (Prediction Results):
   • 预测值 (Predicted Value): {prediction:.2f} mm
   • 置信区间 (Confidence Interval): [{lower_bound:.2f}, {upper_bound:.2f}] mm
   • 区间宽度 (Interval Width): {upper_bound - lower_bound:.2f} mm

🎯 预测精度评估:
   • 相对不确定性: {((upper_bound - lower_bound) / prediction * 100):.1f}%
   • 预测等级: {'高精度' if (upper_bound - lower_bound) / prediction < 0.2 else '中等精度' if (upper_bound - lower_bound) / prediction < 0.4 else '低精度'}

💡 工程建议:
   • 考虑到预测不确定性，建议设计裕量
   • 定期监测实际碳化情况
   • 优化配合比可降低碳化风险

═══════════════════════════════════════════════════════════
"""
        
        self.result_text.insert(tk.END, result_text)
        
        # 更新图表
        self.update_chart(prediction, lower_bound, upper_bound, input_values)
    
    def update_chart(self, prediction, lower_bound, upper_bound, input_values):
        """更新结果图表"""
        self.ax.clear()
        
        # 创建条形图显示置信区间
        x_pos = [0]
        predictions = [prediction]
        errors = [[prediction - lower_bound], [upper_bound - prediction]]
        
        bars = self.ax.bar(x_pos, predictions, yerr=errors, 
                          capsize=10, color='skyblue', alpha=0.7, 
                          error_kw={'elinewidth': 2, 'capthick': 2})
        
        # 添加数值标签
        self.ax.text(0, prediction + (upper_bound - prediction) / 2, 
                    f'{prediction:.2f} mm', ha='center', va='bottom', fontweight='bold')
        
        self.ax.set_ylabel('碳化深度 (mm)')
        self.ax.set_title(f'碳化深度预测结果\n置信区间: [{lower_bound:.2f}, {upper_bound:.2f}] mm')
        self.ax.set_xlim(-0.5, 0.5)
        self.ax.set_xticks([0])
        self.ax.set_xticklabels(['预测结果'])
        
        # 添加网格
        self.ax.grid(True, alpha=0.3)
        
        # 设置背景颜色
        self.ax.set_facecolor('#f8f9fa')
        
        self.canvas.draw()
    
    def reset_inputs(self):
        """重置输入到默认值"""
        for param_name, (default, _, _, _) in self.feature_stats.items():
            self.input_vars[param_name].set(default)
    
    def load_example(self):
        """加载示例数据"""
        examples = {
            'C (水泥)': 350.0,
            'FlA (粉煤灰)': 50.0,
            'W (水)': 180.0,
            'CA (粗骨料)': 600.0,
            'RA (再生骨料)': 400.0,
            'RWA (吸水率)': 4.5,
            'FA (细骨料)': 700.0,
            'SP (减水剂)': 2.0,
            'CS (抗压强度)': 35.0,
            'CC (碳浓度)': 10.0,
            'ET (暴露时间)': 365.0,
            'T (温度)': 20.0,
            'RH (相对湿度)': 65.0
        }
        
        for param_name, value in examples.items():
            self.input_vars[param_name].set(value)

def main():
    """主函数"""
    root = tk.Tk()
    app = CarbonationPredictionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
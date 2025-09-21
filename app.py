#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DRG分组器Web应用
提供Web界面用于输入诊断信息并进行DRG分组
"""

from flask import Flask, render_template, request, jsonify
import json
import traceback
from drg_group.beijing_2022.GroupProxy import GroupProxy
from drg_group.beijing_2022.Base import MedicalRecord

app = Flask(__name__)

# 初始化分组器
grouper = GroupProxy()

# 获取所有可用的DRG版本
DRG_VERSIONS = [
    {'value': 'beijing_2022', 'label': '北京2022版'},
    {'value': 'chs_drg_11', 'label': 'CHS-DRG 1.1标准版'},
    {'value': 'chs_drg_10', 'label': 'CHS-DRG 1.0修订版'},
    {'value': 'shanghai_2022', 'label': '上海2022版'},
    {'value': 'guangzhou_2022', 'label': '广州2022版'},
    {'value': 'wuhan_2022', 'label': '武汉2022版'},
]

# 离院方式选项
LEAVING_TYPE_OPTIONS = [
    {'value': 1, 'label': '医嘱离院'},
    {'value': 2, 'label': '医嘱转院'},
    {'value': 3, 'label': '医嘱转社区卫生服务机构/乡镇卫生院'},
    {'value': 4, 'label': '非医嘱离院'},
    {'value': 5, 'label': '死亡'},
    {'value': 9, 'label': '其他'},
]

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html', 
                         drg_versions=DRG_VERSIONS,
                         leaving_types=LEAVING_TYPE_OPTIONS)

@app.route('/api/group', methods=['POST'])
def api_group():
    """DRG分组API接口"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['index', 'gender', 'age', 'inHospitalTime', 'leavingType', 'zdList']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'缺少必填字段: {field}'
                }), 400
        
        # 构建记录字符串
        record_parts = [
            str(data.get('index', '')),
            str(data.get('gender', '')),
            str(data.get('age', '')),
            str(data.get('ageDay', '')),
            str(data.get('weight', '')),
            str(data.get('dept', '')),
            str(data.get('inHospitalTime', '')),
            str(data.get('leavingType', '')),
            data.get('zdList', ''),
            data.get('ssList', '')
        ]
        
        record_str = ','.join(record_parts)
        
        # 执行DRG分组
        result = grouper.group_record(record_str)
        
        # 转换结果为字典格式
        result_dict = {
            'success': True,
            'data': {
                'index': result.Index,
                'status': result.status,
                'mdc': result.mdc,
                'adrg': result.adrg,
                'drg': result.drg,
                'messages': result.messages
            }
        }
        
        return jsonify(result_dict)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'分组处理失败: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/versions')
def api_versions():
    """获取可用的DRG版本列表"""
    return jsonify({
        'success': True,
        'data': DRG_VERSIONS
    })

@app.route('/api/leaving-types')
def api_leaving_types():
    """获取离院方式选项"""
    return jsonify({
        'success': True,
        'data': LEAVING_TYPE_OPTIONS
    })

@app.route('/api/validate', methods=['POST'])
def api_validate():
    """验证输入数据"""
    try:
        data = request.get_json()
        errors = []
        
        # 性别验证
        gender = data.get('gender')
        if not gender or gender not in [1, 2, '1', '2']:
            errors.append('性别必须为1(男)或2(女)')
        
        # 年龄验证
        age = data.get('age')
        if age is None or age == '':
            errors.append('年龄不能为空')
        else:
            try:
                age = int(age)
                if age < 0 or age > 150:
                    errors.append('年龄必须在0-150之间')
                
                # 新生儿特殊验证
                if age == 0:
                    age_day = data.get('ageDay')
                    if not age_day:
                        errors.append('年龄为0时，年龄天数必须有值')
                    elif int(age_day) <= 28:
                        weight = data.get('weight')
                        if not weight:
                            errors.append('28天内新生儿的出生体重必须有值')
            except ValueError:
                errors.append('年龄必须为数字')
        
        # 住院天数验证
        hospital_time = data.get('inHospitalTime')
        if not hospital_time:
            errors.append('住院天数不能为空')
        else:
            try:
                hospital_time = int(hospital_time)
                if hospital_time <= 0:
                    errors.append('住院天数必须大于0')
            except ValueError:
                errors.append('住院天数必须为数字')
        
        # 诊断列表验证
        zd_list = data.get('zdList', '').strip()
        if not zd_list:
            errors.append('诊断列表不能为空')
        
        return jsonify({
            'success': True,
            'valid': len(errors) == 0,
            'errors': errors
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'验证失败: {str(e)}'
        }), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))  # 默认使用8080端口
    print("启动DRG分组器Web应用...")
    print(f"访问地址: http://localhost:{port}")
    print("使用Ctrl+C停止服务")
    app.run(debug=True, host='0.0.0.0', port=port)

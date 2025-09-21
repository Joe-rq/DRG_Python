#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DRG Web应用测试脚本
"""

import sys
import json
from app import app

def test_drg_grouping():
    """测试DRG分组功能"""
    print("🧪 测试DRG分组功能...")
    
    with app.test_client() as client:
        # 测试主页面
        print("📄 测试主页面...")
        response = client.get('/')
        if response.status_code == 200:
            print("✅ 主页面加载成功")
        else:
            print(f"❌ 主页面加载失败: {response.status_code}")
            return False
        
        # 测试API接口
        print("🔌 测试API接口...")
        test_data = {
            'index': '22058878',
            'gender': '2',
            'age': '88',
            'ageDay': '32460',
            'weight': '',
            'dept': '13040503',
            'inHospitalTime': '94',
            'leavingType': '1',
            'zdList': 'K22.301|K11.901|E11.900|I10.x05',
            'ssList': '96.0800x005'
        }
        
        response = client.post('/api/group', 
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        if response.status_code == 200:
            result = response.get_json()
            if result.get('success'):
                data = result['data']
                print("✅ DRG分组成功")
                print(f"   病案号: {data['index']}")
                print(f"   分组状态: {data['status']}")
                print(f"   MDC: {data['mdc']}")
                print(f"   ADRG: {data['adrg']}")
                print(f"   DRG: {data['drg']}")
                print(f"   消息数量: {len(data.get('messages', []))}")
                return True
            else:
                print(f"❌ DRG分组失败: {result.get('error', '未知错误')}")
                return False
        else:
            print(f"❌ API调用失败: {response.status_code}")
            return False

def test_validation():
    """测试数据验证功能"""
    print("\n🔍 测试数据验证功能...")
    
    with app.test_client() as client:
        # 测试无效数据
        invalid_data = {
            'index': '',  # 空病案号
            'gender': '3',  # 无效性别
            'age': '-1',  # 无效年龄
            'inHospitalTime': '0',  # 无效住院天数
            'leavingType': '',  # 空离院方式
            'zdList': ''  # 空诊断列表
        }
        
        response = client.post('/api/validate',
                              data=json.dumps(invalid_data),
                              content_type='application/json')
        
        if response.status_code == 200:
            result = response.get_json()
            if result.get('success') and not result.get('valid'):
                errors = result.get('errors', [])
                print(f"✅ 验证功能正常，发现 {len(errors)} 个错误")
                for error in errors[:3]:  # 只显示前3个错误
                    print(f"   - {error}")
                return True
            else:
                print("❌ 验证功能异常")
                return False
        else:
            print(f"❌ 验证API调用失败: {response.status_code}")
            return False

def main():
    """主测试函数"""
    print("🏥 DRG Web应用测试")
    print("=" * 40)
    
    try:
        # 测试基本功能
        success1 = test_drg_grouping()
        success2 = test_validation()
        
        print("\n" + "=" * 40)
        if success1 and success2:
            print("🎉 所有测试通过！Web应用运行正常")
            print("\n📖 使用说明:")
            print("1. 运行 './start_web.sh' (Linux/Mac) 或 'start_web.cmd' (Windows)")
            print("2. 在浏览器中访问 http://localhost:5000")
            print("3. 填写患者信息并进行DRG分组")
            return 0
        else:
            print("❌ 部分测试失败，请检查配置")
            return 1
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())

# DRG分组器项目说明文档 - HIS实施工程师指南

## 📋 项目概述

### 什么是OpenDRG？
OpenDRG是国家医保局CHS-DRG的开源Python实现，就像OpenJDK是Java SE的开源实现一样。本项目为医院信息系统（HIS）提供标准化的DRG分组功能，支持多个地区版本的分组方案。

### 核心功能
- **DRG分组计算**：根据患者的诊断、手术、年龄、性别等信息，自动计算DRG分组结果
- **多版本支持**：支持全国30多个地区的DRG分组方案
- **标准化接口**：提供统一的API接口，便于HIS系统集成
- **详细分组过程**：返回完整的分组步骤和规则匹配信息

## 🗂️ 项目结构说明

```
DRG_Python/
├── drg_group/                  # 分组器核心模块
│   ├── beijing_2022/          # 北京2022版分组器
│   ├── chs_drg_11/            # CHS-DRG 1.1标准版
│   ├── chs_drg_10/            # CHS-DRG 1.0修订版
│   └── [其他地区版本]/         # 30多个地区版本
├── input.txt                   # 测试输入文件
├── output.txt                  # 测试输出文件
├── run.cmd                     # Windows测试脚本
└── README.md                   # 项目说明
```

### 每个版本的内部结构
```
beijing_2022/
├── Base.py                     # 基础类和数据结构
├── Grouper.py                  # 主分组逻辑
├── Grouper_beijing_2022.py     # 版本特定的分组器
├── GroupProxy.py               # 外部调用接口
├── GroupTest.py                # 测试入口
├── MDC/                        # 主要诊断大类（26个MDC）
├── ADRG/                       # 核心DRG组（300+个ADRG）
├── DRG/                        # 最终DRG组细分逻辑
├── DATA/                       # 分组数据文件
│   ├── MCC.dat                 # 严重并发症或合并症
│   ├── CC.dat                  # 并发症或合并症
│   ├── CCE.dat                 # 排除表
│   ├── SS_VALID.dat            # 有效手术操作
│   └── DRG.dat                 # DRG组名称对照
└── ICD/                        # ICD编码映射文件
    ├── ZD_INFO.dat             # 诊断信息
    ├── SS_INFO.dat             # 手术信息
    ├── ZD_MAP.dat              # 诊断编码映射
    └── SS_MAP.dat              # 手术编码映射
```

## 🔄 DRG分组流程

### 1. 数据输入
患者病案需要包含以下信息：
- **Index**: 病案号（唯一标识）
- **gender**: 性别（1=男，2=女）
- **age**: 年龄
- **ageDay**: 年龄天数（新生儿必填）
- **weight**: 出生体重（28天内新生儿必填）
- **dept**: 科室代码
- **inHospitalTime**: 住院天数
- **leavingType**: 离院方式（1=医嘱离院，2=医嘱转院，3=医嘱转社区卫生服务机构/乡镇卫生院，4=非医嘱离院，5=死亡，9=其他）
- **zdList**: 诊断列表（ICD-10编码，多个用|分隔）
- **ssList**: 手术操作列表（ICD-9-CM-3编码，多个用|分隔）

### 2. 分组步骤
1. **数据校验**：检查必填字段和数据格式
2. **编码转换**：将输入的ICD编码转换为分组器支持的标准编码
3. **MDC分组**：根据主诊断确定主要诊断大类（A-Z共26个）
4. **ADRG分组**：在MDC内根据诊断和手术确定核心DRG组
5. **DRG细分**：根据并发症/合并症（CC/MCC）确定最终DRG组

### 3. 输出结果
```python
GroupResult(
    Index='22058878',           # 病案号
    status='分组成功',           # 分组状态
    messages=[...],             # 分组过程详细信息
    mdc='MDCG',                 # 主要诊断大类
    adrg='GZ1',                 # 核心DRG组
    drg='GZ13'                  # 最终DRG组
)
```

## 🔧 HIS系统集成方案

### 方案一：Python模块直接调用（推荐）
```python
from drg_group.beijing_2022.GroupProxy import GroupProxy

# 初始化分组器
grouper = GroupProxy()

# 单条病案分组
record_str = "22058878,2,88,32460,,13040503,94,1,K22.301|K11.901|E11.900|I10.x05,96.0800x005"
result = grouper.group_record(record_str)
print(result)
```

### 方案二：命令行调用
```bash
# 单条记录分组
python -m drg_group.beijing_2022.GroupTest "病案数据字符串"

# 批量文件分组（读取input.txt，输出到output.txt）
python -m drg_group.beijing_2022.GroupTest

# CSV文件分组
python -m drg_group.beijing_2022.GroupTest input.csv "列名列表"
```

### 方案三：Web服务封装
可以将分组器封装为Web API服务：
```python
from flask import Flask, request, jsonify
from drg_group.beijing_2022.GroupProxy import GroupProxy

app = Flask(__name__)
grouper = GroupProxy()

@app.route('/drg/group', methods=['POST'])
def group_drg():
    data = request.json
    record_str = f"{data['index']},{data['gender']},{data['age']},..."
    result = grouper.group_record(record_str)
    return jsonify(result._asdict())
```

## 📊 数据格式说明

### 输入数据格式
```
Index,gender,age,ageDay,weight,dept,inHospitalTime,leavingType,zdList,ssList
22058878,2,88,32460,,13040503,94,1,K22.301|K11.901|E11.900|I10.x05,96.0800x005
```

### 字段说明
| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| Index | 字符串 | 是 | 病案唯一标识 | 22058878 |
| gender | 整数 | 是 | 性别：1=男，2=女 | 2 |
| age | 整数 | 是 | 年龄 | 88 |
| ageDay | 整数 | 条件 | 年龄天数（年龄=0时必填） | 32460 |
| weight | 整数 | 条件 | 出生体重（28天内新生儿必填） | 3200 |
| dept | 字符串 | 否 | 科室代码 | 13040503 |
| inHospitalTime | 整数 | 是 | 住院天数 | 94 |
| leavingType | 整数 | 是 | 离院方式 | 1 |
| zdList | 字符串 | 是 | 诊断列表（\|分隔） | K22.301\|K11.901 |
| ssList | 字符串 | 否 | 手术列表（\|分隔） | 96.0800x005 |

### 输出结果说明
| 字段 | 说明 | 示例 |
|------|------|------|
| Index | 原病案号 | 22058878 |
| status | 分组状态 | 分组成功/无法入组/歧义病案 |
| messages | 分组过程 | [诊断解释, 分组步骤, 规则匹配...] |
| mdc | 主要诊断大类 | MDCG（消化系统疾病） |
| adrg | 核心DRG组 | GZ1 |
| drg | 最终DRG组 | GZ13（伴并发症或合并症） |

## 🏥 常见分组结果解释

### MDC分类（主要诊断大类）
- **MDCA**: 神经系统疾病
- **MDCB**: 眼部疾病  
- **MDCC**: 耳鼻咽喉口腔疾病
- **MDCD**: 呼吸系统疾病
- **MDCE**: 循环系统疾病
- **MDCF**: 消化系统疾病
- **MDCG**: 肝胆胰疾病
- **MDCH**: 肌肉骨骼系统疾病
- **MDCI**: 皮肤皮下组织疾病
- **MDCJ**: 内分泌营养代谢疾病
- **MDCK**: 肾脏泌尿系统疾病
- **MDCL**: 男性生殖系统疾病
- **MDCM**: 女性生殖系统疾病
- **MDCN**: 妊娠分娩产褥期
- **MDCO**: 新生儿疾病及先天性畸形
- **MDCP**: 血液造血器官疾病
- **MDCQ**: 淋巴造血系统肿瘤
- **MDCR**: 感染性疾病
- **MDCS**: 精神疾病
- **MDCT**: 酒精药物中毒
- **MDCU**: 损伤中毒外因
- **MDCV**: 烧伤
- **MDCW**: 影响健康状态因素
- **MDCX**: 放射治疗
- **MDCY**: 化学治疗  
- **MDCZ**: 多发外伤

### DRG组编号规则
- **第1位**：MDC字母（A-Z）
- **第2-3位**：ADRG组号（A1-Z9）
- **第4位**：严重程度
  - **1**: 伴严重并发症或合并症（MCC）
  - **3**: 伴并发症或合并症（CC）
  - **5**: 不伴并发症或合并症
  - **9**: 特殊情况

## ⚠️ 常见问题和注意事项

### 1. 编码问题
- **诊断编码**：必须使用ICD-10标准编码
- **手术编码**：必须使用ICD-9-CM-3标准编码
- **编码版本**：不同地区版本支持的编码可能略有差异

### 2. 数据质量要求
- **主诊断**：必须准确，直接影响MDC分组
- **并发症诊断**：影响最终DRG的严重程度分级
- **手术操作**：影响ADRG分组结果
- **年龄性别**：部分诊断有性别和年龄限制

### 3. 分组失败原因
- **编码无效**：使用了分组器不支持的ICD编码
- **数据不完整**：缺少必填字段
- **逻辑错误**：诊断与性别年龄不符
- **无匹配规则**：罕见疾病可能无法分组

### 4. 性能考虑
- **单条分组**：通常在1-5毫秒内完成
- **批量分组**：建议分批处理，避免内存溢出
- **多线程**：分组器是线程安全的，可以并行处理

## 🚀 快速开始测试

### 1. 环境准备
```bash
# 确保Python 3.6+环境
python --version

# 进入项目目录
cd DRG_Python
```

### 2. 快速测试
```bash
# Windows环境
run.cmd

# Linux/Mac环境
python -m drg_group.beijing_2022.GroupTest
```

### 3. 预期输出
```
GroupResult(Index='22058878', status='分组成功', messages=[...], mdc='MDCG', adrg='GZ1', drg='GZ13')
```

## 🔗 HIS系统集成详细指南

### 集成架构建议

#### 方案1：内嵌式集成（推荐）
```
HIS系统 → Python DRG模块 → 返回分组结果
```
**优点**：响应快、无网络依赖、数据安全
**适用**：单机版HIS或私有云部署

#### 方案2：服务化集成
```
HIS系统 → HTTP API → DRG服务 → 返回JSON结果
```
**优点**：解耦合、易维护、可扩展
**适用**：分布式HIS或多医院集团

#### 方案3：数据库集成
```
HIS系统 → 数据表 → 定时批处理 → 写回结果表
```
**优点**：异步处理、批量高效
**适用**：历史数据批量分组

### 数据库设计建议

#### 输入表结构（drg_input）
```sql
CREATE TABLE drg_input (
    id VARCHAR(50) PRIMARY KEY,           -- 病案号
    patient_gender TINYINT,               -- 性别：1男2女
    patient_age INT,                      -- 年龄
    age_days INT,                         -- 年龄天数
    birth_weight INT,                     -- 出生体重(克)
    dept_code VARCHAR(20),                -- 科室代码
    hospital_days INT,                    -- 住院天数
    leaving_type TINYINT,                 -- 离院方式
    diagnosis_codes TEXT,                 -- 诊断编码(|分隔)
    surgery_codes TEXT,                   -- 手术编码(|分隔)
    created_time TIMESTAMP DEFAULT NOW(), -- 创建时间
    status TINYINT DEFAULT 0              -- 处理状态：0待处理1已处理
);
```

#### 输出表结构（drg_result）
```sql
CREATE TABLE drg_result (
    id VARCHAR(50) PRIMARY KEY,           -- 病案号
    group_status VARCHAR(20),             -- 分组状态
    mdc_code VARCHAR(10),                 -- MDC代码
    adrg_code VARCHAR(10),                -- ADRG代码
    drg_code VARCHAR(10),                 -- DRG代码
    drg_name VARCHAR(200),                -- DRG名称
    group_messages TEXT,                  -- 分组过程
    process_time TIMESTAMP DEFAULT NOW(), -- 处理时间
    version VARCHAR(20)                   -- 分组器版本
);
```

### Java集成示例（Spring Boot）

#### 1. Python进程调用
```java
@Service
public class DrgGroupService {
    
    @Value("${drg.python.path}")
    private String pythonPath;
    
    @Value("${drg.version}")
    private String drgVersion = "beijing_2022";
    
    public DrgResult groupRecord(DrgInput input) {
        try {
            String command = String.format(
                "%s -m drg_group.%s.GroupTest \"%s\"",
                pythonPath, drgVersion, input.toRecordString()
            );
            
            Process process = Runtime.getRuntime().exec(command);
            BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream(), "UTF-8")
            );
            
            String result = reader.readLine();
            return parseResult(result);
            
        } catch (Exception e) {
            throw new RuntimeException("DRG分组失败", e);
        }
    }
}
```

#### 2. HTTP API调用
```java
@Service
public class DrgApiService {
    
    @Autowired
    private RestTemplate restTemplate;
    
    @Value("${drg.api.url}")
    private String drgApiUrl;
    
    public DrgResult groupRecord(DrgInput input) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<DrgInput> request = new HttpEntity<>(input, headers);
            
            ResponseEntity<DrgResult> response = restTemplate.postForEntity(
                drgApiUrl + "/group", request, DrgResult.class
            );
            
            return response.getBody();
            
        } catch (Exception e) {
            throw new RuntimeException("DRG API调用失败", e);
        }
    }
}
```

### .NET集成示例

#### Python.NET集成
```csharp
public class DrgGroupService
{
    private dynamic groupProxy;
    
    public DrgGroupService()
    {
        // 初始化Python环境
        PythonEngine.Initialize();
        using (Py.GIL())
        {
            dynamic sys = Py.Import("sys");
            sys.path.append(@"C:\DRG_Python");
            
            dynamic module = Py.Import("drg_group.beijing_2022.GroupProxy");
            groupProxy = module.GroupProxy();
        }
    }
    
    public DrgResult GroupRecord(DrgInput input)
    {
        using (Py.GIL())
        {
            string recordStr = input.ToRecordString();
            dynamic result = groupProxy.group_record(recordStr);
            
            return new DrgResult
            {
                Index = result.Index.ToString(),
                Status = result.status.ToString(),
                Mdc = result.mdc.ToString(),
                Adrg = result.adrg.ToString(),
                Drg = result.drg.ToString(),
                Messages = result.messages.ToString()
            };
        }
    }
}
```

### PHP集成示例

```php
class DrgGroupService 
{
    private $pythonPath;
    private $drgVersion;
    
    public function __construct($pythonPath = 'python', $version = 'beijing_2022') 
    {
        $this->pythonPath = $pythonPath;
        $this->drgVersion = $version;
    }
    
    public function groupRecord($input) 
    {
        $recordStr = $this->buildRecordString($input);
        $command = sprintf(
            '%s -m drg_group.%s.GroupTest "%s"',
            $this->pythonPath,
            $this->drgVersion,
            $recordStr
        );
        
        $output = shell_exec($command);
        return $this->parseResult($output);
    }
    
    private function buildRecordString($input) 
    {
        return implode(',', [
            $input['index'],
            $input['gender'],
            $input['age'],
            $input['ageDay'] ?? '',
            $input['weight'] ?? '',
            $input['dept'] ?? '',
            $input['hospitalTime'],
            $input['leavingType'],
            implode('|', $input['diagnosis']),
            implode('|', $input['surgery'] ?? [])
        ]);
    }
}
```

### 错误处理和日志

#### 分组状态码说明
```python
# 成功状态
'分组成功'           # 正常分组完成
'歧义病案'           # 存在分组歧义，需人工审核

# 失败状态  
'无法入组'           # 不符合任何分组条件
'信息校验不通过'      # 输入数据格式错误
'诊断不能转换'       # ICD编码不支持
'手术操作不能转换'    # 手术编码不支持
'诊断与性别不符'      # 诊断与患者性别冲突
```

#### 日志记录建议
```java
@Slf4j
@Component
public class DrgLogService {
    
    public void logDrgProcess(String caseId, DrgInput input, DrgResult result, long costTime) {
        log.info("DRG分组完成 - 病案号:{}, 状态:{}, MDC:{}, DRG:{}, 耗时:{}ms", 
                caseId, result.getStatus(), result.getMdc(), result.getDrg(), costTime);
        
        if (!"分组成功".equals(result.getStatus())) {
            log.warn("DRG分组异常 - 病案号:{}, 状态:{}, 错误信息:{}", 
                    caseId, result.getStatus(), String.join(";", result.getMessages()));
        }
    }
}
```

### 性能优化建议

#### 1. 连接池管理
```java
@Configuration
public class DrgConfig {
    
    @Bean
    public ExecutorService drgExecutor() {
        return Executors.newFixedThreadPool(10); // 根据并发量调整
    }
}
```

#### 2. 缓存策略
```java
@Service
public class DrgCacheService {
    
    @Cacheable(value = "drgResult", key = "#input.hashCode()")
    public DrgResult groupWithCache(DrgInput input) {
        return drgGroupService.groupRecord(input);
    }
}
```

#### 3. 批量处理
```java
@Service
public class DrgBatchService {
    
    public List<DrgResult> batchGroup(List<DrgInput> inputs) {
        return inputs.parallelStream()
                .map(drgGroupService::groupRecord)
                .collect(Collectors.toList());
    }
}
```

### 部署和运维

#### Docker部署示例
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY DRG_Python/ /app/

# 安装依赖
RUN pip install -r requirements.txt

# 暴露API端口
EXPOSE 8080

# 启动服务
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8080"]
```

#### 监控指标
- **响应时间**：单次分组耗时
- **成功率**：分组成功的比例
- **错误分布**：各类错误的统计
- **并发量**：同时处理的请求数

## 📞 技术支持

### 联系方式
- **邮箱**：OpenDRG@hotmail.com
- **项目地址**：根据实际情况填写

### 常用版本选择指南
| 地区 | 推荐版本 | 特点 |
|------|----------|------|
| 全国通用 | chs_drg_11 | 国家标准1.1版 |
| 北京 | beijing_2022 | 北京地方版 |
| 上海 | 待更新 | - |
| 其他地区 | 参考README | 选择对应地区版本 |

### 实施检查清单
- [ ] 确认使用的DRG版本
- [ ] 验证ICD编码映射
- [ ] 测试数据格式转换
- [ ] 性能压力测试
- [ ] 错误处理机制
- [ ] 日志监控配置
- [ ] 数据备份策略

## 📝 更新日志

### 版本特性
- **多地区支持**：已支持30+个地区版本
- **标准化接口**：统一的API调用方式
- **详细日志**：完整的分组过程记录
- **高性能**：单条分组毫秒级响应

---

*本文档专为HIS厂家实施工程师编写，如有疑问请联系技术支持团队。*

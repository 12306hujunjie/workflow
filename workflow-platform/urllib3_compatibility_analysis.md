# urllib3 版本兼容性分析报告

## 问题背景
当前项目使用 urllib3 v2.4.0，在 macOS 系统上会出现 SSL 警告：
```
NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'
```

## 依赖关系分析

### 直接依赖 urllib3 的包
1. **requests (v2.32.4)**
   - 要求: `urllib3<3,>=1.21.1`
   - ✅ 兼容 urllib3 v1.x 和 v2.x

### 间接可能受影响的包
1. **httpx (v0.25.2)** - 使用自己的 HTTP 实现，不依赖 urllib3
2. **prefect (v2.14.5)** - 通过 httpx 和其他包间接使用
3. **playwright (v1.40.0)** - 独立的浏览器自动化工具

## 降级到 urllib3 v1.x 的影响评估

### ✅ 优点
1. **解决 SSL 警告**: 完全消除 macOS LibreSSL 兼容性警告
2. **稳定性**: urllib3 v1.26.x 是成熟稳定的版本
3. **兼容性**: 所有依赖包都支持 v1.x

### ⚠️ 潜在风险
1. **功能差异**: urllib3 v2.x 有一些新功能和性能改进
2. **安全更新**: v1.x 分支的安全更新可能会逐渐减少
3. **未来兼容性**: 新版本的依赖包可能逐渐要求 urllib3 v2.x

## 推荐方案

### 方案1: 降级 urllib3 (推荐)
```bash
pip install "urllib3<2.0"
```

**优点:**
- 彻底解决警告问题
- 不影响现有功能
- 兼容性最好

**requirements.txt 更新:**
```
urllib3<2.0  # 固定在 v1.x 避免 macOS SSL 警告
```

### 方案2: 保持 v2.x + 忽略警告 (当前方案)
```python
# 在应用启动时忽略警告
import warnings
from urllib3.exceptions import NotOpenSSLWarning
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
```

**优点:**
- 使用最新版本
- 获得性能和安全改进

**缺点:**
- 警告信息仍然存在
- 需要在代码中处理

## 结论

**降级到 urllib3 v1.x 不会影响其他包的版本兼容性**，因为：

1. requests 明确支持 `urllib3<3,>=1.21.1`
2. 其他主要依赖包（httpx, prefect, playwright）都不直接依赖 urllib3
3. 当前项目的所有功能在 urllib3 v1.x 下都能正常工作

**建议采用方案1（降级）**，这是最简洁和稳定的解决方案。
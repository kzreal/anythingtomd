# Design Context

此文档由 teach-impeccable 技能生成，用于指导 AlltoMarkdown 项目的设计决策。

## Design Context

### Users
**目标用户**：开发者、文档工作者、内容创作者

**使用场景**：
- 需要将 Word/Excel 文档快速转换为 Markdown 格式
- 可能在工作时使用，需要高效完成转换任务
- 期望界面直观、操作简单

**核心任务**：上传文件 → 选择选项 → 转换 → 预览/下载

### Brand Personality
**三个词描述**：极简、清晰、克制

**情感目标**：
- 传递专业感和可靠性
- 让用户感到操作流畅、无障碍
- 通过简洁设计减少认知负担
- 营造干净、专注的阅读体验

**参考风格**：Notion - 干净、克制、以内容为中心的文档工具界面

### Aesthetic Direction
**视觉基调**：极简主义，追求清晰和功能性的平衡

**设计特征**：
- 清晰的排版和层级，易于阅读
- 柔和的阴影和边框，微妙地界定内容区域
- 浅灰色背景，减少视觉疲劳
- 大量留白，保持呼吸感和空间感
- 克制的色彩使用，避免过多装饰
- 适度使用渐变，营造精致感

**主题设置**：浅色模式（参考 Notion）

**色彩偏好**：
- 主色调：中性色系（白/灰/黑）为主，遵循 Notion 配色系统
- 强调色：单一、克制，仅用于关键交互（如按钮、状态指示）
- 避免：过度的渐变、过度装饰、花哨的动效

**字体偏好**：清晰、易读的系统字体

### Design Principles

1. **功能优先**
   - 每个视觉元素都服务于明确的用户任务
   - 避免纯装饰性元素干扰用户注意力

2. **清晰直观**
   - 使用高对比度和明确边界
   - 让用户一眼就能理解当前状态和可操作项

3. **克制优雅**
   - 保持简洁，不堆砌功能
   - 使用留白和呼吸感营造优雅氛围

4. **高效流畅**
   - 最少化用户操作步骤
   - 提供即时的反馈和状态提示

5. **一致性**
   - 统一的间距、圆角、字体大小
   - 相同功能使用相同的视觉表达方式

## Technical Design Specifications

### Color Palette
```css
/* 主色系 */
--text-primary: #1a1a1a;      /* 主要文字 */
--text-secondary: #666666;    /* 次要文字 */
--text-tertiary: #999999;     /* 辅助文字 */

/* 背景色 */
--bg-primary: #ffffff;         /* 主背景 */
--bg-secondary: #f7f7f7;      /* 次要背景 */
--bg-tertiary: #e9e9e9;       /* 辅助背景 */

/* 强调色（单一、克制） */
--accent: #007aff;            /* 主要交互 */
--accent-hover: #0062cc;

/* 功能色 */
--success: #22c55e;           /* 成功 */
--error: #ef4444;             /* 错误 */
--warning: #f59e0b;           /* 警告 */
```

### Spacing Scale
```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
```

### Border Radius
```css
--radius-sm: 4px;
--radius-md: 6px;
--radius-lg: 8px;
--radius-full: 9999px;
```

### Typography
```css
--font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

--font-size-xs: 12px;
--font-size-sm: 14px;
--font-size-md: 16px;
--font-size-lg: 18px;
--font-size-xl: 24px;
--font-size-2xl: 32px;

--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;

--line-height-tight: 1.25;
--line-height-normal: 1.5;
--line-height-relaxed: 1.75;
```

### Component Guidelines

#### 按钮
- 主要按钮：纯色填充，圆角 6px
- 次要按钮：边框样式
- 悬停状态：轻微颜色加深
- 禁用状态：降低不透明度

#### 输入区域
- 边框 1px，颜色 `--bg-tertiary`
- 聚焦状态：边框颜色改为强调色
- 内边距：12px 16px

#### 卡片
- 背景：白色
- 边框：1px solid `--bg-tertiary`
- 圆角：8px
- 阴影：无或极轻微

#### 分隔线
- 颜色：`--bg-tertiary`
- 厚度：1px

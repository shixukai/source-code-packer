# 项目源码打包工具

该工具用于将指定项目目录中的源码文件打包成一个 `.tar.gz` 压缩包，并且支持根据配置文件和用户输入排除指定的子目录。

## 功能

1. 只打包指定后缀的源码文件，后缀列表通过 `config.json` 读取。
2. 保留项目的文件目录结构。
3. 支持排除指定的子目录，排除目录列表通过 `config.json` 读取和用户输入获取。
4. 以树形结构输出打包的文件列表。

## 配置文件

在脚本目录下创建 `config.json` 文件，示例如下：

```json
{
    "file_extensions": [".cpp", ".hpp", ".h", ".json"],
    "exclude_dirs": ["SLW-Sort_Lifter_Wheel/CANOpen", "src/commination"]
}
```

- `file_extensions`: 要打包的文件后缀列表。
- `exclude_dirs`: 需要排除的子目录列表。

## 使用方法

### 前提条件

确保已安装 Python 3。

### 步骤

1. 将项目克隆到本地：

    ```sh
    git clone <repository_url>
    cd <repository_directory>
    ```

2. 创建并配置 `config.json` 文件，参考上面的示例配置文件。

3. 运行脚本：

    ```sh
    python3 main.py
    ```

4. 按提示输入项目路径和需要排除的子目录：

    ```
    输入项目路径: /path/to/your/project
    输入需要排除的子目录 (相对路径), 完成输入 'done': subdir1
    输入需要排除的子目录 (相对路径), 完成输入 'done': subdir2
    输入需要排除的子目录 (相对路径), 完成输入 'done': done
    ```

### 输出结果

- 压缩包会创建在 `/tmp` 目录下，命名为项目的名称，例如：`/tmp/your_project.tar.gz`。
- 脚本会以树形结构输出打包的文件列表。

## 注意事项

- `config.json` 文件需要与 `main.py` 脚本放置在同一目录下。
- 用户输入的排除目录路径为相对路径，相对于项目根目录。
- 排除目录列表为配置文件和用户输入的并集，去重后生效。

## 支持

如有问题，请联系项目维护者。

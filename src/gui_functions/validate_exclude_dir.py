import os
class InvalidSubdirectoryException(Exception):
    pass

def validate_exclude_dir(exclude_dir, project_path):
    """
    验证排除目录是否是有效的子目录。
    如果无效，抛出 InvalidSubdirectoryException 异常。
    """
    full_path = os.path.join(project_path, exclude_dir)

    if not (os.path.isdir(full_path) and full_path.startswith(project_path)):
        raise InvalidSubdirectoryException(f"排除的目录 '{exclude_dir}' 无效: {full_path}")
    return True

"""General function"""

def escape_text(text):
    """Escape text"""
    return text \
        .replace("_", "\\_") \
        .replace("*", "\\*") \
        .replace("[", "\\[") \
        .replace("`", "\\`")

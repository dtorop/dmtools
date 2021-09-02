def log_msg(name: str, time: float, size: int) -> str:
    """Return log message for creation of file.

    Args:
        name (str): Name of the created file.
        time (float): Amount of time it took to compile the file.
        size (int): Size of the created file.

    Returns:
        str: Log message with information about the created file.
    """
    i = 0
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    while size >= 1000:
        size = round(size / 1000)
        i += 1
    size_str = '%d%s' % (size, units[i])
    return "%s | %.3fs | %s" % (name, time, size_str)

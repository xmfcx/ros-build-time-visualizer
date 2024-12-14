def seconds_to_minutes_seconds(seconds):
    from datetime import timedelta
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.total_seconds(), 3600)
    minutes, remaining_seconds = divmod(remainder, 60)

    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m {remaining_seconds:.2f}s"
    elif minutes > 0:
        return f"{int(minutes)}m {remaining_seconds:.2f}s"
    else:
        return f"{remaining_seconds:.2f}s"

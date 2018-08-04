def formated_date(obj):
    if not obj:
        return obj
    isoformat = obj.isoformat()
    return isoformat.split('+')[0]

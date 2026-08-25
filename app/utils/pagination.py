def paginate(query, skip=0, limit=20):
    return query.offset(skip).limit(limit).all(), query.count()

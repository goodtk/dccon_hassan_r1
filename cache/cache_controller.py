from .service import cache_add_service, cache_read_service, cache_clear_service

async def clear_cache(ctx):
    user_id = str(ctx.author.id)
    msg = cache_clear_service.clear_cache(user_id)
    await ctx.send(msg)

def add_cache(package_name, idx, file_name, bytes):
    cache_add_service.add_cache(package_name, idx, file_name, bytes)

def find_cache(package_name, idx):
    return cache_read_service.find_dccon(package_name, idx)
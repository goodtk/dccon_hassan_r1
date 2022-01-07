from .service import favorite_add_service, favorite_backup_service, favorite_read_service, favorite_delete_service, favorite_search_service

def add_favorite(ctx, shortcut_name, package_name, dccon_name):
    return favorite_add_service.add_favorite(ctx, shortcut_name, package_name, dccon_name)

def find_favorite_one(ctx, shortcut_name):
    return favorite_read_service.find_favorite_one(ctx, shortcut_name)

def show_favorites(ctx):
    return favorite_read_service.show_favorites(ctx)

def delete_favorite(ctx, shortcut_name):
    return favorite_delete_service.delete_favorite(ctx, shortcut_name)

def serach_favorites(ctx, keyword):
    return favorite_search_service.search_favorite(ctx, keyword)

def dump_favorites(ctx, user_id):
    return favorite_backup_service.dump_favorites(ctx, user_id)

def resotre_favorites(ctx, download_url):
    return favorite_backup_service.restore_favorites(ctx, download_url)

def reset_favorites(ctx):
    return favorite_delete_service.reset_favorites(ctx)
from .service import dccon_core_service
from send import sender

async def send_dccon(ctx, package_name, idx):
    await sender.reaction_by_slash(ctx)
    return await dccon_core_service.send_dccon(ctx, package_name, idx)

async def send_dccon_list(ctx, package_name):
    await sender.reaction_by_slash(ctx)
    return await dccon_core_service.send_dccon_list(ctx, package_name)
from django.contrib import admin
from manager.models import *

# Register your models here.

admin.site.register(UserPermissions)
admin.site.register(Address)
admin.site.register(Room)
admin.site.register(Institution)
admin.site.register(EntryGroup)
admin.site.register(Entry)
admin.site.register(InventoryOrder)
admin.site.register(InventoryRoomReport)
admin.site.register(InventoryEntryNote)
admin.site.register(Liquidation)
admin.site.register(LiquidationEntryNote)

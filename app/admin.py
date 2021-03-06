from django.contrib import admin
from .models import Item,OrderItem,Order,Address,Payment,Coupon,Refund,UserProfile



# Register your models here.

def make_refund_accepted(modeladmin,request,queryset):
    queryset.update(refund_requested=False,refund_granted=True)
    make_refund_accepted.short_description = "update orders to refund granted"

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user','ordered','being_delivered','recieved','refund_requested','refund_granted','billing_address','shipping_address','coupon','payment']

    list_filter = ['ordered','being_delivered','recieved','refund_requested','refund_granted']

    list_display_links = ['user','billing_address','shipping_address','coupon','payment']

    search_fields = ['user__username','ref_code']

    actions = [make_refund_accepted]

class AddressAdmin(admin.ModelAdmin):
    list_display = ['user','street_address','apartment_address','country','zip','address_type','default']
    list_filter = ['user','default','address_type','country']
    search_fields = ['user','street_address','apartment_address','zip']


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order,OrderAdmin)
admin.site.register(Address,AddressAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(UserProfile)

from django.contrib import admin
from rango.models import Category, Page, UserProfile

# Register your models here.

#class PageInline(admin.TabularInline):
#	model = Category

class PageInline(admin.TabularInline):
	model = Page
	extra = 0

class PageAdmin(admin.ModelAdmin):
	list_display = ('title', 'category', 'url')

class CategoryAdmin(admin.ModelAdmin):
	prepopulated_fields = {'slug':('name',)}
	inlines = [PageInline]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)
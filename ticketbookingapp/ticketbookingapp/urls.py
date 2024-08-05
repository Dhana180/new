# # """
# # URL configuration for ticketbookingapp project.

# # The `urlpatterns` list routes URLs to views. For more information please see:
# #     https://docs.djangoproject.com/en/5.0/topics/http/urls/
# # Examples:
# # Function views
# #     1. Add an import:  from my_app import views
# #     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# # Class-based views
# #     1. Add an import:  from other_app.views import Home
# #     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# # Including another URLconf
# #     1. Import the include() function: from django.urls import include, path
# #     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# # """
# # from django.contrib import admin
# # from django.urls import path

# # urlpatterns = [
# #     path('admin/', admin.site.urls),
# # ]






from django.contrib import admin
from django.urls import path
from home.views import *
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', home, name='home'),
    path('cart/', cart, name='cart'),
    path('remove_cart_item/<uuid:cart_item_uid>/', remove_cart_item, name='remove_cart'),  # Use <uuid:cart_item_uid>
    path('add_cart/<uuid:movie_uid>/', add_cart, name="add-cart"),  # Use <uuid:movie_uid>
    path('login/', login_page, name="login"),
    path('register/', register_page, name="register"),
    path("admin/", admin.site.urls),
    path('logout/', user_logout, name='logout'),
    path('create-order/', create_order, name='create_order'),  # Add create-order path
    path('verify-payment/', verify_payment, name='verify_payment'),  # Add verify-payment path
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()

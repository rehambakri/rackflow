from asgiref.sync import async_to_sync
from authentication.models import CustomUser
from channels.layers import get_channel_layer
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from notification.models import Notification

from .forms import ProductForm
from .models import Category, Product


class ProductList(ListView):
    model = Product
    template_name = "product/index.html"
    context_object_name = "products"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        # Get all filter parameters from request
        params = {
            "search": self.request.GET.get("search"),
            "category": self.request.GET.get("category"),
            "items": self.request.GET.get("items"),
        }
        # Apply search filter (name only as per your model)
        if params["search"]:
            queryset = queryset.filter(name__icontains=params["search"])

        # Apply category filter
        if params["category"]:
            queryset = queryset.filter(category__name=params["category"])
        # Update pagination size
        if params["items"] and params["items"].isdigit():
            self.paginate_by = int(params["items"])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add all categories to context
        context["categories"] = Category.objects.all().distinct()

        # Preserve current filter values
        context["current_filters"] = {
            "search_query": self.request.GET.get("search", ""),
            "category_query": self.request.GET.get("category", ""),
            "items_query": self.paginate_by,
        }

        return context


class ProductCreate(CreateView):
    form_class = ProductForm
    model = Product
    template_name = "product/create.html"
    context_object_name = "products"
    success_url = reverse_lazy("product:list")

    def form_valid(self, form):
        response = super().form_valid(form)

        # send websocket a message through channel layer
        # to notify them to start stream new data added to the database

        # get manager user
        manager = CustomUser.objects.filter(is_superuser=True).first()

        # save the notification of product creation in the database
        Notification(
            sender=self.request.user,
            receiver=manager,
            product=self.object,
            type="product_created",
        ).save()

        # notify all manager sockets to stream the latest added new notification record
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "manager_notification_channels",
            {
                "type": "notification.new",
                "receiver_id": manager.id,
            },
        )
        return response


class ProductUpdate(UpdateView):
    form_class = ProductForm
    model = Product
    template_name = "product/update.html"
    context_object_name = "products"
    success_url = reverse_lazy("product:list")


class ProductDetails(DetailView):
    model = Product
    template_name = "product/details.html"
    context_object_name = "product"
    success_url = reverse_lazy("product:details")
